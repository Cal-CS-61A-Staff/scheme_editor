from typing import Union

from scheme_exceptions import ParseError

SPECIALS = ["(", ")", ".", "'", "`", ",", "@", "\"", ";"]


def get_input():
    out = []
    while True:
        x = input("> ")
        if x == 'X':
            return out
        out.append(x)


class EndParen:
    def __eq__(self, other):
        return other == ")"

    def __hash__(self):
        return hash(")")

    def __repr__(self):
        return ")"


class TokenBuffer:
    """
    >>> buff = TokenBuffer(["(1 (2 cat) (cat+dog-2 (5 6)  ) )"])
    >>> buff.pop_next_token()
    '('
    >>> buff.pop_next_token()
    '1'
    >>> buff.pop_next_token()
    '('
    >>> buff.pop_next_token()
    '2'
    >>> buff.pop_next_token()
    'cat'
    >>> buff.pop_next_token()
    ')'
    >>> buff.pop_next_token()
    '('
    >>> buff.pop_next_token()
    'cat+dog-2'
    >>> buff.pop_next_token()
    '('
    >>> buff.pop_next_token()
    '5'
    >>> buff.pop_next_token()
    '6'
    >>> buff.pop_next_token()
    ')'
    >>> buff.pop_next_token()
    ')'
    >>> buff.pop_next_token()
    ')'
    >>> buff.pop_next_token()
    Traceback (most recent call last):
    ...
    scheme_exceptions.ParseError: Character buffer exhausted
    >>> buff = TokenBuffer(["1"])
    >>> buff.pop_next_token()
    '1'
    """

    def __init__(self, lines):
        self.i = 0
        self.string = "\n".join(lines).strip()
        self.done = False
        self.next_token = None
        self.in_string = False
        self.in_comment = False
        self.prev_paren = EndParen()  # TODO: temporary fix!

    def get_next_token(self) -> Union[str, EndParen, None]:
        if self.next_token is not None:
            return self.next_token
        curr = ""

        if self.in_comment:
            if self.in_string:
                raise ParseError("String not terminated before comment")
            while not self.done and self.get_next_char() != "\n":
                curr += self.pop_next_char()
            self.prev_paren.comment = curr
            self.in_comment = False
            if self.done:
                return None
            else:
                return self.get_next_token()

        if self.in_string and self.get_next_char() != "\"":
            while self.get_next_char() != "\n" and self.get_next_char() != "\"":
                curr += self.pop_next_char()
            if self.get_next_char() == "\n":
                raise ParseError("Multiline strings are not supported!")
            self.next_token = curr
            return curr

        while not self.done and self.get_next_char().isspace():
            self.pop_next_char()

        while True:
            next = self.get_next_char()
            if next.isspace():
                self.next_token = curr
                return curr
            elif curr and next in SPECIALS and next != ".":
                self.next_token = curr
                return curr
            curr += self.pop_next_char()
            # print(f"curr = '{curr}'")
            if curr in SPECIALS or self.done:
                if curr == ")":
                    self.prev_paren = EndParen()
                    curr = self.prev_paren
                self.next_token = curr
                if curr == "\"":
                    self.in_string ^= True
                if curr == ";":
                    self.in_comment = True
                    self.next_token = None
                    return self.get_next_token()
                return curr

    def pop_next_token(self):
        out = self.get_next_token()
        self.next_token = None
        return out

    def get_next_char(self) -> str:
        if self.done:
            raise ParseError("Incomplete expression, probably due to unmatched parentheses or quotes.")
        out = self.string[self.i]
        return out

    def pop_next_char(self) -> str:
        out = self.get_next_char()

        self.i += 1

        if self.i == len(self.string):
            self.done = True
        return out
