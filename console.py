from typing import List

import gui
from datamodel import Expression, Nil
from environment import global_attr
from evaluate_apply import Callable, Frame
from helper import verify_exact_callable_length


@global_attr("print")
class Print(Callable):

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: gui.Holder):
        verify_exact_callable_length(self, 1, len(operands))
        gui.logger.out(operands[0])
        return Nil
