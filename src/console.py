from typing import List

from src.scheme_exceptions import OperandDeduceError
from src import gui
from src.datamodel import Expression, Undefined, Symbol, String
from src.environment import global_attr
from src.evaluate_apply import Frame
from src.helper import verify_exact_callable_length
from src.primitives import SingleOperandPrimitive, BuiltIn


@global_attr("print")
class Print(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        gui.logger.out(operand)
        print(operand)
        return Undefined


@global_attr("display")
class Display(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if isinstance(operand, String):
            gui.logger.raw_out(operand.value)
        else:
            gui.logger.out(operand, end="")
        return Undefined


@global_attr("newline")
class Newline(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        gui.logger.raw_out("\n")
        return Undefined


@global_attr("load")
class Load(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        import src.execution as execution
        if not gui.logger.strict_mode:
            raise NotImplementedError("Unable to load files from web interface.")
        verify_exact_callable_length(self, 1, len(operands))
        if not isinstance(operands[0], Symbol):
            raise OperandDeduceError(f"Load expected a Symbol, received {operands[0]}.")
        with open(f"{operands[0].value}.scm") as file:
            execution.string_exec([" ".join(file.readlines())], lambda *x, **y: None, frame)
