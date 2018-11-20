"""A Scheme interpreter and its read-eval-print loop."""
from scheme_builtins import *
from scheme_reader import *

import src.datamodel as datamodel
import src.evaluate_apply as evaluate_apply
import src.parser as parser
import src.lexer as lexer
import src.environment as environment
import src.scheme_exceptions as scheme_exceptions
import src.gui as gui

from ucb import main


##############
# Eval/Apply #
##############

def scheme_eval(expr, env, _=None): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in environment ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """

    print(expr, file=sys.stderr)

    if env.real_env is None:
        env.real_env = environment.build_global_frame()
    gui.logger.new_query(True, True, True, strict_mode=True)
    try:
        expr = parser.get_expression(lexer.TokenBuffer([str(expr)]))
        out = evaluate_apply.evaluate(expr, env.real_env, gui.Holder(expr))
    except (ZeroDivisionError, scheme_exceptions.SchemeError) as e:
        print("; expect SchemeError", "\n", file=sys.stderr)
        raise SchemeError(e)
    print("; expect", out, "\n", file=sys.stderr)
    return out


class FakeProcedure(evaluate_apply.Callable):
    def __init__(self, proc):
        self.proc = proc

    def execute(self, operands, frame, _=None):
        real_operands = []
        for operand in operands:
            real_operands.append(parser.get_expression(lexer.TokenBuffer(str(operand))))
        return self.proc.apply(real_operands, frame)


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV."""
    return procedure.apply(args.map(lambda x: scheme_eval(x, env)), env)


################
# Environments #
################

class Frame:
    """An environment frame binds Scheme symbols to Scheme values."""

    def __init__(self, parent, real_env=None):
        """An empty frame with parent frame PARENT (which may be None)."""
        "Your Code Here"
        self.real_env = real_env

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

##############
# Procedures #
##############

class Procedure:
    """The supertype of all Scheme procedures."""

def scheme_procedurep(x):
    return isinstance(x, Procedure)

class BuiltinProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False, name='builtin'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4
        """
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        lst = []
        args.map(lst.append)
        for i, elem in enumerate(lst):
            if isinstance(elem, datamodel.ValueHolder):
                lst[i] = elem.value
        try:
            if self.use_env:
                return self.fn(*lst, env)
            else:
                return self.fn(*lst)
        except TypeError as e:
            raise SchemeError(e)
        # END PROBLEM 2

"""A procedure defined by a lambda expression or a define form."""

class LambdaProcedure(Procedure):

    def __init__(self, formals, body, env):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env

    def __str__(self):
        return str(Pair('lambda', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))

################
# Input/Output #
################

def read_eval_print_loop(next_line, env, interactive=False, quiet=False,
                         startup=False, load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None and result is not datamodel.Undefined:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in getattr(err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            print()
            return

def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into environment ENV,
    with verbosity determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    check_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)

    read_eval_print_loop(next_line, env, quiet=quiet)


def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))


def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    return Frame(None)

@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
    parser.add_argument('-load', '-i', action='store_true',
                       help='run file interactively')
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()

    next_line = buffer_input
    interactive = True
    load_files = []

    if args.file is not None:
        if args.load:
            load_files.append(getattr(args.file, 'name'))
        else:
            lines = args.file.readlines()
            def next_line():
                return buffer_lines(lines)
            interactive = False

    read_eval_print_loop(next_line, create_global_frame(), startup=True,
                         interactive=interactive, load_files=load_files)
    tscheme_exitonclick()
