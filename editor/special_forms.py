from typing import List

from editor.datamodel import Expression, Symbol, Pair, SingletonTrue, SingletonFalse, Nil, Undefined
from editor.environment import global_attr
from editor.evaluate_apply import Frame, evaluate, Callable, evaluate_all, Applicable
from editor.gui import Holder, VisualExpression, return_symbol, logger
from editor.helper import pair_to_list, verify_exact_callable_length, verify_min_callable_length, \
    make_list
from editor.scheme_exceptions import OperandDeduceError


class LambdaObject(Applicable):
    def __init__(self, params: List[Symbol], body: List[Expression], frame: Frame, name: str = "lambda"):
        self.params = params
        self.body = body
        self.frame = frame
        self.name = name

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        new_frame = Frame(self.name, self.frame)
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        gui_holder.apply()

        if len(self.body) > 1:
            body = [Pair(Symbol("begin"), make_list(self.body))]
        else:
            body = self.body

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.display_value) for expr in body])
        for i, expression in enumerate(body):
            out = evaluate(expression, new_frame, gui_holder.expression.children[i],
                           i == len(body) - 1, log_stack=len(self.body) == 1)
        new_frame.assign(return_symbol, out)
        return out

    def __repr__(self):
        if logger.strict_mode:
            return f"(lambda ({(' '.join(map(repr, self.params)))}) {' '.join(map(repr, self.body))})"
        return f"({self.name} {' '.join(map(repr, self.params))}) [parent = {self.frame.id}]"

    def __str__(self):
        if logger.strict_mode:
            return repr(self)
        return f"#[{self.name}]"


@global_attr("lambda")
class Lambda(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, name: str = "lambda"):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if isinstance(params, Symbol):
            raise NotImplementedError("Varargs not yet implemented!")
            params = [operands[0]]
        elif isinstance(params, Pair) or params is Nil:
            params = pair_to_list(params)
        else:
            raise OperandDeduceError(f"{params} is neither a Symbol or a List (aka Pair) of Symbols.")
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")
        return LambdaObject(params, operands[1:], frame, name)


@global_attr("define")
class Define(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        first = operands[0]
        if isinstance(first, Symbol):
            verify_exact_callable_length(self, 2, len(operands))
            frame.assign(first, evaluate(operands[1], frame, gui_holder.expression.children[2]))
            return first
        elif isinstance(first, Pair):
            name = first.first
            operands[0] = first.rest
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected a Symbol, not {name}.")
            frame.assign(name, Lambda().execute(operands, frame, gui_holder, name.value))
            return name
        else:
            raise OperandDeduceError("Expected a Symbol or List (aka Pair) as first operand of define.")


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
                # gui_holder.expression = gui_holder.expression.children[3].expression
                return evaluate(operands[2], frame, gui_holder.expression.children[3], True)
        else:
            # gui_holder.expression = gui_holder.expression.children[1].expression
            return evaluate(operands[1], frame, gui_holder.expression.children[2], True)


@global_attr("begin")
class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        out = None
        for i, (operand, holder) in enumerate(zip(operands, gui_holder.expression.children[1:])):
            out = evaluate(operand, frame, holder, i == len(operands) - 1)
        return out


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
                # TODO: Can be tail context under rare circumstances
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


@global_attr("mu")
class Mu(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, name: str = "mu"):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if isinstance(params, Symbol):
            params = [operands[0]]
        elif isinstance(params, Pair) or params is Nil:
            params = pair_to_list(params)
        else:
            raise OperandDeduceError(f"{params} is neither a Symbol or a List (aka Pair) of Symbols.")
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")
        # noinspection PyTypeChecker
        return MuObject(params, operands[1:], name)


class MuObject(Applicable):
    def __init__(self, params: List[Symbol], body: List[Expression], name: str):
        self.params = params
        self.body = body
        self.name = name

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        new_frame = Frame(self.name, frame)
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        gui_holder.apply()

        if len(self.body) > 1:
            body = [Pair(Symbol("begin"), make_list(self.body))]
        else:
            body = self.body

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.display_value) for expr in body])
        for i, expression in enumerate(body):
            out = evaluate(expression, new_frame, gui_holder.expression.children[i],
                           i == len(body) - 1, log_stack=len(self.body) == 1)
        new_frame.assign(return_symbol, out)
        return out

    def __repr__(self):
        if logger.strict_mode:
            return f"(mu ({(' '.join(map(repr, self.params)))}) {' '.join(map(repr, self.body))})"
        return f"({self.name} {' '.join(map(repr, self.params))})"

    def __str__(self):
        if logger.strict_mode:
            return repr(self)
        return f"#[{self.name}]"


class MacroObject(Callable):
    def __init__(self, params: List[Symbol], body: List[Expression], frame: Frame, name: str):
        self.params = params
        self.body = body
        self.frame = frame
        self.name = name

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        new_frame = Frame(self.name, self.frame)
        verify_exact_callable_length(self, len(self.params), len(operands))

        if len(self.body) > 1:
            body = [Pair(Symbol("begin"), make_list(self.body))]
        else:
            body = self.body

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.display_value) for expr in body])
        for i, expression in enumerate(body):
            out = evaluate(expression, new_frame, gui_holder.expression.children[i],
                           i == len(body) - 1, log_stack=len(self.body) == 1)

        gui_holder.expression.set_entries([VisualExpression(out, gui_holder.expression.display_value)])
        new_frame.assign(return_symbol, out)
        return evaluate(out, frame, gui_holder.expression.children[i], True)

    def __repr__(self):
        if logger.strict_mode:
            return f"(lambda ({(' '.join(map(repr, self.params)))}) {' '.join(map(repr, self.body))})"
        return f"({self.name} {' '.join(map(repr, self.params))}) [parent = {self.frame.id}]"

    def __str__(self):
        if logger.strict_mode:
            return repr(self)
        return f"#[{self.name}]"


@global_attr("define-macro")
class DefineMacro(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if not isinstance(params, Pair):
            raise OperandDeduceError(f"Expected a Pair, not {params}, as the first operand of define-macro.")
        params = pair_to_list(params)
        for param in params:
            if not isinstance(param, Symbol):
                raise OperandDeduceError(f"{param} is not a Symbol.")
        name, *params = params
        frame.assign(name, MacroObject(params, operands[1:], frame, name.value))
        return name


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
                return out
        else:
            visual_expression.value = expr
            return expr
