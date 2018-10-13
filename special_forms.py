from typing import List

from datamodel import Expression, Symbol, Pair, Integer
from helper import pair_to_list
from evaluate_apply import Frame, evaluate, Callable, evaluate_all
from scheme_exceptions import CallableResolutionError, ArithmeticError


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


class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 0, len(operands))
        out = None
        for operand in operands:
            out = evaluate(operand, frame)
        return out


def assert_all_integers(operands):
    for operand in operands:
        if not isinstance(operand, Integer):
            raise ArithmeticError(f"Unable to perform arithmetic, as {operand} is not an integer.")


def verify_exact_callable_length(operator: Expression, expected: int, actual: int):
    if expected != actual:
        raise CallableResolutionError(f"{operator} expected {expected} operands, received {actual}.")


def verify_min_callable_length(operator: Expression, expected: int, actual: int):
    if expected > actual:
        raise CallableResolutionError(f"{operator} expected {expected} operands, received {actual}.")

def build_global_frame():
    global_frame = Frame()
    global_frame.assign(Symbol("+"), Add())
    global_frame.assign(Symbol("*"), Multiply())
    global_frame.assign(Symbol("define"), Define())
    global_frame.assign(Symbol("lambda"), Lambda())
    global_frame.assign(Symbol("begin"), Begin())

    return global_frame