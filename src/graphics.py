import math
from typing import List

from src.datamodel import Expression, Number, Undefined, String
from src.environment import global_attr
from src.evaluate_apply import Frame
from src.helper import verify_exact_callable_length, verify_min_callable_length
from src.primitives import SingleOperandPrimitive, BuiltIn
from src.scheme_exceptions import OperandDeduceError


class Canvas:
    SIZE = 1000

    def __init__(self):
        self.x = self.SIZE / 2
        self.y = self.SIZE / 2
        self.angle = 0  # w.r.t vertical

        self.bg_color = [0, 0, 0]

        self.board = self.reset_board()

        self.pen_down = False
        self.color = (0, 0, 0)

        self.size = 1

    def reset_board(self):
        self.board = [[self.bg_color] * self.SIZE for _ in range(self.SIZE)]
        return self.board

    def draw(self, x, y, color):
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return
        self.board[x][y] = color

    def move(self, x, y):
        if self.pen_down:
            dist = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
            move_num = round(dist * 2 + 1)
            for i in range(move_num):
                curr_x, curr_y = (round(a * (1 - i / move_num) + b * (i / move_num))
                                  for a, b in [[x, self.x], [y, self.y]])
                self.draw(curr_x, curr_y, self.color)
        self.x = x
        self.y = y

    def rotate(self, theta):
        self.angle += theta
        self.angle %= 360

    def abs_rotate(self, theta):
        self.angle = theta % 360

    def forward(self, dist):
        self.move(self.x + dist * math.cos(self.angle / 360 * 2 * math.pi),
                  self.y + dist * math.sin(self.angle / 360 * 2 * math.pi))

    def pendown(self):
        self.pen_down = True

    def penup(self):
        self.pen_down = False

    def rect(self, x, y, color):
        for i in range(x, x + self.size):
            for j in range(y, y + self.size):
                self.draw(i, j, color)


def make_color(expression: Expression):
    if not isinstance(expression, String):
        raise OperandDeduceError(f"Unable to convert {expression} to a color.")


@global_attr("bk")
@global_attr("back")
@global_attr("backward")
class Backward(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.forward(-operand.value)
        return Undefined


@global_attr("begin_fill")
class BeginFill(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        raise NotImplementedError("fill not yet implemented")


@global_attr("bgcolor")
class BGColor(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        canvas.bg_color = make_color(operand)
        return Undefined


@global_attr("circle")
class Circle(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 1, len(operands))
        if len(operands) > 2:
            verify_exact_callable_length(self, 2, len(operands))
        raise NotImplementedError("circle not yet implemented")


@global_attr("clear")
class Clear(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        canvas.reset_board()
        return Undefined


@global_attr("color")
class Color(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        canvas.color = make_color(operand)
        return Undefined


@global_attr("end_fill")
class EndFill(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        raise NotImplementedError("fill not yet implemented")


@global_attr("fd")
@global_attr("forward")
class Forward(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.forward(operand.value)
        return Undefined


@global_attr("lt")
@global_attr("left")
class Left(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.rotate(operand.value)
        return Undefined


@global_attr("rt")
@global_attr("right")
class Right(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.rotate(-operand.value)
        return Undefined


@global_attr("screen_width")
@global_attr("screen_height")
class ScreenSize(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        return Number(canvas.size)

@global_attr("setheading")
class SetHeading(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.abs_rotate(-operand.value)
        return Undefined


@global_attr("setposition")
class SetPosition(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        for operand in operands:
            if not isinstance(operand, Number):
                raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.move(operands[0].value, operands[1].value)
        return Undefined


canvas = Canvas()
