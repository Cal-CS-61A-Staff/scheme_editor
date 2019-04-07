from abc import ABC
from functools import lru_cache
from typing import List, Tuple, Union, Sequence, Iterator, Type

import lexer as lexer
from format_parser import get_expression, Formatted, FormatAtom, FormatList, FormatComment

LINE_LENGTH = 80
MAX_EXPR_COUNT = 10
MAX_EXPR_LEN = 30
INDENT = 4

DEFINE_VALS = ["define", "define-macro"]
DECLARE_VALS = ["lambda", "mu"]
SHORTHAND = {"quote": "'", "quasiquote": "`", "unquote": ",", "unquote-splicing": ",@", "variadic": "."}
MULTILINE_VALS = ["let", "cond", "if"]

FREE_TOKENS = ["if", "define", "define-macro", "mu", "lambda"]

OPEN_PARENS = ["(", "["]
CLOSE_PARENS = [")", "]"]

CACHE_SIZE = 2 ** 8


def prettify(strings: List[str], javastyle: bool=False) -> str:
    out = []
    for i, string in enumerate(strings):
        if not string.strip():
            continue
        out.extend(prettify_single(string, javastyle))

    return "\n\n".join(out)


@lru_cache(CACHE_SIZE)
def prettify_single(string: str, javastyle: bool) -> List[str]:
    global java_newline
    if javastyle:
        java_newline = "\n"
    else:
        java_newline = ""
    out = []
    buff = lexer.TokenBuffer([string], True)
    while not buff.done:
        expr = get_expression(buff)
        out.append(ExpressionFormatter.format(expr, LINE_LENGTH))
    return out


class OptimalFormattingReached(Exception):
    pass


class MatchFailure(Exception):
    pass


class WeakMatchFailure(MatchFailure):
    pass


class StrongMatchFailure(MatchFailure):
    ...


class Formatter(ABC):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> str:
        raise NotImplementedError()


class SpecialFormFormatter(Formatter, ABC):
    @staticmethod
    def match_form(expr: Formatted, form: str):
        if not isinstance(expr, FormatList):
            raise WeakMatchFailure("Special form must be list, not atom.")
        if not expr.contents:
            raise WeakMatchFailure("Special form must be list, not nil.")
        if not isinstance(expr.contents[0], FormatAtom):
            raise WeakMatchFailure("Special form must begin with a Symbol.")
        if not expr.contents[0] == form:
            raise WeakMatchFailure("Call expression does not match desired special form.")
        # if expr.last:
        #     raise StrongMatchFailure("Special form must not be dotted.")


# class CondFormatter(SpecialFormFormatter):
#     class MultilineCondClause(Formatter):
#         ...
#
#     class AlignedCondClause(Formatter):
#         ...
#
#     @classmethod
#     def format(cls, expr: Formatted) -> str:
#         cls.match_form(expr, "cond")
#         for clause in expr.contents[1:]:


class AtomFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int=None) -> str:
        if not isinstance(expr, FormatAtom):
            raise WeakMatchFailure("expr is not atomic")
        return expr.prefix + expr.value


class InlineFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int=None) -> str:
        if isinstance(expr, FormatComment):
            raise WeakMatchFailure("Cannot inline-format a comment")
        elif isinstance(expr, FormatAtom):
            return AtomFormatter.format(expr, remaining)
        else:
            formatted_exprs = []
            for expr in expr.contents:
                formatted_exprs.append(InlineFormatter.format(expr))
            return expr.open_paren + " ".join(formatted_exprs) + expr.close_paren


class ListFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> str:
        if not isinstance(expr, FormatList):
            raise WeakMatchFailure("expr is not a list")


class CommentFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int=None) -> str:
        if not isinstance(expr, FormatComment):
            raise WeakMatchFailure("expr is not a comment")
        return ";" + expr.value


class ExpressionFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> str:
        candidates = [AtomFormatter, ListFormatter, CommentFormatter]
        return find_best(expr, candidates, remaining)


class Best:
    def __init__(self, remaining):
        self.curr_best = None
        self.curr_cost = None
        self.remaining = remaining

    @staticmethod
    def heuristic(string: str) -> int:
        return 5  # TODO: ACTUALLY IMPLEMENT

    def add(self, formatted: str):
        cost = self.heuristic(formatted)
        if self.curr_cost is None or cost < self.curr_cost:
            self.curr_best = formatted
            self.curr_cost = 0
            if cost == 0:
                raise OptimalFormattingReached()

    def get_best(self):
        if self.curr_best is None:
            raise Exception("Error!!!")
        return self.curr_best


def find_best(raw: Formatted, candidates: List[Type[Formatter]], remaining):
    best = Best(remaining)
    for candidate in candidates:
        try:
            best.add(candidate.format(raw, remaining))
        except WeakMatchFailure:
            continue
        except StrongMatchFailure:
            # TODO: Warn about potentially invalid special form
            continue
        except OptimalFormattingReached:
            return best.get_best()
    return best.get_best()


def indent(lines: Union[Iterator, str], depth) -> str:
    if not isinstance(lines, str):
        lines = "\n".join(lines)
    return " " * depth + lines.rstrip().replace("\n", "\n" + " " * depth)


def count_lines(lines: Sequence[str]) -> int:
    return sum(x.count("\n") for x in lines)
