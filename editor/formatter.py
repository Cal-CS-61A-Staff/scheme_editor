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


def prettify(strings: List[str], javastyle: bool = False) -> str:
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
        out.append(ExpressionFormatter.format(expr, LINE_LENGTH).stringify())
    return out


class OptimalFormattingReached(Exception):
    pass


class MatchFailure(Exception):
    pass


class WeakMatchFailure(MatchFailure):
    pass


class StrongMatchFailure(MatchFailure):
    ...


class FormatSeq:
    def __init__(self):
        self.left: FormatOp = None
        self.right: FormatOp = None
        self.active = True
        self.line_lengths = [0]
        self.max_line_len = 0

    def __add__(self, other):
        if other is None:
            return self
        if isinstance(other, FormatSeq):
            return other.__radd__(self)
        return NotImplemented

    def __radd__(self, other: 'FormatSeq'):
        if other is None:
            return self
        if not other.active:
            raise Exception("Attempting to manipulate inactive seqs!")
        if not self.active:
            raise Exception("???")
        other.right.next = self.left
        other.active = False
        self.left = other.left
        self.line_lengths[0] += other.line_lengths.pop()
        self.line_lengths = other.line_lengths + self.line_lengths
        self.max_line_len = max(self.line_lengths)
        if len(self.line_lengths) > 1:
            self.line_lengths = [self.line_lengths[0], self.line_lengths[-1]]
        return self

    def contains_newline(self):
        return len(self.line_lengths) > 1

    def stringify(self):
        pos = self.left
        out = []
        indent_level = 0
        while pos is not None:
            if isinstance(pos, _Token):
                out.append(pos.value)
                if pos.value == "\n":
                    out.append(" " * indent_level)
            elif isinstance(pos, _ChangeIndent):
                indent_level += pos.level
            else:
                raise NotImplementedError("unable to stringify " + str(type(pos)))
            pos = pos.next
        return "".join(out)


class FormatOp:
    def __init__(self):
        self.next = None


class _Token(FormatOp):
    def __init__(self, value):
        super().__init__()
        assert isinstance(value, str)
        self.value = value


class Token(FormatSeq):
    def __init__(self, value):
        super().__init__()
        self.left = self.right = _Token(value)
        self.max_line_len = self.line_lengths[0] = len(value)


class _ChangeIndent(FormatOp):
    def __init__(self, level):
        super().__init__()
        self.level = level


class ChangeIndent(FormatSeq):
    def __init__(self, level):
        super().__init__()
        self.left = self.right = _ChangeIndent(level)


class Newline(Token):
    def __init__(self):
        super().__init__("\n")
        self.max_line_len = self.line_lengths[0] = 0
        self.line_lengths.append(0)


class Space(Token):
    def __init__(self):
        super().__init__(" ")


class Formatter(ABC):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> FormatSeq:
        raise NotImplementedError()


class SpecialFormFormatter:
    @staticmethod
    def assert_form(expr: Formatted, form: str):
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

    @classmethod
    def match_form(cls, expr: Formatted, form: str):
        try:
            cls.assert_form(expr, form)
        except WeakMatchFailure:
            return False
        else:
            return True

    @classmethod
    def is_multiline(cls, expr: Formatted):
        return any(cls.match_form(expr, form) for form in MULTILINE_VALS)


# class CondFormatter(SpecialFormFormatter):
#     class MultilineCondClause(Formatter):
#         ...
#
#     class AlignedCondClause(Formatter):
#         ...
#
#     @classmethod
#     def format(cls, expr: Formatted) -> str:
#         cls.assert_form(expr, "cond")
#         for clause in expr.contents[1:]:


class AtomFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int = None) -> FormatSeq:
        if not isinstance(expr, FormatAtom):
            raise WeakMatchFailure("expr is not atomic")
        return Token(expr.prefix + expr.value)


class InlineFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int = None) -> FormatSeq:
        if isinstance(expr, FormatComment):
            raise WeakMatchFailure("Cannot inline-format a comment")
        if isinstance(expr, FormatAtom):
            return AtomFormatter.format(expr, remaining)
        if SpecialFormFormatter.is_multiline(expr):
            raise WeakMatchFailure("Cannot inline-format a multiline expr")

        formatted_exprs = [InlineFormatter.format(elem) for elem in expr.contents]

        out = Token(expr.prefix) + Token(expr.open_paren)
        for formatted_expr in formatted_exprs:
            out += formatted_expr
            if formatted_expr is not formatted_exprs[-1]:
                out += Space()
        out += Token(expr.close_paren)
        return out


class ListFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> FormatSeq:
        if not isinstance(expr, FormatList):
            raise WeakMatchFailure("expr is not a list")
        return find_best(expr, [InlineFormatter, PrefixedListFormatter, CallExprFormatter, DataListFormatter],
                         remaining)


class CallExprFormatter(Formatter):
    @staticmethod
    def format(expr: FormatList, remaining: int) -> FormatSeq:
        assert isinstance(expr, FormatList)
        if len(expr.contents) <= 2:
            raise WeakMatchFailure("Call expr must have at least 3 arguments, otherwise handle using DataListFormatter")
        if expr.prefix:
            raise WeakMatchFailure("Call expr cannot be prefixed")
        if not isinstance(expr.contents[0], FormatAtom) or isinstance(expr.contents[1], FormatComment):
            raise WeakMatchFailure("Unable to inline first two arguments, fallback to DataListFormatter")
        return find_best(expr, [
            # LetExprFormatter, CondExprFormatter,
            DefaultCallExprFormatter], remaining)


class PrefixedListFormatter(Formatter):
    @staticmethod
    def format(expr: FormatList, remaining: int):
        assert isinstance(expr, FormatList)
        if not expr.prefix:
            raise WeakMatchFailure("Expr is not prefixed")
        with expr.hold_prefix() as prefix:
            if prefix == "`":
                ret = ListFormatter.format(expr, remaining - 1)
            else:
                ret = DataListFormatter.format(expr, remaining - 1)
        return Token(prefix) + ChangeIndent(1) + ret + ChangeIndent(-1)


class DefaultCallExprFormatter(Formatter):
    @staticmethod
    def format(expr: FormatList, remaining: int) -> FormatSeq:
        operator = expr.contents[0]
        firstarg = expr.contents[1]

        assert isinstance(operator, FormatAtom)
        assert not isinstance(operator, FormatComment)

        indent_level = len(operator.value) + 2
        out = Token(expr.open_paren)
        out += AtomFormatter.format(operator)
        out += ChangeIndent(indent_level) + Space()
        out += ExpressionFormatter.format(firstarg, remaining - indent_level) + Newline()

        rest, trailing_paren_safe = rest_format(expr.contents[2:], remaining - indent_level)

        out += rest
        if not trailing_paren_safe:
            out += Newline()
        out += ChangeIndent(-indent_level)
        out += Token(expr.close_paren)

        return out


class DataListFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> FormatSeq:
        if expr.prefix:
            raise WeakMatchFailure("Cannot format prefixed datalist")
        out = Token(expr.open_paren) + ChangeIndent(1)
        rest, trailing_paren_safe = rest_format(expr.contents, remaining - 1)
        out += rest
        if not trailing_paren_safe:
            out += Newline()
        out += ChangeIndent(-1) + Token(expr.close_paren)
        return out


class CommentFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int = None) -> FormatSeq:
        if not isinstance(expr, FormatComment):
            raise WeakMatchFailure("Expr is not a comment")
        return Token(";" + expr.value)


class ExpressionFormatter(Formatter):
    @staticmethod
    def format(expr: Formatted, remaining: int) -> FormatSeq:
        candidates = [AtomFormatter, ListFormatter, CommentFormatter]
        return find_best(expr, candidates, remaining)


class Best:
    def __init__(self, remaining):
        self.curr_best = None
        self.curr_cost = None
        self.remaining = remaining

    @staticmethod
    def heuristic(chain: FormatSeq) -> int:
        return chain.max_line_len

    def add(self, formatted: FormatSeq):
        cost = self.heuristic(formatted)
        if self.curr_cost is None or cost < self.curr_cost:
            self.curr_best = formatted
            self.curr_cost = cost
            if cost == 0:
                raise OptimalFormattingReached()

    def get_best(self) -> FormatSeq:
        if self.curr_best is None:
            raise Exception("No candidates found")
        return self.curr_best


def find_best(raw: Formatted, candidates: List[Type[Formatter]], remaining) -> FormatSeq:
    best = Best(remaining)
    for candidate in candidates:
        try:
            print(" " * (80 - remaining), "candidate", candidate, raw)
            best.add(candidate.format(raw, remaining))
            print(" " * (80 - remaining), "success", candidate)
        except WeakMatchFailure as e:
            print(" " * (80 - remaining), str(e), candidate)
            continue
        except StrongMatchFailure:
            print("err")
            raise
            # TODO: Warn about potentially invalid special form
            continue
        except OptimalFormattingReached:
            print("cat")
            return best.get_best()
    return best.get_best()


def rest_format(exprs: List[Formatted], remaining: int) -> Tuple[FormatSeq, bool]:
    out = None
    i = 0

    while i != len(exprs):
        curr_expr = exprs[i]
        i += 1
        if i != len(exprs) and isinstance(exprs[i], FormatComment):
            inline_comment = exprs[i]
            i += 1
        else:
            inline_comment = ""
        formatted_expr = ExpressionFormatter.format(curr_expr, remaining)
        if not formatted_expr.contains_newline() and inline_comment:
            formatted_expr += Space() + CommentFormatter.format(inline_comment)
        out += formatted_expr if i == len(exprs) else formatted_expr + Newline()
    ends_with_comment = exprs and isinstance(exprs[-1], FormatComment)
    return out, not ends_with_comment
