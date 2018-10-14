from __future__ import annotations

from typing import Dict, List

from datamodel import Symbol, Expression, Integer, Pair, Nil
import gui
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


def evaluate(expr: Expression, frame: Frame, gui_holder: gui.Holder):
    """
    >>> global_frame = __import__("special_forms").build_global_frame()
    >>> gui_holder = __import__("gui").Holder(None)
    >>> __import__("gui").Root.setroot(gui_holder)
    >>> __import__("gui").silent = True

    >>> buff = __import__("lexer").TokenBuffer(["(+ 1 2)"])
    >>> expr = __import__("parser").get_expression(buff)
    >>> result = evaluate(expr, global_frame, gui_holder)
    >>> print(result)
    3
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(+ 3 4 5)"])), global_frame, gui_holder)
    12
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(* 3 4 5)"])), global_frame, gui_holder)
    60
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(* (+ 1 2) 4 5)"])), global_frame, gui_holder)
    60
    >>> __import__("gui").silent = False
    """
    if gui_holder is None:
        gui_holder = gui.Holder(expr)  # dummy holder
    visual_expression = gui.VisualExpression(expr)  # magically copies the attributes of the expression and creates Holder objects
    gui_holder.link_visual(visual_expression)
    if isinstance(expr, Integer):
        return expr
    elif isinstance(expr, Symbol):
        gui_holder.evaluate()
        out = frame.lookup(expr)
        visual_expression.value = out
        gui_holder.complete()
        return out
    elif isinstance(expr, Pair):
        gui_holder.evaluate()
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


def apply(operator: Expression, operands: List[Expression], frame: Frame, gui_holder: gui.Holder):
    if isinstance(operator, Callable):
        gui_holder.apply()
        return operator.execute(operands, frame, gui_holder)
    else:
        raise CallableResolutionError(f"Unable to pass parameters into: '{operator}'")


class Callable(Expression):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: gui.Holder):
        raise NotImplementedError()


def evaluate_all(operands: List[Expression], frame: Frame, operand_holders: List[gui.Holder]) -> List[Expression]:
    return [evaluate(operand, frame, holder) for operand, holder in zip(operands, operand_holders)]