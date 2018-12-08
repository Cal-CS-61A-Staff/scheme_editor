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

    def __str__(self):
        if isinstance(self.first, Symbol):
            if isinstance(self.rest, Pair) and self.rest.rest == Nil:
                if self.first.value == "quote":
                    return f"'{str(self.rest.first)}"
                elif self.first.value == "unquote":
                    return f",{str(self.rest.first)}"
                elif self.first.value == "unquote-splicing":
                    return f",@{str(self.rest.first)}"
                elif self.first.value == "quasiquote":
                    return f"`{str(self.rest.first)}"

        if isinstance(self.rest, Pair):
            rest_str = str(self.rest)
            if rest_str[0] == "(" and rest_str[-1] == ")":
                return f"({self.first} {str(self.rest)[1:-1]})"
            else:
                return f"({self.first} . {str(self.rest)})"
        elif self.rest is Nil:
            return f"({self.first})"

        return f"({str(self.first)} . {str(self.rest)})"

    def __repr__(self):
        if isinstance(self.rest, Pair):
            return f"({repr(self.first)} {repr(self.rest)[1:-1]})"
        elif self.rest is Nil:
            return f"({repr(self.first)})"
        else:
            return f"({repr(self.first)} . {repr(self.rest)})"


class NilType(Expression):
    def __repr__(self):
        return "nil"


class UndefinedType(Expression):
    def __repr__(self):
        from gui import logger
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
    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        return "\"" + self.value + "\""


SingletonTrue = Boolean(True)
SingletonFalse = Boolean(False)

bools = [SingletonFalse, SingletonTrue]

Nil = NilType()
Undefined = UndefinedType()
