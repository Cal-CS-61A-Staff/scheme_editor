from functools import lru_cache
from typing import List, Tuple, Union, Sequence, Iterator

import lexer as lexer
from format_parser import get_expression, Formatted, FormatAtom, FormatList

LINE_LENGTH = 80
MAX_EXPR_COUNT = 10
MAX_EXPR_LEN = 50
INDENT = 4

DEFINE_VALS = ["define", "define-macro"]
DECLARE_VALS = ["lambda", "mu"]
SHORTHAND = {"quote": "'", "quasiquote": "`", "unquote": ",", "unquote-splicing": ",@", "variadic": "."}
MULTILINE_VALS = ["let", "cond"]

FREE_TOKENS = ["if", "define", "define-macro", "mu", "lambda"]


CACHE_SIZE = 2 ** 8


def prettify(strings: List[str]) -> str:
    out = []
    for i, string in enumerate(strings):
        if not string.strip():
            continue
        out.extend(prettify_single(string))

    return "\n\n".join(out)


@lru_cache(CACHE_SIZE)
def prettify_single(string: str) -> List[str]:
    out = []
    buff = lexer.TokenBuffer([string], True)
    while not buff.done:
        expr = get_expression(buff)
        out.append(prettify_expr(expr, LINE_LENGTH)[0])
    return out


def make_comments(comments: List[str], depth: int, newline: bool):
    if not comments:
        return ""
    if newline or len(comments) > 1:
        return "\n".join(";" + x for x in comments) + "\n"
    else:
        return " " + indent("\n".join(";" + x for x in comments), depth + 1).lstrip()


def to_count(phrase):
    while phrase and phrase[0] == "(":
        phrase = phrase[1:]
    while phrase and phrase[-1] == ")":
        phrase = phrase[:-1]
    return bool(phrase and not phrase.isdigit() and phrase.lower() not in FREE_TOKENS)


def verify(out: str, remaining: int) -> Tuple[str, bool]:
    total_length = max(map(len, out.split("\n"))) <= min(MAX_EXPR_LEN, remaining)
    expr_count = max(sum(to_count(y) for y in x.split()) for x in out.split("\n"))

    expr_length = expr_count <= MAX_EXPR_COUNT

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
    if isinstance(expr, FormatAtom):
        if len(expr.comments) <= 1:
            return verify(inline_format(expr) + make_comments(expr.comments, len(expr.value), False), remaining)
        else:
            return verify(make_comments(expr.comments, len(expr.value), True) + inline_format(expr), remaining)

    if expr.contents and not expr.contains_comment and not is_multiline(expr):
        expr_str = inline_format(expr)
        if verify(expr_str, remaining)[1]:
            out1 = expr_str + make_comments(expr.comments, len(expr_str), False)
            out2 = make_comments(expr.comments, len(expr_str), True) + expr_str
            if len(expr.comments) <= 1 and verify(out1, remaining)[1]:
                return verify(out1, remaining)
            elif verify(out2, remaining)[1]:
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
            if len(expr.comments) <= 1:
                return verify("()" + make_comments(expr.comments, 2, False), remaining)
            else:
                return verify(make_comments(expr.comments, 2, True) + "()", remaining)
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
                    else:
                        bindings = expr.contents[1]
                        if not isinstance(bindings, FormatList) or bindings.prefix:
                            log("let bindings incorrectly formatted")
                        else:
                            for binding in bindings.contents:
                                if isinstance(binding, FormatAtom) or len(binding.contents) != 2 or binding.prefix:
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

                if operator == "cond":
                    if len(expr.contents) < 2:
                        log("cond statement with too few arguments")
                    else:
                        clauses = expr.contents[1:]
                        for clause in clauses:
                            if not isinstance(clause, FormatList) \
                                    or clause.last is not None \
                                    or len(clause.contents) < 1\
                                    or clause.prefix:
                                log("screwed up clause")
                                break
                        else:
                            # cond expr looks ok
                            if all(len(clause.contents) == 2 for clause in clauses):
                                # fancy cond fmt
                                formatted_clauses = []
                                preds = []
                                for clause in clauses:
                                    preds.append(inline_format(clause.contents[0]))
                                max_pred = max(len(pred) for pred in preds)

                                for pred_fmt, clause in zip(preds, clauses):
                                    pred, val = clause.contents
                                    if pred.comments or pred.contains_comment or val.comments or val.contains_comment:
                                        break
                                    pred_str = pred_fmt
                                    val_str = inline_format(val)
                                    clause_str = "(" + pred_str + " " * (max_pred - len(pred_str) + 1) + val_str + ")"

                                    ok = False
                                    if len(clause.comments) > 1:
                                        clause_str = make_comments(clause.comments, 0, True) + clause_str
                                        ok = verify(clause_str, remaining - 1)[1]
                                    if not ok:
                                        clause_str = clause_str + make_comments(clause.comments, 0, False)

                                    formatted_clauses.append(clause_str)
                                else:
                                    # success!
                                    out_str = make_comments(expr.comments, 0, True) + \
                                              "(cond\n" + indent("\n".join(formatted_clauses), 1) + ")"
                                    out = verify(out_str, remaining)
                                    if out[1]:
                                        return out

                            formatted_clauses = []
                            for clause in clauses:
                                pred_str = prettify_expr(clause.contents[0], remaining - 1)[0]
                                val_strs = []
                                for expr in clause.contents[1:]:
                                    val_strs.append(prettify_expr(expr, remaining - 1)[0])
                                clause_str = "(" + pred_str + "\n" + \
                                             indent("\n".join(val_strs), 1)
                                if len(clause.contents) > 1 and clause.contents[-1].comments:
                                    clause_str += "\n"
                                clause_str += ")"
                                clause_str = make_comments(clause.comments, 0, True) + clause_str
                                formatted_clauses.append(clause_str)

                            out_str = "(cond\n" + indent("\n".join(formatted_clauses), 1) + ")"
                            return verify(make_comments(expr.comments, 0, True) + out_str, remaining)

                # assume no special forms
                # we can inline the first two elements
                operands = []
                for operand in expr.contents[1:]:
                    ret = prettify_expr(operand, remaining - len(operator) - 2)
                    # if not ret[1]:
                    #     break
                    operands.append(ret[0])
                else:
                    operand_string = indent(operands, len(operator) + 2)
                    out_str = "(" + operator + " " + operand_string.lstrip()
                    if expr.contents[-1].comments:
                        out_str += "\n"
                    out_str += ")"
                    out = verify(make_comments(expr.comments, 0, True) + out_str, remaining)
                    if out[1]:
                        return out
            # but may have to go here anyway, if inlining takes up too much space
            return prettify_data(expr, remaining, False)
    else:
        # poorly formed
        return prettify_data(expr, remaining, False)


def prettify_data(expr: Formatted, remaining: int, is_data: bool, force_multiline: bool=False) -> Tuple[str, bool]:
    print("Here", inline_format(expr))
    if isinstance(expr, FormatAtom):
        if len(expr.comments) <= 1:
            return verify(inline_format(expr) + make_comments(expr.comments, len(expr.value), False), remaining)
        else:
            return verify(make_comments(expr.comments, len(expr.value), True) + inline_format(expr), remaining)

    if is_data:
        callback = lambda *args: prettify_data(*args, is_data=True)
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
        if verify(expr_str, remaining)[1]:
            out1 = expr_str + make_comments(expr.comments, len(expr_str), False)
            out2 = make_comments(expr.comments, len(expr_str), True) + expr_str
            if len(expr.comments) <= 1 and verify(out1, remaining)[1]:
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
