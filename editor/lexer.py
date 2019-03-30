from typing import Union, List

from scheme_exceptions import ParseError

SPECIALS = ["(", ")", "'", "`", ",", "@", "\"", ";"]


class Token:
    def __init__(self, value: str):
        self.value = value
        self.comments: List[str] = []

    def __eq__(self, other):
        return other == self.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class TokenBuffer:
    def __init__(self, lines, do_comments=False):
        self.string = "\n".join(lines)
        self.tokens = tokenize(self.string, do_comments)
        self.done = not self.tokens
        self.i = 0

    def get_next_token(self) -> Token:
        if self.done:
            raise ParseError("Incomplete expression, probably due to unmatched parentheses.")
        return self.tokens[self.i]

    def pop_next_token(self) -> Token:
        out = self.get_next_token()
        self.i += 1
        if self.i == len(self.tokens):
            self.done = True
        return out


def tokenize(string, do_comments) -> List[Token]:
    string = string.strip()
    tokens = []
    comments = {}
    i = 0
    first_in_line = True
    prev_newline = True

    def _get_token():
        """Always starts at a non-space character"""
        nonlocal i, first_in_line, prev_newline
        if i == len(string):
            return
        if string[i] == "\"":
            first_in_line = False
            prev_newline = False
            tokens.append(Token(string[i]))
            i += 1
            _get_string()
            return

        elif string[i] == ";":
            i += 1
            _get_comment()

        elif string[i] in SPECIALS:
            first_in_line = False
            prev_newline = False
            tokens.append(Token(string[i]))
            i += 1

        else:
            curr = ""
            while i != len(string) and not string[i].isspace() and string[i] not in SPECIALS:
                curr += string[i]
                i += 1
            if curr:
                first_in_line = False
                prev_newline = False
                tokens.append(Token(curr))

    def _get_comment():
        nonlocal i
        curr = ""
        while i != len(string) and string[i] != "\n":
            curr += string[i]
            i += 1
        if first_in_line:
            if len(tokens) not in comments:
                comments[len(tokens)] = []
            comments[len(tokens)].append(curr)
        else:
            if len(tokens) - 1 not in comments:
                comments[len(tokens) - 1] = []
            comments[len(tokens) - 1].append(curr)

    def _get_string():
        """Starts just after an opening quotation mark"""
        nonlocal i
        curr = ""
        while i != len(string) and string[i] != "\"":
            char = string[i]
            if char == "\n":
                raise ParseError("Multiline strings not supported!")
            if char == "\\":
                curr += char
                if i + 1 == len(string):
                    raise ParseError("String not terminated correctly (try escaping the backslash?)")
                curr += string[i + 1]
                i += 2
            else:
                curr += string[i]
                i += 1
        tokens.append(Token(curr))
        if i == len(string):
            raise ParseError("String missing a closing quote")
        tokens.append(Token(string[i]))
        i += 1

    while i != len(string):
        _get_token()
        while i != len(string) and string[i].isspace():
            if string[i] == "\n" and i and prev_newline:
                first_in_line = True
            elif string[i] == "\n":
                prev_newline = True
            i += 1

    if do_comments:
        for key, val in comments.items():
            tokens[min(key, len(tokens) - 1)].comments.extend(val)

    return tokens
