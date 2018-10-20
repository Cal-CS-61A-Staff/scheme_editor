from scheme_exceptions import ParseError

SPECIALS = ["(", ")", ".", "'"]

def get_input():
    out = []
    while True:
        x = input("> ")
        if x == 'X':
            return out
        out.append(x)


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
        for i, line in enumerate(lines):
            out = ""
            for real_line in line.split("\n"):
                out += real_line.split(";")[0]
            lines[i] = out
        self.string = " ".join(lines).strip()
        self.done = False
        self.next_token = None

    def get_next_token(self) -> str:
        if self.next_token is not None:
            return self.next_token
        curr = ""
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
                self.next_token = curr
                return curr

    def pop_next_token(self):
        out = self.get_next_token()
        self.next_token = None
        return out

    def get_next_char(self) -> str:
        if self.done:
            raise ParseError("Character buffer exhausted")
        return self.string[self.i]

    def pop_next_char(self) -> str:
        out = self.get_next_char()
        # print(f"Popping: '{out}'")

        self.i += 1

        if self.i == len(self.string):
            self.done = True

        return out