from typing import List

from datamodel import Expression, Symbol, Pair, Integer, SingletonTrue, SingletonFalse, Nil, Boolean, bools
from gui import Holder, VisualExpression
from helper import pair_to_list, assert_all_integers, verify_exact_callable_length, verify_min_callable_length, \
    make_list
from evaluate_apply import Frame, evaluate, Callable, evaluate_all
from scheme_exceptions import ComparisonError, OperandDeduceError


class LambdaObject(Callable):
    def __init__(self, params: List[Symbol], body: Expression, frame: Frame):
        self.params = params
        self.body = body
        self.frame = frame

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        new_frame = Frame(self.frame)
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        gui_holder.apply()

        # need to substitute body expressions into the holder
        # we can wrap them in a begin?
        # that's unnecessarily complex
        # just put all the elements and then magically delete all but the last one
        # actually, put them all and then pop from the front after evaluation completes

        # gui_holder.expression = VisualExpression(self.body[0])

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.base_expr) for expr in self.body])
        for i, expression in enumerate(self.body):
            # holder = gui_holder.expression.children[0]
            out = evaluate(expression, new_frame, gui_holder.expression.children[i])
            # if len(gui_holder.expression.children) > 1:
            #     gui_holder.expression.children.pop(0)
        # gui_holder.expression = gui_holder.expression.children[0].expression
        return out

    def __repr__(self):
        return "#[lambda_obj]"


class Lambda(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
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
        if len(operands) == 2:
            # noinspection PyTypeChecker
            return LambdaObject(params, operands[1:], frame)
        else:
            # noinspection PyTypeChecker
            return LambdaObject(params, [Pair(Symbol("begin"), make_list(operands[1:]))], frame)

    def __repr__(self):
        return "#[lambda]"


class Add(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        assert_all_integers(operands)
        return Integer(sum(operand.value for operand in operands))

    def __repr__(self):
        return "#[+]"


class Subtract(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        assert_all_integers(operands)
        return Integer(operands[0].value - sum(operand.value for operand in operands[1:]))

    def __repr__(self):
        return "#[-]"


class Multiply(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        assert_all_integers(operands)
        out = 1
        for operand in operands:
            out *= operand.value
        return Integer(out)

    def __repr__(self):
        return "#[*]"


class Define(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        first = operands[0]
        if isinstance(first, Symbol):
            frame.assign(first, evaluate(operands[1], frame, gui_holder.expression.children[2]))
            return first
        elif isinstance(first, Pair):
            name = first.first
            operands[0] = first.rest
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected a Symbol, not {name}.")
            frame.assign(name, Lambda().execute(operands, frame, gui_holder))
            return name
        else:
            raise OperandDeduceError("Expected a Symbol or List (aka Pair) as first operand of define.")

    def __repr__(self):
        return "#[define]"


class If(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        if len(operands) > 3:
            verify_exact_callable_length(self, 3, len(operands))
        if evaluate(operands[0], frame, gui_holder.expression.children[1]) is SingletonFalse:
            if len(operands) == 2:
                return Nil
            else:
                # gui_holder.expression = gui_holder.expression.children[3].expression
                return evaluate(operands[2], frame, gui_holder.expression.children[3])
        else:
            # gui_holder.expression = gui_holder.expression.children[1].expression
            return evaluate(operands[1], frame, gui_holder.expression.children[2])

    def __repr__(self):
        return "#[if]"


class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        out = None
        for operand, holder in zip(operands, gui_holder.expression.children[1:]):
            out = evaluate(operand, frame, holder)
        return out

    def __repr__(self):
        return "#[begin]"


class IntegerEq(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 2, len(operands))
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        for operand in operands:
            if not isinstance(operand, Integer):
                raise ComparisonError(f"Unable to perform integer comparison with: {operand}.")
        return bools[operands[0].value == operands[1].value]

    def __repr__(self):
        return "#[=]"


class IntegerLess(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 2, len(operands))
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        for operand in operands:
            if not isinstance(operand, Integer):
                raise ComparisonError(f"Unable to perform integer comparison with: {operand}.")
        return bools[operands[0].value < operands[1].value]

    def __repr__(self):
        return "#[<]"


class IntegerGreater(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 2, len(operands))
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        for operand in operands:
            if not isinstance(operand, Integer):
                raise ComparisonError(f"Unable to perform integer comparison with: {operand}.")
        return bools[operands[0].value > operands[1].value]

    def __repr__(self):
        return "#[>]"


class Quote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return operands[0]

    def __repr__(self):
        return "#[quote]"


class Eval(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        operand = evaluate(operands[0], frame, gui_holder.expression.children[1])
        gui_holder.expression = VisualExpression(operands[0], gui_holder.expression.base_expr)

        return evaluate(operand, frame, gui_holder.expression.children[1])

    def __repr__(self):
        return "#[eval]"


class Car(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        operand = operands[0]
        if isinstance(operand, Pair):
            return operand.first
        else:
            raise OperandDeduceError(f"Unable to extract first element, as {operand} is not a Pair.")

    def __repr__(self):
        return "#[car]"


class Cdr(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        operand = operands[0]
        if isinstance(operand, Pair):
            return operand.rest
        else:
            raise OperandDeduceError(f"Unable to extract second element, as {operand} is not a Pair.")

    def __repr__(self):
        return "#[cdr]"


class Cond(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for cond_i, cond in enumerate(operands):
            if not isinstance(cond, Pair):
                raise OperandDeduceError(f"Unable to evaluate clause of cond, as {operand} is not a Pair.")
            expanded = pair_to_list(cond)
            cond_holder = gui_holder.expression.children[cond_i + 1]
            verify_min_callable_length(self, 2, len(expanded))
            cond_holder.link_visual(VisualExpression(cond))
            if evaluate(expanded[0], frame, cond_holder.expression.children[0]) is not SingletonFalse:
                out = None
                for i, expr in enumerate(expanded[1:]):
                    out = evaluate(expr, frame, cond_holder.expression.children[i + 1])
                return out
        return Nil

    def __repr__(self):
        return "#[cond]"


class And(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1])
            if value is SingletonFalse:
                return SingletonFalse
        return SingletonTrue

    def __repr__(self):
        return "#[and]"


class Or(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1])
            if value is SingletonTrue:
                return SingletonTrue
        return SingletonFalse

    def __repr__(self):
        return "#[or]"


class Let(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))

        bindings = operands[0]
        if not isinstance(bindings, Pair):
            raise OperandDeduceError(f"Expected first argument of let to be a Pair, not {bindings}.")

        new_frame = Frame(frame)

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

        operands = evaluate_all(operands[1:], new_frame, gui_holder.expression.children[2:])

        return operands[-1]

    def __repr__(self):
        return "#[let]"


class Mu(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
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
        if len(operands) == 2:
            # noinspection PyTypeChecker
            return MuObject(params, operands[1:])
        else:
            # noinspection PyTypeChecker
            return MuObject(params, [Pair(Symbol("begin"), make_list(operands[1:]))])

    def __repr__(self):
        return "#[mu]"


class MuObject(Callable):
    def __init__(self, params: List[Symbol], body: Expression):
        self.params = params
        self.body = body

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        new_frame = Frame(frame)
        operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        verify_exact_callable_length(self, len(self.params), len(operands))

        gui_holder.apply()

        # need to substitute body expressions into the holder
        # we can wrap them in a begin?
        # that's unnecessarily complex
        # just put all the elements and then magically delete all but the last one
        # actually, put them all and then pop from the front after evaluation completes

        # gui_holder.expression = VisualExpression(self.body[0])

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.base_expr) for expr in self.body])
        for i, expression in enumerate(self.body):
            # holder = gui_holder.expression.children[0]
            out = evaluate(expression, new_frame, gui_holder.expression.children[i])
            # if len(gui_holder.expression.children) > 1:
            #     gui_holder.expression.children.pop(0)
        # gui_holder.expression = gui_holder.expression.children[0].expression
        return out

    def __repr__(self):
        return "#[mu_obj]"


def build_global_frame():
    global_frame = Frame()
    global_frame.assign(Symbol("+"), Add())
    global_frame.assign(Symbol("-"), Subtract())
    global_frame.assign(Symbol("*"), Multiply())
    global_frame.assign(Symbol("define"), Define())
    global_frame.assign(Symbol("lambda"), Lambda())
    global_frame.assign(Symbol("begin"), Begin())
    global_frame.assign(Symbol("if"), If())
    global_frame.assign(Symbol("#t"), SingletonTrue)
    global_frame.assign(Symbol("#f"), SingletonFalse)
    global_frame.assign(Symbol("="), IntegerEq())
    global_frame.assign(Symbol("<"), IntegerLess())
    global_frame.assign(Symbol(">"), IntegerGreater())
    global_frame.assign(Symbol("quote"), Quote())
    global_frame.assign(Symbol("eval"), Eval())
    global_frame.assign(Symbol("car"), Car())
    global_frame.assign(Symbol("cdr"), Cdr())
    global_frame.assign(Symbol("nil"), Nil)
    global_frame.assign(Symbol("cond"), Cond())
    global_frame.assign(Symbol("and"), And())
    global_frame.assign(Symbol("or"), Or())
    global_frame.assign(Symbol("let"), Let())
    global_frame.assign(Symbol("mu"), Mu())

    return global_frame
