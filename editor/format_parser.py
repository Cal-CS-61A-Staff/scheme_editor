from typing import Union, List

from lexer import TokenBuffer, SPECIALS
from scheme_exceptions import ParseError


class FormatList:
    def __init__(self,
                 contents: List['Formatted'],
                 last: 'Formatted',
                 comments: List[str],
                 prefix: str=""):
        self.contents = contents
        self.last = last
        self.comments = comments
        self.contains_comment = any(x.contains_comment or x.comments for x in contents)
        self.prefix = prefix

    def __repr__(self):
        return str(self.__dict__)


class FormatAtom:
    def __init__(self, value: str, comments: List[str]=None):
        self.value = value
        self.comments = comments if comments else []
        self.contains_comment = False
        self.prefix = ""

    def __repr__(self):
        return str(self.__dict__)


Formatted = Union[FormatList, FormatAtom]


def get_expression(buffer: TokenBuffer) -> Formatted:
    token = buffer.pop_next_token()
    comments = []
    if token in SPECIALS:
        comments = token.comments
        if token == "(":
            out = get_rest_of_list(buffer)
        elif token in ("'", "`"):
            out = get_expression(buffer)
            out.prefix = token.value
        elif token == ",":
            if buffer.get_next_token() == "@":
                buffer.pop_next_token()
                out = get_expression(buffer)
                out.prefix = ",@"
            else:
                out = get_expression(buffer)
                out.prefix = token.value
        elif token == "\"":
            out = FormatAtom('"' + buffer.pop_next_token().value + '"')
            buffer.pop_next_token()
        else:
            raise ParseError(f"Unexpected token: '{token}'")

    else:
        if token.value.lower() == "true":
            token.value = "#t"
        elif token.value.lower() == "false":
            token.value = "#f"
        out = FormatAtom(token.value)

    out.comments = comments + buffer.tokens[buffer.i - 1].comments
    return out


def get_rest_of_list(buffer: TokenBuffer):
    out = []
    last = None
    while buffer.get_next_token() != ")" and buffer.get_next_token() != ".":
        out.append(get_expression(buffer))
    if buffer.get_next_token() == ".":
        buffer.pop_next_token()
        last = get_expression(buffer)
    if buffer.get_next_token() != ")":
        raise ParseError("Only one expression may follow a dot in a dotted list.")
    buffer.pop_next_token()
    return FormatList(out, last, [])