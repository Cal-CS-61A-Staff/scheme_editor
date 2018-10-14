from __future__ import annotations

from typing import Dict, List

from datamodel import Symbol, Expression, Integer, Pair, Nil
from gui import Holder, VisualExpression
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


def evaluate(expr: Expression, frame: Frame, gui_holder: Holder = None):
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
    if gui_holder is None:
        gui_holder = Holder(expr)  # dummy holder
    gui_holder.evaluate()
    visual_expression = VisualExpression(expr)  # magically copies the attributes of the expression and creates Holder objects
    gui_holder.link_visual(visual_expression)
    if isinstance(expr, Integer):
        return expr
    elif isinstance(expr, Symbol):
        out = frame.lookup(expr)
        visual_expression.value = out
        gui_holder.complete()
        return out
    elif isinstance(expr, Pair):
        operator = expr.first
        operator = evaluate(operator, frame, visual_expression.children[0])  # evaluating operator and storing it in visual_expression
        operands = pair_to_list(expr.rest)
        out = apply(operator, operands, frame, gui_holder)
        visual_expression.value = out
        gui_holder.complete()
        return out
    elif isinstance(expr, Nil):
        visual_expression.value = Nil
        gui_holder.complete()
        return Nil


def apply(operator: Expression, operands: List[Expression], frame: Frame, gui_holder: Holder):
    if isinstance(operator, Callable):
        gui_holder.apply()
        return operator.execute(operands, frame, gui_holder)
    else:
        raise CallableResolutionError(f"Unable to pass parameters into: '{operator}'")


class Callable(Expression):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        raise NotImplementedError()


def evaluate_all(operands: List[Expression], frame: Frame, operand_holders: List[Holder]) -> List[Expression]:
    return [evaluate(operand, frame, holder) for operand, holder in zip(operands, operand_holders)]