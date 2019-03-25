from typing import TYPE_CHECKING

from log_utils import get_id
from scheme_exceptions import TypeMismatchError

if TYPE_CHECKING:
    from evaluate_apply import Frame
    from log import Heap


class Expression:
    def __init__(self):
        self.id = get_id()


class ValueHolder(Expression):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return str(self.value)


class Symbol(ValueHolder):
    pass


class Number(ValueHolder):
    def __init__(self, value, *, force_float=False):
        super().__init__(value)
        if value == round(value) and not force_float:
            self.value = round(value)
        else:
            self.value = value

    def __repr__(self):
        return super().__repr__()


class Pair(Expression):
    def __init__(self, first: Expression, rest: Expression):
        import log
        super().__init__()
        self.first = first
        if not log.logger.dotted and not isinstance(rest, (Pair, NilType, Promise)):
            raise TypeMismatchError(
                f"Unable to construct a Pair with a cdr of {rest}, expected a Pair, Nil, or Promise.")
        self.rest = rest

    # def __str__(self):
    #     if isinstance(self.first, Symbol):
    #         if isinstance(self.rest, Pair) and self.rest.rest == Nil:
    #             if self.first.value == "quote":
    #                 return f"'{str(self.rest.first)}"
    #             elif self.first.value == "unquote":
    #                 return f",{str(self.rest.first)}"
    #             elif self.first.value == "unquote-splicing":
    #                 return f",@{str(self.rest.first)}"
    #             elif self.first.value == "quasiquote":
    #                 return f"`{str(self.rest.first)}"
    #
    #     if isinstance(self.rest, Pair):
    #         rest_str = str(self.rest)
    #         if rest_str[0] == "(" and rest_str[-1] == ")":
    #             return f"({self.first} {rest_str[1:-1]})"
    #         else:
    #             return f"({self.first} . {rest_str})"
    #     elif self.rest is Nil:
    #         return f"({self.first})"
    #
    #     return f"({str(self.first)} . {str(self.rest)})"

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
        from log import logger
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
        return "\"" + self.value.replace("\n", "\\n").replace("\"", "\\\"").replace("\'", "'") + "\""


class Promise(Expression):
    def __init__(self, expr: Expression, frame: 'Frame'):
        super().__init__()
        self.forced = False
        self.force_i = None
        self.expr = expr
        self.frame = frame
        self.targets = []

    def __repr__(self):
        return "#[promise]"

    def bind(self) -> 'Heap.HeapKey':
        import log
        if self.forced:
            target = ["promise", [self.force_i, log.logger.heap.record(self.expr)]]
        else:
            target = ["promise", [99999999999999, None]]
        self.targets.append(target)
        return target

    def force(self):
        import log
        self.forced = True
        self.force_i = log.logger.i
        for target in self.targets:
            target[:] = ["promise", [self.force_i, log.logger.heap.record(self.expr)]]
        log.logger.heap.modify(self.id)


SingletonTrue = Boolean(True)
SingletonFalse = Boolean(False)

bools = [SingletonFalse, SingletonTrue]

Nil = NilType()
Undefined = UndefinedType()
