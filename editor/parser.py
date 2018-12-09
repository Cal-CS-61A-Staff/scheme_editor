import sys
from typing import Union

from datamodel import Expression, Symbol, Number, Nil, SingletonTrue, SingletonFalse, String
from helper import make_list
from scheme_exceptions import ParseError
from lexer import TokenBuffer, SPECIALS


def tokenize(buffer: TokenBuffer):
    """
    >>> buff = TokenBuffer(["(1 (2 cat) (cat+dog-2 (5 6)  ) )"])
    >>> tokenize(buff)
    [(1 (2 cat) (cat+dog-2 (5 6)))]
    >>> buff = TokenBuffer(["(1 . 2)"])
    >>> tokenize(buff)
    [(1 . 2)]
    >>> buff = TokenBuffer(["(1 2 . 3)"])
    >>> tokenize(buff)
    [(1 2 . 3)]
    >>> buff = TokenBuffer(["1"])
    >>> tokenize(buff)
    [1]
    """
    out = []  # array of top-level elements to be executed sequentially
    while not buffer.done:
        out.append(get_expression(buffer))
        if out[-1] is None:
            out.pop()
    return out


def get_expression(buffer: TokenBuffer) -> Union[Expression, None]:
    token = buffer.pop_next_token()
    if token is None:
        return None
    if token in SPECIALS:
        if token == "(":
            return get_rest_of_list(buffer)
        elif token == "'":
            return make_list([Symbol("quote"), get_expression(buffer)])
        elif token == ",":
            if buffer.get_next_token() == "@":
                buffer.pop_next_token()
                return make_list([Symbol("unquote-splicing"), get_expression(buffer)])
            else:
                return make_list([Symbol("unquote"), get_expression(buffer)])
        elif token == "`":
            return make_list([Symbol("quasiquote"), get_expression(buffer)])
        elif token == "\"":
            return get_string(buffer)
        else:
            raise ParseError(f"Unexpected token: '{token}'")
    elif is_number(token.value):
        try:
            return Number(int(token))
        except ValueError:
            return Number(float(token))
    elif token == "#t" or token.value.lower() == "true":
        return SingletonTrue
    elif token == "#f" or token.value.lower() == "false":
        return SingletonFalse
    elif token == "nil":
        return Nil
    elif is_str(token.value):
        return Symbol(token.value.lower())
    else:
        raise ParseError(f"Unexpected token: '{token}'")


def get_string(buffer: TokenBuffer) -> String:
    out = []
    string = buffer.pop_next_token()
    escaping = False
    for char in string.value:
        if escaping:
            if char == "n":
                out.append("\n")
            else:
                out.append(char)
            escaping = False
        elif char == "\\":
            escaping = True
        else:
            out.append(char)
    if buffer.pop_next_token() != "\"":
        raise ParseError("String not terminated correctly!")
    return String("".join(out))


def get_rest_of_list(buffer: TokenBuffer) -> Expression:
    out = []
    last = Nil
    while True:
        next = buffer.get_next_token()
        if next == ")":
            buffer.pop_next_token()
            break
        elif next == ".":
            buffer.pop_next_token()
            last = get_expression(buffer)
            if buffer.pop_next_token() != ")":
                raise ParseError(f"Only one expression may follow a dot in a dotted list.")
            break
        expr = get_expression(buffer)
        out.append(expr)
    out = make_list(out, last)
    return out


def is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def is_str(token: str) -> bool:
    return True
