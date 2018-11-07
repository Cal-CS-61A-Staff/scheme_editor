from typing import List

from src.helper import verify_exact_callable_length
from src.gui import Holder

from src.datamodel import Expression
from src.evaluate_apply import Frame, evaluate_all, Applicable


class BuiltIn(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True) -> Expression:
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        gui_holder.apply()
        return self.execute_evaluated(operands, frame)

    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        raise NotImplementedError()


class SingleOperandPrimitive(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 1, len(operands))
        operand = operands[0]
        return self.execute_simple(operand)

    def execute_simple(self, operand: Expression) -> Expression:
        raise NotImplementedError()


def load_primitives():
    __import__("src.arithmetic")
    __import__("src.lists")
    __import__("src.type_checking")
    __import__("src.console")
