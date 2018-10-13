from typing import List

from datamodel import Expression, Symbol, Pair, Integer, SingletonTrue, SingletonFalse, Nil
from helper import pair_to_list, assert_all_integers, verify_exact_callable_length, verify_min_callable_length
from evaluate_apply import Frame, evaluate, Callable, evaluate_all
from scheme_exceptions import CallableResolutionError, ComparisonError


class LambdaObject(Callable):
    def __init__(self, params: List[Symbol], body: List[Expression], frame: Frame):
        self.params = params
        self.body = body
        self.frame = frame

    def execute(self, operands: List[Expression], _: Frame):
        new_frame = Frame(self.frame)
        operands = evaluate_all(operands, self.frame)
        verify_exact_callable_length(self, len(self.params), len(operands))
        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)
        out = None
        for expression in self.body:
            out = evaluate(expression, new_frame)
        return out


class Lambda(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, len(operands), 2)
        params = operands[0]
        if isinstance(params, Symbol):
            params = [operands[0]]
        elif isinstance(params, Pair):
            params = pair_to_list(params)
        else:
            raise CallableResolutionError(f"{params} is neither a Symbol or a List (aka Pair) of Symbols.")
        for param in params:
            if not isinstance(param, Symbol):
                raise CallableResolutionError(f"{param} is not a Symbol.")
        return LambdaObject(params, operands[1:], frame)


class Add(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        operands = evaluate_all(operands, frame)
        assert_all_integers(operands)
        return Integer(sum(operand.value for operand in operands))


class Multiply(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        operands = evaluate_all(operands, frame)
        assert_all_integers(operands)
        out = 1
        for operand in operands:
            out *= operand.value
        return Integer(out)


class Define(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 1, len(operands))
        first = operands[0]
        if isinstance(first, Symbol):
            frame.assign(first, evaluate(operands[1], frame))
            return first
        elif isinstance(first, Pair):
            name = first.first
            operands[0] = first.rest
            if not isinstance(name, Symbol):
                raise CallableResolutionError(f"Expected a Symbol, not {name}.")
            frame.assign(name, Lambda().execute(operands, frame))
            return name
        else:
            raise CallableResolutionError("Expected a Symbol or List (aka Pair) as first operand of define.")


class If(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 2, len(operands))
        if len(operands) > 3:
            verify_exact_callable_length(self, 3, len(operands))
        if evaluate(operands[0], frame) is SingletonFalse:
            return Nil if len(operands) == 2 else evaluate(operands[2], frame)
        else:
            return evaluate(operands[1], frame)


class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 0, len(operands))
        out = None
        for operand in operands:
            out = evaluate(operand, frame)
        return out


class IntegerEq(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        for operand in operands:
            if not isinstance(operand, Integer):
                raise ComparisonError(f"Unable to perform integer comparison with: {operand}.")
        return operands[0].value == operands[1].value

class IntegerLess(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        for operand in operands:
            if not isinstance(operand, Integer):
                raise ComparisonError(f"Unable to perform integer comparison with: {operand}.")
        return operands[0].value < operands[1].value

class IntegerGreater(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        for operand in operands:
            if not isinstance(operand, Integer):
                raise ComparisonError(f"Unable to perform integer comparison with: {operand}.")
        return operands[0].value > operands[1].value


class Quote(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 1, len(operands))
        return operands[0]

class Eval(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 1, len(operands))
        return evaluate(evaluate(operands[0], frame), frame)


def build_global_frame():
    global_frame = Frame()
    global_frame.assign(Symbol("+"), Add())
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

    return global_frame