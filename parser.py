from datamodel import Expression, Symbol, Number, Nil
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
    return out


def get_expression(buffer: TokenBuffer) -> Expression:
    token = buffer.pop_next_token()
    if token in SPECIALS:
        if token == "(":
            return get_rest_of_list(buffer)
        elif token == "'":
            return make_list([Symbol("quote"), get_expression(buffer)])
        else:
            raise ParseError(f"Unexpected token: '{token}'")
    elif is_number(token):
        return Number(float(token))
    elif is_str(token):
        return Symbol(token)
    else:
        raise ParseError(f"Unexpected token: '{token}'")


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
            buffer.pop_next_token()
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