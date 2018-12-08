from typing import List, Tuple, Union, Sequence, Iterator

import lexer as lexer
from datamodel import Expression, Pair, Symbol, Nil
from helper import pair_to_list
from parser import get_expression
from scheme_exceptions import SchemeError

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
            out.append(prettify_expr(expr, LINE_LENGTH)[0])

    return "\n\n".join(out)


def prettify_expr(expr: Expression, remaining: int) -> Tuple[str, bool]:
    print("Print:", expr)
    if not isinstance(expr, Pair) or (len(str(expr)) < min(MAX_EXPR_LENGTH, remaining)
                                      and (not isinstance(expr.first, Symbol)
                                           or not (expr.first.value in MULTILINE_VALS or
                                                   expr.first.value in SHORTHAND))):
        return str(expr), remaining > 0
    first, rest = expr.first, expr.rest
    try:
        if isinstance(first, Symbol):
            try:
                if first.value in DEFINE_VALS:
                    prettified = [*zip(*(prettify_expr(arg, remaining - INDENT // 2) for arg in pair_to_list(rest.rest)))]
                    if not prettified:
                        prettified = [[], []]
                    return "(" + first.value + " " + str(rest.first) + "\n" \
                           + indent(prettified[0], INDENT // 2) + ")", all(prettified[1])

                elif first.value == "if":
                    space = remaining - len(first.value) - 3  # subtracting the brackets, symbol, and first space
                    prettified_no_newline = [*zip(*(prettify_expr(arg, space) for arg in pair_to_list(rest)))]
                    if not prettified_no_newline:
                        prettified_no_newline = [[], []]
                    return "(" + first.value + " " + indent(prettified_no_newline[0], len(first.value) + 2).lstrip() + ")", \
                           all(prettified_no_newline[1])

                elif first.value == "cond":
                    clauses = pair_to_list(rest)
                    clause_list = [pair_to_list(clause) for clause in clauses]
                    if max(len(str(clause)) for clause in clauses) <= min(remaining - INDENT // 2, MAX_EXPR_LENGTH):
                        if all(len(clause) == 2 for clause in clause_list):
                            out = ["(cond"]
                            depth = max(len(str(pred)) for pred, expr in clause_list)
                            for pred, expr in clause_list:
                                out.append("\n" + " " * (INDENT // 2) + "(" + str(pred) + " ")
                                out.append(" " * (depth - len(str(pred))))
                                out.append(str(expr) + ")")
                            return "".join(out) + ")", True
                    out = ["(cond"]
                    for pred, *exprs in clause_list:
                        out.append("\n" + " " * (INDENT // 2) + "(" +
                                   indent(prettify_expr(pred, remaining - INDENT // 2 - 1)[0], INDENT // 2).lstrip())
                        for expr in exprs:
                            out.append("\n")
                            out.append(indent(prettify_expr(expr, remaining - INDENT // 2 - 1)[0], INDENT // 2 + 1))
                        out.append(")")
                    return "".join(out) + ")", True

                elif first.value == "let":
                    bindings = rest.first
                    bindings_list = [pair_to_list(binding) for binding in pair_to_list(bindings)]
                    out = ["(let ("]
                    for var, expr in bindings_list:
                        out.append("(" + str(var) + " " +
                                   indent(prettify_expr(expr, remaining - 9 - len(str(var)))[0],
                                          8 + len(str(var))).lstrip()
                                   + ")\n" + " " * 6)
                    if bindings_list:
                        out[-1] = out[-1][:-7]
                    out.append(")")
                    exprs = pair_to_list(rest.rest)
                    for expr in exprs:
                        out.append("\n")
                        out.append(indent(prettify_expr(expr, remaining - INDENT // 2)[0], INDENT // 2))
                    out.append(")")
                    return "".join(out), True

                # elif first.value in DECLARE_VALS:
                #     return str(expr), remaining > 0
                elif first.value in SHORTHAND:
                    if rest.rest is Nil:
                        if first.value == "quote":
                            ret = prettify_data(rest.first, remaining - 1)
                        else:
                            ret = prettify_expr(rest.first, remaining - 1)
                        return SHORTHAND[first.value] + indent(ret[0], 1).lstrip(), ret[1]
            except SchemeError:
                print(f"Poorly formed {first.value} expression - printing in debug configuration")

            if len(str(expr)) < min(MAX_EXPR_LENGTH, remaining):
                return str(expr), True

            space = remaining - len(first.value) - 3  # subtracting the brackets, symbol, and first space
            prettified_no_newline = [*zip(*(prettify_expr(arg, space) for arg in pair_to_list(rest)))]
            if not prettified_no_newline:
                prettified_no_newline = [[], []]
            prettified_newline = [*zip(*(prettify_expr(arg, remaining - INDENT // 2 - 1)
                                         for arg in pair_to_list(rest)))]
            if not prettified_newline:
                prettified_newline = [[], []]

            if all(prettified_no_newline[1]) and lines(prettified_no_newline) <= 1 + lines(prettified_newline):
                return "(" + first.value + " " + indent(prettified_no_newline[0], len(first.value) + 2).lstrip() + ")", True
            else:
                return "(" + first.value + "\n" + indent(prettified_newline[0], INDENT // 2) + ")", \
                       all(prettified_newline[1])
        else:
            return prettify_data(expr, remaining)
    except SchemeError:
        print("Poorly formed Scheme list - printing in data configuration")
        return prettify_data(expr, remaining)


def prettify_data(expr: Expression, remaining: int):
    print("Dataprint:", expr)
    if not isinstance(expr, Pair) or len(str(expr)) < remaining:
        return str(expr), remaining > 0

    try:
        args = pair_to_list(expr)
        prettified = list(zip(*(prettify_expr(arg, remaining - 1) for arg in args)))
        if not prettified:
            prettified = [[], []]
        return "(" + indent(prettified[0], 1)[1:] + ")", all(prettified[1])
    except SchemeError:
        # manually recover elements of ill-formed list
        pos = expr
        args = []
        while isinstance(pos, Pair):
            args.append(pos.first)
            pos = pos.rest
        prettified = list(zip(*(prettify_expr(arg, remaining - 1) for arg in args)))
        if not prettified:
            prettified = [[], []]
        return "(" + indent(prettified[0], 1)[1:] + "\n" + " . " + indent(prettify_data(pos, remaining - 1)[0], 3).lstrip() + ")",\
               all(prettified[1])


def indent(lines: Union[Iterator, str], depth) -> str:
    if not isinstance(lines, str):
        lines = "\n".join(lines)
    return " " * depth + lines.rstrip().replace("\n", "\n" + " " * depth)


def lines(lines: Sequence[str]) -> int:
    return sum(x.count("\n") for x in lines)
