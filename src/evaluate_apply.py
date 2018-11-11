from __future__ import annotations

from abc import ABC
from typing import Dict, List, Union

from src.datamodel import Symbol, Expression, Number, Pair, Nil, Undefined, Boolean, String
from src import gui
from src.scheme_exceptions import SymbolLookupError, CallableResolutionError
from src.helper import pair_to_list


class Frame:
    def __init__(self, name: str, parent: Frame = None):
        self.parent = parent
        self.name = name
        self.vars: Dict[str, Expression] = {}
        self.id = "unknown (error)"
        gui.logger.frame_create(self)

    def assign(self, varname: Symbol, varval: Expression):
        self.vars[varname.value] = varval
        gui.logger.frame_store(self, varname.value, varval)

    def lookup(self, varname: Symbol):
        if varname.value in self.vars:
            return self.vars[varname.value]
        if self.parent is None:
            raise SymbolLookupError(f"Variable not found in current environment: '{varname}'")
        return self.parent.lookup(varname)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return repr(self.vars)


class Thunk:
    def __init__(self, expr: Expression, frame: Frame):
        self.expr = expr
        self.frame = frame

    def __repr__(self):
        return "thunk"


def evaluate(expr: Expression, frame: Frame, gui_holder: gui.Holder, tail_context: bool = False)\
        -> Union[Expression, Thunk]:
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
    while True:
        if gui_holder is None:
            gui_holder = gui.Holder(expr)  # dummy holder
        if isinstance(gui_holder.expression, Expression):
            visual_expression = gui.VisualExpression(expr)
            gui_holder.link_visual(visual_expression)
        else:
            visual_expression = gui_holder.expression

        if isinstance(expr, Number) \
                or isinstance(expr, Callable) \
                or isinstance(expr, Boolean) \
                or isinstance(expr, String):
            gui_holder.complete()
            visual_expression.value = expr
            return expr
        elif isinstance(expr, Symbol):
            gui_holder.evaluate()
            out = frame.lookup(expr)
            from src.special_forms import MacroObject
            if isinstance(out, Callable) and not isinstance(out, Applicable) and not isinstance(out, MacroObject):
                raise SymbolLookupError(f"Variable not found in current environment: '{expr.value}'")
            visual_expression.value = out
            gui_holder.complete()
            return out
        elif isinstance(expr, Pair):
            if gui.logger.skip_tree and gui.logger.skip_envs and tail_context:
                return Thunk(expr, frame)
            gui_holder.evaluate()
            operator = expr.first
            if isinstance(operator, Symbol) \
                    and isinstance(frame.lookup(operator), Callable) \
                    and not isinstance(frame.lookup(operator), Applicable):
                operator = frame.lookup(operator)
            else:
                operator = evaluate(operator, frame, visual_expression.children[
                    0])  # evaluating operator and storing it in visual_expression
            operands = pair_to_list(expr.rest)
            out = apply(operator, operands, frame, gui_holder)
            if isinstance(out, Thunk):
                expr, frame = out.expr, out.frame
                gui_holder = None
                continue
            visual_expression.value = out
            gui_holder.complete()
            return out
        elif expr is Nil or expr is Undefined:
            visual_expression.value = expr
            gui_holder.complete()
            return expr
        else:
            raise Exception("Internal error. Please report to maintainer!")


def apply(operator: Expression, operands: List[Expression], frame: Frame, gui_holder: gui.Holder):
    if isinstance(operator, Callable):
        return operator.execute(operands, frame, gui_holder)
    else:
        raise CallableResolutionError(f"Unable to pass parameters into: '{operator}'")


class Callable(Expression):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: gui.Holder):
        raise NotImplementedError()


class Applicable(Callable, ABC):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: gui.Holder, eval_operands=True):
        raise NotImplementedError()


def evaluate_all(operands: List[Expression], frame: Frame, operand_holders: List[gui.Holder]) -> List[Expression]:
    return [evaluate(operand, frame, holder) for operand, holder in zip(operands, operand_holders)]
