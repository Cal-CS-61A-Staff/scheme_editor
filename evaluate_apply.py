from __future__ import annotations

from typing import Dict, List

from datamodel import Symbol, Expression, Integer, Pair, Nil
from scheme_exceptions import NameError, CallableResolutionError
from helper import pair_to_list


class Frame:
    def __init__(self, parent: Frame = None):
        self.parent = parent
        self.vars: Dict[Symbol, Expression] = {}

    def assign(self, varname: Symbol, varval: Expression):
        self.vars[varname.value] = varval

    def lookup(self, varname: Symbol):
        if varname.value in self.vars:
            return self.vars[varname.value]
        if self.parent is None:
            raise NameError(f"Variable not found in current environment: '{varname}'")
        return self.parent.lookup(varname)


def evaluate(expr: Expression, frame: Frame):
    """
    >>> global_frame = __import__("special_forms").build_global_frame()

    >>> buff = __import__("lexer").TokenBuffer(["(+ 1 2)"])
    >>> expr = __import__("parser").get_expression(buff)
    >>> result = evaluate(expr, global_frame)
    >>> print(result)
    3
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(+ 3 4 5)"])), global_frame)
    12
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(* 3 4 5)"])), global_frame)
    60
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(* (+ 1 2) 4 5)"])), global_frame)
    60
    """
    if isinstance(expr, Integer):
        return expr
    elif isinstance(expr, Symbol):
        return frame.lookup(expr)
    elif isinstance(expr, Pair):
        operator = expr.first
        operator = evaluate(operator, frame)
        operands = pair_to_list(expr.rest)
        return apply(operator, operands, frame)
    elif isinstance(expr, Nil):
        return Nil


def apply(operator: Expression, operands: List[Expression], frame: Frame):
    if isinstance(operator, Callable):
        return operator.execute(operands, frame)
    else:
        raise CallableResolutionError(f"Unable to pass parameters into: '{operator}'")


class Callable(Expression):
    def execute(self, operands: List[Expression], frame: Frame):
        raise NotImplementedError()


def evaluate_all(operands: List[Expression], frame: Frame) -> List[Expression]:
    return [evaluate(operand, frame) for operand in operands]