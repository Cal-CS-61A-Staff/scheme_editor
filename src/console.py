from typing import List

from src import gui
from src.datamodel import Expression, Undefined
from src.environment import global_attr
from src.evaluate_apply import Frame
from src.helper import verify_exact_callable_length
from src.primitives import SingleOperandPrimitive, BuiltIn


@global_attr("print")
class Print(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        gui.logger.out(operand)
        return Undefined


@global_attr("display")
class Display(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        gui.logger.out(operand, end="")
        return Undefined


@global_attr("newline")
class Newline(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        gui.logger.raw_out("\n")
        return Undefined
