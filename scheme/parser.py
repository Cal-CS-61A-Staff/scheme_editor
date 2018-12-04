import sys

from scheme.datamodel import Expression, Symbol, Number, Nil, SingletonTrue, SingletonFalse, String
from scheme.helper import make_list
from scheme.scheme_exceptions import ParseError
from scheme.lexer import TokenBuffer, SPECIALS


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
    return out


def get_expression(buffer: TokenBuffer) -> Expression:
    token = buffer.pop_next_token()
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
        elif token == "\\":
            raise ParseError("Symbols with backslashes aren't yet supported! Pick a better naming convention :P")
        else:
            raise ParseError(f"Unexpected token: '{token}'")
    elif is_number(token):
        token = str(token)  # for okpy tests
        try:
            return Number(int(token))
        except ValueError:
            return Number(float(token))
    elif token == "#t" or token.lower() == "true":
        return SingletonTrue
    elif token == "#f" or token.lower() == "false":
        return SingletonFalse
    elif token == "nil":
        return Nil
    elif is_str(token):
        return Symbol(token.lower())
    else:
        raise ParseError(f"Unexpected token: '{token}'")


def get_string(buffer: TokenBuffer) -> String:
    out = []
    while True:
        token = buffer.pop_next_token()
        if token == "\"":
            return String("".join(out))
        elif token == "\\":
            escaped = buffer.pop_next_token()
            if escaped == "n":
                out.append("\n")
            else:
                out.append(escaped)
        else:
            out.append(token)


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
        out.append(get_expression(buffer))
    return make_list(out, last)


def is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def is_str(token: str) -> bool:
    return True