from typing import List, Tuple, Union, Sequence, Iterator

import lexer as lexer
from format_parser import get_expression, Formatted, FormatAtom, FormatList

LINE_LENGTH = 100
MAX_EXPR_LENGTH = 40
INDENT = 4

DEFINE_VALS = ["define", "define-macro"]
DECLARE_VALS = ["lambda", "mu"]
SHORTHAND = {"quote": "'", "quasiquote": "`", "unquote": ",", "unquote-splicing": ",@"}
MULTILINE_VALS = ["let", "cond"]


def prettify(strings: List[str]) -> str:
    out = []
    for i, string in enumerate(strings):
        if not string.strip():
            continue
        buff = lexer.TokenBuffer([string])
        while not buff.done:
            expr = get_expression(buff)
            print(expr)
            out.append(prettify_expr(expr, LINE_LENGTH)[0])

    return "\n\n".join(out)


def make_comments(comments: List[str], depth: int, newline: bool):
    if not comments:
        return ""
    if newline:
        return "\n".join(";" + x for x in comments) + "\n"
    else:
        return " " + indent("\n".join(";" + x for x in comments), depth + 1).lstrip()


def verify(out: str, remaining: int) -> Tuple[str, bool]:
    total_length = max(map(len, out.split("\n"))) <= remaining
    expr_length = max(len(x.strip()) for x in out.split("\n")) <= MAX_EXPR_LENGTH
    return out, total_length and expr_length


def is_multiline(expr: Formatted):
    if isinstance(expr, FormatList):
        return any(map(is_multiline, expr.contents))
    return expr.value in MULTILINE_VALS


def inline_format(expr: Formatted) -> str:
    if isinstance(expr, FormatAtom):
        return expr.prefix + expr.value
    else:
        out = expr.prefix + "(" + " ".join(inline_format(elem) for elem in expr.contents)
        if expr.last:
            return out + " . " + inline_format(expr.last) + ")"
        else:
            return out + ")"


def log(message: str):
    print(message)


def prettify_expr(expr: Formatted, remaining: int) -> Tuple[str, bool]:
    print(inline_format(expr))

    if isinstance(expr, FormatAtom):
        return verify(inline_format(expr) + make_comments(expr.comments, len(expr.value), False), remaining)

    if expr.contents and not expr.contains_comment and not is_multiline(expr):
        expr_str = inline_format(expr)
        if len(expr_str) < min(MAX_EXPR_LENGTH, remaining):
            out1 = expr_str + make_comments(expr.comments, len(expr_str), False)
            out2 = make_comments(expr.comments, len(expr_str), True) + expr_str
            if verify(out1, remaining)[1]:
                return verify(out1, remaining)
            else:
                return verify(out2, remaining)

    if expr.last is None:
        # well formed
        if expr.prefix:
            # quoted or something
            old_prefix = expr.prefix
            comments, expr.comments = expr.comments, ""
            expr.prefix = ""
            if old_prefix == "`":
                out = verify(make_comments(comments, 0, True) + old_prefix + indent(prettify_expr(expr, remaining - 1)[0], 1).strip(), remaining)
            else:
                out = verify(make_comments(comments, 0, True) + old_prefix + indent(prettify_data(expr, remaining - 1, True)[0], 1).strip(), remaining)
            expr.prefix = old_prefix
            expr.comments = comments
            return out
        elif not expr.contents:
            # nil expr
            return verify("()" + make_comments(expr.comments, 2, False), remaining)
        else:
            # call expr
            if isinstance(expr.contents[0], FormatAtom) \
                    and not expr.contents[0].comments\
                    and not expr.contents[0].prefix:

                operator = expr.contents[0].value
                if operator in DEFINE_VALS:
                    if len(expr.contents) < 3:
                        log("define statement with too few arguments")
                    else:
                        name = expr.contents[1]
                        body = []
                        for body_expr in expr.contents[2:]:
                            body.append(prettify_expr(body_expr, remaining - 2)[0])
                        name_str = indent(prettify_expr(name, remaining - len(f"({operator} "))[0],
                                          len(f"({operator} "))
                        body_str = indent("\n".join(body), INDENT // 2)
                        out_str = "(" + operator + " " + name_str.lstrip() + "\n" + body_str + ")"
                        return verify(make_comments(expr.comments, 0, True) + out_str, remaining)

                if operator == "let":
                    if len(expr.contents) < 3:
                        log("let statement with too few arguments")
                    bindings = expr.contents[1]
                    if not isinstance(bindings, FormatList):
                        log("let bindings incorrectly formatted")
                    else:
                        for binding in bindings.contents:
                            if isinstance(binding, FormatAtom) or len(binding.contents) != 2:
                                log("binding with incorrect number of elements")
                                break
                        else:
                            # let is well-formed (bearing in mind unquotes can change things)
                            binding_str = prettify_data(bindings, remaining - len("(let "), False, True)[0]
                            binding_str = indent(binding_str, len("(let "))
                            body = []
                            for body_expr in expr.contents[2:]:
                                body.append(prettify_expr(body_expr, remaining - INDENT // 2)[0])
                            body_string = indent(body, INDENT // 2)
                            out_str = "(let " + binding_str.lstrip() + "\n" + body_string
                            if expr.contents[-1].comments:
                                out_str += "\n"
                            out_str += ")"
                            return verify(make_comments(expr.comments, 0, True) + out_str, remaining)

                # assume no special forms
                # we can inline the first two elements
                operands = []
                for operand in expr.contents[1:]:
                    ret = prettify_expr(operand, remaining - len(operator) - 2)
                    if not ret[1]:
                        break
                    operands.append(ret[0])
                else:
                    if not operands or len(operator) + len(operands[0]) < min(remaining, MAX_EXPR_LENGTH):
                        # successfully loaded operands
                        operand_string = indent(operands, len(operator) + 2)
                        out_str = "(" + operator + " " + operand_string.lstrip()
                        if expr.contents[-1].comments:
                            out_str += "\n"
                        out_str += ")"
                        return verify(make_comments(expr.comments, 0, True) + out_str, remaining)
            # but may have to go here anyway, if inlining takes up too much space
            return prettify_data(expr, remaining, False)
    else:
        # poorly formed
        return prettify_data(expr, remaining, False)


def prettify_data(expr: Formatted, remaining: int, is_data: bool, force_multiline: bool=False) -> Tuple[str, bool]:
    if isinstance(expr, FormatAtom):
        return verify(inline_format(expr) + make_comments(expr.comments, len(expr.value), False), remaining)

    if is_data:
        callback = lambda *args : prettify_data(*args, is_data=True)
    else:
        callback = prettify_expr

    if expr.prefix:
        old_prefix = expr.prefix
        expr.prefix = ""
        out = verify(old_prefix + indent(callback(expr, remaining - 1)[0], 1).strip(), remaining)
        expr.prefix = old_prefix
        return out

    if not force_multiline and expr.contents and not expr.contains_comment:
        expr_str = inline_format(expr)
        if len(expr_str) < MAX_EXPR_LENGTH:
            out1 = expr_str + make_comments(expr.comments, len(expr_str), False)
            out2 = make_comments(expr.comments, len(expr_str), True) + expr_str
            if verify(out1, remaining)[1]:
                return verify(out1, remaining)
            else:
                return verify(out2, remaining)

    elems = []
    for elem in expr.contents:
        ret = callback(elem, remaining - 1)
        elems.append(ret[0])

    elem_string = indent("\n".join(elems), 1).strip()
    out_str = "(" + elem_string
    if expr.contents and expr.contents[-1].comments:
        out_str += "\n"
    out_str += ")"
    return verify(make_comments(expr.comments, 0, True) + out_str, remaining)


def indent(lines: Union[Iterator, str], depth) -> str:
    if not isinstance(lines, str):
        lines = "\n".join(lines)
    return " " * depth + lines.rstrip().replace("\n", "\n" + " " * depth)


def count_lines(lines: Sequence[str]) -> int:
    return sum(x.count("\n") for x in lines)
