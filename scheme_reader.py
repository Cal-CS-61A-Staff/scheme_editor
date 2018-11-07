"""This module implements the built-in data types of the Scheme language, along
with a parser for Scheme expressions.

In addition to the types defined in this file, some data types in Scheme are
represented by their corresponding type in Python:
    number:       int or float
    symbol:       string
    boolean:      bool
    unspecified:  None

The __repr__ method of a Scheme value will return a Python expression that
would be evaluated to the value, where possible.

The __str__ method of a Scheme value will return a Scheme expression that
would be read to the value, where possible.
"""
from typing import Union

import src.gui as gui
import src.scheme_exceptions as scheme_exceptions
import src.datamodel as datamodel
import src.lexer as lexer
import src.parser as parser

from ucb import main, trace, interact
from scheme_tokens import tokenize_lines, DELIMITERS
from buffer import Buffer, InputReader, LineReader


# Pairs and Scheme lists

class Pair:
    """A pair has two instance attributes: first and second.  For a Pair to be
    a well-formed list, second is either a well-formed list or nil.  Some
    methods only apply to well-formed lists.

    >>> s = Pair(1, Pair(2, nil))
    >>> s
    Pair(1, Pair(2, nil))
    >>> print(s)
    (1 2)
    >>> print(s.map(lambda x: x+4))
    (5 6)
    """

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __repr__(self):
        return 'Pair({0}, {1})'.format(repr(self.first), repr(self.second))

    def __str__(self):
        s = '(' + repl_str(self.first)
        second = self.second
        while isinstance(second, Pair):
            s += ' ' + repl_str(second.first)
            second = second.second
        if second is not nil and second is not datamodel.Nil:
            s += ' . ' + repl_str(second)
        return s + ')'

    def __len__(self):
        n, second = 1, self.second
        while isinstance(second, Pair):
            n += 1
            second = second.second
        if second is not nil:
            raise TypeError('length attempted on improper list')
        return n

    def __eq__(self, p):
        if not isinstance(p, Pair):
            return False
        return self.first == p.first and self.second == p.second

    def map(self, fn):
        """Return a Scheme list after mapping Python function FN to SELF."""
        mapped = fn(self.first)
        if self.second is nil or isinstance(self.second, Pair):
            return Pair(mapped, self.second.map(fn))
        else:
            raise TypeError('ill-formed list')


class nil:
    """The empty list"""

    def __repr__(self):
        return 'nil'

    def __str__(self):
        return '()'

    def __len__(self):
        return 0

    def map(self, fn):
        return self


nil = nil()  # Assignment hides the nil class; there is only one instance

# Scheme list parser

# Quotation markers
quotes = {"'": 'quote',
          '`': 'quasiquote',
          ',': 'unquote'}


class BuffWrapper(lexer.TokenBuffer):
    # noinspection PyMissingConstructor
    def __init__(self, buff: Buffer):
        self.src_buff = buff

        def get_next_token():
            out = buff.current()
            if out is None:
                raise SyntaxError("buffer exhausted")
            if out is True:
                return "#t"
            if out is False:
                return "#f"
            return out

        def pop_next_token():
            out = buff.remove_front()
            if out is None:
                raise SyntaxError("buffer exhausted")
            if out is True:
                return "#t"
            if out is False:
                return "#f"
            return out

        self.get_next_token = get_next_token
        self.pop_next_token = pop_next_token


def make_proj_pair(pair: datamodel.Expression) -> Union[datamodel.Expression, Pair]:
    if isinstance(pair, datamodel.Pair):
        return Pair(make_proj_pair(pair.first), make_proj_pair(pair.rest))
    elif isinstance(pair, datamodel.ValueHolder):
        return pair.value
    else:
        return pair


def scheme_read(src):
    """Read the next expression from SRC, a Buffer of tokens.

    >>> scheme_read(Buffer(tokenize_lines(['nil'])))
    nil
    >>> scheme_read(Buffer(tokenize_lines(['1'])))
    1
    >>> scheme_read(Buffer(tokenize_lines(['true'])))
    True
    >>> scheme_read(Buffer(tokenize_lines(['(+ 1 2)'])))
    Pair('+', Pair(1, Pair(2, nil)))
    """
    if src.current() is None:
        raise EOFError
    gui.logger.strict_mode = False
    # BEGIN PROBLEM 1/2
    "*** YOUR CODE HERE ***"
    try:
        token_buffer = BuffWrapper(src)
        scm_expr = parser.get_expression(token_buffer)
        return make_proj_pair(scm_expr)
    except scheme_exceptions.ParseError as e:
        raise SyntaxError(e)
    # END PROBLEM 1/2


def read_tail(src):
    """Return the remainder of a list in SRC, starting before an element or ).

    >>> read_tail(Buffer(tokenize_lines([')'])))
    nil
    >>> read_tail(Buffer(tokenize_lines(['2 3)'])))
    Pair(2, Pair(3, nil))
    >>> read_line('(1 . 2)')
    Pair(1, 2)
    """
    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        # BEGIN PROBLEM 1
        "*** YOUR CODE HERE ***"
        try:
            token_buffer = BuffWrapper(src)
            scm_expr = parser.get_rest_of_list(token_buffer)
            return make_proj_pair(scm_expr)
        except scheme_exceptions.ParseError as e:
            raise SyntaxError(e)
        # END PROBLEM 1
    except EOFError:
        raise SyntaxError('unexpected end of file')


# Convenience methods

def buffer_input(prompt='scm> '):
    """Return a Buffer instance containing interactive input."""
    return Buffer(tokenize_lines(InputReader(prompt)))


def buffer_lines(lines, prompt='scm> ', show_prompt=False):
    """Return a Buffer instance iterating through LINES."""
    if show_prompt:
        input_lines = lines
    else:
        input_lines = LineReader(lines, prompt)
    return Buffer(tokenize_lines(input_lines))


def read_line(line):
    """Read a single string LINE as a Scheme expression."""
    return scheme_read(Buffer(tokenize_lines([line])))


def repl_str(val):
    """Should largely match str(val), except for booleans and undefined."""
    if val is True:
        return "#t"
    if val is False:
        return "#f"
    if val is None:
        return "undefined"
    return str(val)


# Interactive loop
def read_print_loop():
    """Run a read-print loop for Scheme expressions."""
    while True:
        try:
            src = buffer_input('read> ')
            while src.more_on_line:
                expression = scheme_read(src)
                print('str :', expression)
                print('repr:', repr(expression))
        except (SyntaxError, ValueError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            print()
            return


@main
def main(*args):
    if len(args) and '--repl' in args:
        read_print_loop()
