from __future__ import annotations

from typing import Union


class Expression:
    pass


class ValueHolder(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class Symbol(ValueHolder):
    pass


class Number(ValueHolder):
    # noinspection PyMissingConstructor
    def __init__(self, value, *, force_float=False):
        if value == round(value) and not force_float:
            self.value = round(value)
        else:
            self.value = value

    def __repr__(self):
        return super().__repr__()


class Pair(Expression):
    def __init__(self, first: Expression, rest: Union[Pair, Nil]):
        self.first = first
        self.rest = rest

    def __repr__(self):
        if isinstance(self.rest, Pair):
            return f"({self.first} {repr(self.rest)[1:-1]})"
        elif self.rest is Nil:
            return f"({self.first})"
        else:
            return f"({self.first} . {self.rest})"


class NilType(Expression):
    def __repr__(self):
        from src.gui import logger
        if logger.strict_mode:
            return "()"
        return "nil"


class UndefinedType(Expression):
    def __repr__(self):
        from src.gui import logger
        if logger.strict_mode:
            return ""
        return "undefined"


class Boolean(ValueHolder):
    def __repr__(self):
        if self.value:
            return "#t"
        else:
            return "#f"


class String(ValueHolder):
    def __repr__(self):
        return "\"" + self.value + "\""


SingletonTrue = Boolean(True)
SingletonFalse = Boolean(False)

bools = [SingletonFalse, SingletonTrue]

Nil = NilType()
Undefined = UndefinedType()
