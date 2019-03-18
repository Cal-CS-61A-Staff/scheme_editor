from typing import List, Optional, Type

from datamodel import Expression, Symbol, Pair, SingletonTrue, SingletonFalse, Nil, Undefined, Promise
from environment import global_attr
from evaluate_apply import Frame, evaluate, Callable, evaluate_all, Applicable
from log import Holder, VisualExpression, return_symbol, logger
from helper import pair_to_list, verify_exact_callable_length, verify_min_callable_length, \
    make_list, dotted_pair_to_list
from lexer import TokenBuffer
from execution_parser import get_expression
from scheme_exceptions import OperandDeduceError, IrreversibleOperationError, LoadError, SchemeError


class ProcedureObject(Callable):
    evaluates_operands: bool
    lexically_scoped: bool
    name: str

    def __init__(self,
                 params: List[Symbol],
                 var_param: Optional[Symbol],
                 body: List[Expression],
                 frame: Frame,
                 name: str=None):
        super().__init__()
        self.params = params
        self.var_param = var_param
        self.body = body
        self.frame = frame
        self.name = name if name is not None else self.name

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        new_frame = Frame(self.name, self.frame if self.lexically_scoped else frame)

        if eval_operands and self.evaluates_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])

        if self.var_param:
            verify_min_callable_length(self, len(self.params), len(operands))
        else:
            verify_exact_callable_length(self, len(self.params), len(operands))

        if len(self.body) > 1:
            body = [Pair(Symbol("begin"), make_list(self.body))]
        else:
            body = self.body

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)

        if self.var_param:
            new_frame.assign(self.var_param, make_list(operands[len(self.params):]))

        out = None
        # noinspection PyTypeChecker
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.display_value) for expr in body])

        if self.evaluates_operands:
            gui_holder.apply()

        for i, expression in enumerate(body):
            out = evaluate(expression,
                           new_frame,
                           gui_holder.expression.children[i],
                           self.evaluates_operands and i == len(body) - 1,
                           log_stack=len(self.body) == 1)

        new_frame.assign(return_symbol, out)

        if not self.evaluates_operands:
            # noinspection PyTypeChecker
            gui_holder.expression.set_entries([VisualExpression(out, gui_holder.expression.display_value)])
            out = evaluate(out, frame, gui_holder.expression.children[i], True)

        return out

    def __repr__(self):
        if self.var_param is not None:
            varparams = " . " + self.var_param.value
        else:
            varparams = ""
        return f"({self.name} {' '.join(map(repr, self.params))} {varparams}) [parent = {self.frame.id}]"

    def __str__(self):
        return f"#[{self.name}]"


class LambdaObject(ProcedureObject, Applicable):
    evaluates_operands = True
    lexically_scoped = True
    name = "lambda"


class MuObject(ProcedureObject, Applicable):
    evaluates_operands = True
    lexically_scoped = False
    name = "mu"


class MacroObject(ProcedureObject, Callable):
    evaluates_operands = False
    lexically_scoped = True
    name = "macro"


class ProcedureBuilder(Callable):
    procedure: Type[ProcedureObject]

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, name: str = "lambda"):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        params, var_param = dotted_pair_to_list(params)
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")

        return self.procedure(params, var_param, operands[1:], frame, name)


@global_attr("lambda")
class Lambda(ProcedureBuilder):
    procedure = LambdaObject


@global_attr("mu")
class Mu(ProcedureBuilder):
    procedure = MuObject


class Macro(ProcedureBuilder):
    procedure = MacroObject


@global_attr("define-macro")
class DefineMacro(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if not isinstance(params, Pair):
            raise OperandDeduceError(f"Expected a Pair, not {params}, as the first operand of define-macro.")
        name = params.first
        operands[0] = params.rest
        if not isinstance(name, Symbol):
            raise OperandDeduceError(f"Expected a Symbol, not {name}.")
        frame.assign(name, Macro().execute(operands, frame, gui_holder, name.value))
        return name


@global_attr("define")
class Define(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if isinstance(params, Symbol):
            verify_exact_callable_length(self, 2, len(operands))
            frame.assign(params, evaluate(operands[1], frame, gui_holder.expression.children[2]))
            return params
        elif isinstance(params, Pair):
            name = params.first
            operands[0] = params.rest
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected a Symbol, not {name}.")
            frame.assign(name, Lambda().execute(operands, frame, gui_holder, name.value))
            return name
        else:
            raise OperandDeduceError(f"Expected a Pair, not {params}, as the first operand of define-macro.")


@global_attr("begin")
class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        out = None
        for i, (operand, holder) in enumerate(zip(operands, gui_holder.expression.children[1:])):
            out = evaluate(operand, frame, holder, i == len(operands) - 1)
        return out


@global_attr("if")
class If(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        if len(operands) > 3:
            verify_exact_callable_length(self, 3, len(operands))
        if evaluate(operands[0], frame, gui_holder.expression.children[1]) is SingletonFalse:
            if len(operands) == 2:
                return Undefined
            else:
                return evaluate(operands[2], frame, gui_holder.expression.children[3], True)
        else:
            return evaluate(operands[1], frame, gui_holder.expression.children[2], True)


@global_attr("quote")
class Quote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return operands[0]


@global_attr("eval")
class Eval(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operand = evaluate(operands[0], frame, gui_holder.expression.children[1])
        else:
            operand = operands[0]
        gui_holder.expression.set_entries([VisualExpression(operand, gui_holder.expression.display_value)])
        gui_holder.apply()
        return evaluate(operand, frame, gui_holder.expression.children[0], True)


@global_attr("apply")
class Apply(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 2, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        func, args = operands
        if not isinstance(func, Applicable):
            raise OperandDeduceError(f"Unable to apply {func}.")
        gui_holder.expression.set_entries([VisualExpression(Pair(func, args), gui_holder.expression.display_value)])
        gui_holder.expression.children[0].expression.children = []
        gui_holder.apply()
        args = pair_to_list(args)
        return func.execute(args, frame, gui_holder.expression.children[0], False)


@global_attr("cond")
class Cond(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for cond_i, cond in enumerate(operands):
            if not isinstance(cond, Pair):
                raise OperandDeduceError(f"Unable to evaluate clause of cond, as {cond} is not a Pair.")
            expanded = pair_to_list(cond)
            cond_holder = gui_holder.expression.children[cond_i + 1]
            cond_holder.link_visual(VisualExpression(cond))
            eval_condition = SingletonTrue
            if not isinstance(expanded[0], Symbol) or expanded[0].value != "else":
                eval_condition = evaluate(expanded[0], frame, cond_holder.expression.children[0])
            if (isinstance(expanded[0], Symbol) and expanded[0].value == "else") \
                    or eval_condition is not SingletonFalse:
                out = eval_condition
                for i, expr in enumerate(expanded[1:]):
                    out = evaluate(expr, frame, cond_holder.expression.children[i + 1], i == len(expanded) - 2)
                return out
        return Undefined


@global_attr("and")
class And(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        value = None
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1], i == len(operands) - 1)
            if value is SingletonFalse:
                return SingletonFalse
        return value if operands else SingletonTrue


@global_attr("or")
class Or(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1], i == len(operands) - 1)
            if value is not SingletonFalse:
                return value
        return SingletonFalse


@global_attr("let")
class Let(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))

        bindings = operands[0]
        if not isinstance(bindings, Pair) and bindings is not Nil:
            raise OperandDeduceError(f"Expected first argument of let to be a Pair, not {bindings}.")

        new_frame = Frame("anonymous let", frame)

        gui_holder.expression.children[1].link_visual(VisualExpression(bindings))
        bindings_holder = gui_holder.expression.children[1]

        bindings = pair_to_list(bindings)

        for i, binding in enumerate(bindings):
            if not isinstance(binding, Pair):
                raise OperandDeduceError(f"Expected binding to be a Pair, not {binding}.")
            binding_holder = bindings_holder.expression.children[i]
            binding_holder.link_visual(VisualExpression(binding))
            binding = pair_to_list(binding)
            if len(binding) != 2:
                raise OperandDeduceError(f"Expected binding to be of length 2, not {len(binding)}.")
            name, expr = binding
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected first element of binding to be a Symbol, not {name}.")
            new_frame.assign(name, evaluate(expr, frame, binding_holder.expression.children[1]))

        value = None

        for i, (operand, holder) in enumerate(zip(operands[1:], gui_holder.expression.children[2:])):
            value = evaluate(operand, new_frame, holder, i == len(operands) - 2)

        new_frame.assign(return_symbol, value)
        return value


@global_attr("quasiquote")
class Quasiquote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return Quasiquote.quasiquote_evaluate(operands[0], frame, gui_holder.expression.children[1])

    @classmethod
    def quasiquote_evaluate(cls, expr: Expression, frame: Frame, gui_holder: Holder):
        is_well_formed = False

        if isinstance(expr, Pair):
            try:
                lst = pair_to_list(expr)
            except OperandDeduceError:
                pass
            else:
                is_well_formed = not any(map(lambda x: isinstance(x, Symbol) and x.value in ["unquote", "quasiquote"], lst))

        visual_expression = VisualExpression(expr)
        gui_holder.link_visual(visual_expression)
        if not is_well_formed:
            visual_expression.children[2:] = []

        if isinstance(expr, Pair):
            if isinstance(expr.first, Symbol) and expr.first.value == "unquote":
                gui_holder.evaluate()
                verify_exact_callable_length(Symbol("unquote"), 1, len(pair_to_list(expr)) - 1)
                out = evaluate(expr.rest.first, frame, visual_expression.children[1])
                visual_expression.value = out
                gui_holder.complete()
                return out
            elif isinstance(expr.first, Symbol) and expr.first.value == "quasiquote":
                visual_expression.value = expr
                gui_holder.complete()
                return expr
            else:
                if is_well_formed:
                    out = []
                    for sub_expr, holder in zip(pair_to_list(expr), visual_expression.children):
                        out.append(Quasiquote.quasiquote_evaluate(sub_expr, frame, holder))
                    out = make_list(out)
                else:
                    out = Pair(Quasiquote.quasiquote_evaluate(expr.first, frame, visual_expression.children[0]),
                               Quasiquote.quasiquote_evaluate(expr.rest, frame, visual_expression.children[1]))
                visual_expression.value = out
                gui_holder.complete()
                return out
        else:
            visual_expression.value = expr
            gui_holder.complete()
            return expr


@global_attr("load")
class Load(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        if not isinstance(operands[0], Symbol):
            raise OperandDeduceError(f"Load expected a Symbol, received {operands[0]}.")
        if logger.fragile:
            raise IrreversibleOperationError()
        try:
            with open(f"{operands[0].value}.scm") as file:
                code = "(begin" + "\n".join(file.readlines()) + ")"
                buffer = TokenBuffer([code])
                expr = get_expression(buffer)
                # noinspection PyTypeChecker
                gui_holder.expression.set_entries([VisualExpression(expr, gui_holder.expression.display_value)])
                gui_holder.apply()
                return evaluate(expr, frame, gui_holder.expression.children[0], True)
        except OSError as e:
            raise LoadError(e)


@global_attr("delay")
class Delay(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return Promise(operands[0], frame)


@global_attr("force")
class Force(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        operand = operands[0]
        if eval_operands:
            operand = evaluate_all(operands, frame, gui_holder.expression.children[1:])[0]
        if not isinstance(operand, Promise):
            raise OperandDeduceError(f"Force expected a Promise, received {operand}")
        if operand.forced:
            return operand.expr
        if logger.fragile:
            raise IrreversibleOperationError()
        # noinspection PyTypeChecker
        gui_holder.expression.set_entries([VisualExpression(operand.expr, gui_holder.expression.display_value)])
        gui_holder.apply()
        operand.expr = evaluate(operand.expr, operand.frame, gui_holder.expression.children[0])
        operand.force()
        return operand.expr


@global_attr("cons-stream")
class ConsStream(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 2, len(operands))
        operands[0] = evaluate(operands[0], frame, gui_holder.expression.children[1])
        return Pair(operands[0], Delay().execute(operands[1:], frame, gui_holder))


@global_attr("error")
class Error(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        raise SchemeError(operands[0])
