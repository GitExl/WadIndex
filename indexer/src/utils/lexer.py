"""
Heavily modified version of https://gist.github.com/eliben/5797351 by
Eli Bendersky (eliben@gmail.com).
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Pattern, Tuple


class TokenTypeBase(Enum):
    """ Base class for token type values.
    """
    pass


# A token as returned from get_token().
# type, contents, position, lexer object
Token = Tuple[TokenTypeBase, any, int, any]


def process_float(f):
    return float('0' + f) if f[0] == '.' else float(f)


def process_int(i):
    return int(i)


def process_int_base8(i):
    return int(i, 8)


def process_int_base16(i):
    return int(i, 16)


def process_string(s):
    return s[1:-1]


def expand_token_position(token: Token) -> (int, int):
    """ Returns a (line, column) tuple for a given character position
        inside the current buffer. This is an expensive function to
        call, so do not use this frequently.
    """

    pos = token[2]
    lexer = token[3]

    return lexer.expand_position(pos)


@dataclass(frozen=True)
class Rule:
    """ A single rule that can be matched.
    """
    type: TokenTypeBase
    regex: str
    process: Optional[any] = None
    skip: bool = False


class LexerError(Exception):
    """ Lexer error exception.
    """

    def __init__(self, message: str, position: Tuple[int, int]):
        super(Exception, self).__init__('Line {} column {}: {}'.format(position[0], position[1], message))


class Lexer:
    """ A simple regex-based lexer/tokenizer.

        See below for an example of usage.
    """

    def __init__(self, rules: List[Rule], add_newline: bool = True):
        """ Create a lexer.

            rules:
                A list of rules. Each rule is a Rule instance with a type
                identifier, a regular expression used to recognize the token,
                and an optional `skip` parameter to indicate that if the rule
                is matched, the token should be skipped.

                Note that the regexes themselves can use groups, but these
                must be non-capturing (?:).
        """

        # All the rule regexes are concatenated into a single grouped one.
        regex_parts = []
        self.group_rules: List[Rule] = []
        for rule in rules:
            regex_parts.append('({})'.format(rule.regex))
            self.group_rules.append(rule)
        self.regex: Pattern = re.compile('|'.join(regex_parts))

        self.text: Optional[str] = None
        self.text_len: int = 0
        self.pos: int = 0
        self.add_newline = add_newline

    def input(self, text: str):
        """ Initializes the lexer text input.
        """

        self.text = text
        if self.add_newline:
            self.text += '\n'

        self.text_len = len(text)
        self.pos = 0

    def require_token(self, token_type: TokenTypeBase) -> any:
        """ Returns the value if the next token is of a specific type.
        """

        token = self.get_token()
        if token is None:
            raise LexerError('Expected "{}" token but reached end of file.'.format(token_type), (0, 0))
        if token[0] != token_type:
            raise LexerError('Expected "{}" token, got "{}".'.format(token_type, token[0]), expand_token_position(token))

        return token[1]

    def get_all_tokens_until(self, token_type: TokenTypeBase) -> List[Token]:
        """ Returns a list of tokens up to and including a specific token type.
        """

        tokens = []
        while True:
            token = self.get_token()
            if token is None:
                break

            tokens.append(token)
            if token[0] == token_type:
                break

        return tokens

    def skip_tokens_until(self, token_type: TokenTypeBase):
        """ Skips tokens up to and including a specific token type.
        """

        while True:
            token = self.get_token()
            if token is None:
                break
            if token[0] == token_type:
                break

    def get_token(self) -> Optional[Token]:
        """ Returns the next token found in the input buffer. None is returned
            if the end of the buffer was reached.

            In case of a lexing error (the current chunk of the buffer matches
            no rule), a LexerError is raised with the position of the error.
        """

        while True:
            if self.pos >= self.text_len:
                return None

            m = self.regex.match(self.text, self.pos)
            if not m:
                break

            # A token was detected, but it did not advance in the text stream.
            if m.end() == self.pos:
                break

            self.pos = m.end()
            group_index = m.lastindex
            rule = self.group_rules[group_index - 1]
            if rule.skip:
                continue

            value = m.group(group_index)
            if rule.process is not None:
                value = rule.process(value)

            return rule.type, value, m.pos, self

        # If we're here, no rule matched.
        raise LexerError('Invalid token', self.expand_position(self.pos))

    def expand_position(self, pos: int):
        """ Returns a (line, column) tuple for a given character position
            inside the current buffer. This is an expensive function to
            call, so do not use this frequently.
        """

        text_part = self.text[:pos]

        line = text_part.count('\n') + 1
        line_start = text_part.rfind('\n')
        if line_start > 0:
            return line, pos - line_start + 1

        return line, pos + 1
