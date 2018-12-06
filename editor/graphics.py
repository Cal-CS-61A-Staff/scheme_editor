import math
from typing import List

from datamodel import Expression, Number, Undefined, String, Symbol
from environment import global_attr
from evaluate_apply import Frame
from helper import verify_exact_callable_length, verify_min_callable_length
from primitives import SingleOperandPrimitive, BuiltIn
from scheme_exceptions import OperandDeduceError


class Canvas:
    SIZE = 1000

    def __init__(self):
        self.x = None
        self.y = None
        self.angle = None
        self.bg_color = None
        self.moves = None
        self.pen_down = None
        self.color = None
        self.size = None

        self.reset()

    def move(self, x: float, y: float):
        if self.pen_down:
            self.moves.extend([["moveTo", self.x, self.y], ["lineTo", x, y]])
        self.x = x
        self.y = y

    def set_bg(self, color):
        self.bg_color = color

    def rotate(self, theta: float):
        self.angle += theta
        self.angle %= 360

    def abs_rotate(self, theta: float):
        self.angle = theta % 360

    def forward(self, dist: float):
        self.move(self.x + dist * math.cos(self.angle / 360 * 2 * math.pi),
                  self.y + dist * math.sin(self.angle / 360 * 2 * math.pi))

    def pendown(self):
        self.pen_down = True

    def penup(self):
        self.pen_down = False

    def rect(self, x: float, y: float, color: str):
        old_color = self.color
        self.moves.extend([
            ["fillStyle", color],
            ["rect", x, y, self.size, self.size],
            ["fillStyle", old_color]
        ])

    def export(self):
        if self.moves:
            out = [["fillStyle", self.bg_color],
                   ["rect", 0, 0, self.SIZE, self.SIZE]
                   ] + self.moves
        else:
            out = []
        self.reset()
        return out

    def reset(self):
        self.x = self.SIZE / 2
        self.y = self.SIZE / 2
        self.angle = 0
        self.bg_color = "#ffffff"
        self.moves = []
        self.pen_down = True
        self.color = "#000000"
        self.size = 1


def make_color(expression: Expression) -> str:
    if not isinstance(expression, String) and not isinstance(expression, Symbol):
        raise OperandDeduceError(f"Unable to convert {expression} to a color.")
    return expression.value


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
        canvas.set_bg(make_color(operand))
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
        canvas.moves = []
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


@global_attr("pd")
@global_attr("pendown")
class PenDown(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        canvas.pendown()
        return Undefined


@global_attr("pu")
@global_attr("penup")
class PenUp(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        canvas.penup()
        return Undefined


@global_attr("pixel")
class Pixel(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 3, len(operands))
        x, y, c, = operands
        for v in x, y:
            if not isinstance(v, Number):
                raise OperandDeduceError(f"Expected operand to be Number, not {v}")
        canvas.rect(x.value, y.value, make_color(c))
        return Undefined


@global_attr("pixelsize")
class PixelSize(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.size = operand.value
        return Undefined


@global_attr("rgb")
class RGB(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 3, len(operands))
        for operand in operands:
            if not isinstance(operand, Number):
                raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
            if not 0 <= operand.value <= 1:
                raise OperandDeduceError(f"RGB values must be between 0 and 1, not {operand}")
        return String("#" + "".join('{:02X}'.format(round(x.value * 255)) for x in operands))


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
        return Number(canvas.SIZE)


@global_attr("seth")
@global_attr("setheading")
class SetHeading(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number):
            raise OperandDeduceError(f"Expected operand to be Number, not {operand}")
        canvas.abs_rotate(-operand.value)
        return Undefined


@global_attr("setpos")
@global_attr("goto")
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
