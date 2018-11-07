import math

import src.execution as execution
from src.scheme_exceptions import MathError
from src.datamodel import Symbol, Nil, SingletonTrue, SingletonFalse, Expression, Number
from src.evaluate_apply import Frame
from src.primitives import SingleOperandPrimitive


def make_frame_decorator(defdict):
    def global_builtin(name):
        def decorator(cls):
            cls.__repr__ = lambda self: f"#[{name}]"
            defdict[Symbol(name)] = cls()
            return cls

        return decorator

    return global_builtin


defdict = {}
global_attr = make_frame_decorator(defdict)


class MathProcedure(SingleOperandPrimitive):
    def __init__(self, func):
        self.func = func

    def execute_simple(self, operand: Expression):
        if not isinstance(operand, Number):
            raise MathError
        return Number(self.func(operand.value), force_float=True)


def build_global_frame():
    from src import primitives
    primitives.load_primitives()
    frame = Frame("builtins")
    for k, v in defdict.items():
        frame.assign(k, v)
    frame.assign(Symbol("nil"), Nil)
    frame.assign(Symbol("#t"), SingletonTrue)
    frame.assign(Symbol("#f"), SingletonFalse)

    for name in ["acos", "acosh", "asin", "asinh", "atan", "atanh",
                 "ceil", "copysign", "cos", "cosh", "degrees", "floor", "log",
                 "log10", "log1p", "log2", "radians", "sin", "sinh", "sqrt",
                 "tan", "tanh", "trunc"]:
        frame.assign(Symbol(name), MathProcedure(getattr(math, name)))

    with open("src/builtins.scm") as file:
        execution.string_exec([" ".join(file.readlines())], lambda *x, **y: None, frame)

    return Frame("Global", frame)
