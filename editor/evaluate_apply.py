from typing import Dict, List, Union, Optional

import memory_usage
import log
from datamodel import Symbol, Expression, Number, Pair, Nil, Undefined, Boolean, String, Promise
from helper import pair_to_list
from scheme_exceptions import SymbolLookupError, CallableResolutionError, IrreversibleOperationError


class Frame:
    def __init__(self, name: str, parent: 'Frame' = None):
        self.parent = parent
        self.name = name
        self.vars: Dict[str, Expression] = {}
        self.id = "unknown - an error has occurred"
        self.temp = log.logger.fragile
        log.logger.frame_create(self)

    def assign(self, varname: Symbol, varval: Expression):
        if log.logger.fragile and not self.temp:
            raise IrreversibleOperationError()
        if isinstance(varval, Thunk):
            assert varname == log.return_symbol
            varval.bind(self)
            return
        self.vars[varname.value] = varval
        log.logger.frame_store(self, varname.value, varval)

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
    def __init__(self, expr: Expression, frame: Frame, gui_holder: log.Holder, log_stack: bool):
        self.expr = expr
        self.frame = frame
        self.log_stack = log_stack
        self.gui_holder = gui_holder
        self.return_frame: Optional[Frame] = None

    def __repr__(self):
        return "thunk"

    def evaluate(self, expr: Expression):
        if self.return_frame is not None:
            self.return_frame.assign(log.return_symbol, expr)

    def bind(self, return_frame: Frame):
        self.return_frame = return_frame


def evaluate(expr: Expression, frame: Frame, gui_holder: log.Holder,
             tail_context: bool = False, *, log_stack: bool=True) -> Union[Expression, Thunk]:
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

    depth = 0
    thunks = []
    holders = []

    while True:
        memory_usage.assert_low_memory()

        if isinstance(gui_holder.expression, Expression):
            visual_expression = log.VisualExpression(expr)
            gui_holder.link_visual(visual_expression)
        else:
            visual_expression = gui_holder.expression

        if log_stack:
            log.logger.eval_stack.append(f"{repr(expr)} [frame = {frame.id}]")
            depth += 1

        holders.append(gui_holder)

        from special_forms import MacroObject

        if isinstance(expr, Number) \
                or isinstance(expr, Callable) \
                or isinstance(expr, Boolean) \
                or isinstance(expr, String) \
                or isinstance(expr, Promise):
            ret = expr
        elif isinstance(expr, Symbol):
            gui_holder.evaluate()
            out = frame.lookup(expr)
            if isinstance(out, Callable) and not isinstance(out, Applicable) and not isinstance(out, MacroObject):
                raise SymbolLookupError(f"Variable not found in current environment: '{expr.value}'")
            ret = out
        elif isinstance(expr, Pair):
            if tail_context:
                if log_stack:
                    log.logger.eval_stack.pop()
                return Thunk(expr, frame, gui_holder, log_stack)
            else:
                gui_holder.evaluate()
                operator = expr.first
                if isinstance(operator, Symbol) \
                        and isinstance(frame.lookup(operator), Callable) \
                        and not isinstance(frame.lookup(operator), Applicable) \
                        and not isinstance(frame.lookup(operator), MacroObject):
                    operator = frame.lookup(operator)  # we don't evaluate special forms
                else:
                    # evaluating operator and storing it in visual_expression
                    operator = evaluate(operator, frame, visual_expression.children[0])
                operands = pair_to_list(expr.rest)
                out = apply(operator, operands, frame, gui_holder)
                if isinstance(out, Thunk):
                    expr, frame = out.expr, out.frame
                    gui_holder = out.gui_holder
                    thunks.append(out)
                    continue
                ret = out
        elif expr is Nil or expr is Undefined:
            ret = expr
        else:
            raise Exception("Internal error. Please report to maintainer!")

        for _ in range(depth):
            log.logger.eval_stack.pop()

        for thunk, holder in zip(reversed(thunks), reversed(holders)):
            holder.expression.value = ret
            holder.complete()
            thunk.evaluate(ret)

        holders[0].expression.value = ret
        holders[0].complete()

        return ret


def apply(operator: Expression, operands: List[Expression], frame: Frame, gui_holder: log.Holder):
    if isinstance(operator, Callable):
        return operator.execute(operands, frame, gui_holder)
    elif isinstance(operator, Symbol):
        raise CallableResolutionError(f"Unable to pass parameters into the Symbol '{operator}'")
    else:
        raise CallableResolutionError(f"Unable to pass parameters into: '{operator}'")


class Callable(Expression):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: log.Holder):
        raise NotImplementedError()


class Applicable(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: log.Holder, eval_operands=True):
        raise NotImplementedError()


def evaluate_all(operands: List[Expression], frame: Frame, operand_holders: List[log.Holder]) -> List[Expression]:
    return [evaluate(operand, frame, holder) for operand, holder in zip(operands, operand_holders)]
