from typing import List

import gui
from datamodel import Expression, Nil
from environment import global_attr
from evaluate_apply import Callable, Frame
from helper import verify_exact_callable_length
from primitives import SingleOperandPrimitive


@global_attr("print")
class Print(SingleOperandPrimitive):

    def execute_simple(self, operand: Expression) -> Expression:
        gui.logger.out(operand)
        return Nil
