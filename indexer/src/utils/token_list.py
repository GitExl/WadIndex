from __future__ import annotations

from typing import List, Optional, Tuple

from utils.lexer import Lexer, Token, TokenTypeBase, expand_token_position


class TokenListError(Exception):

    def __init__(self, message: str, position: Tuple[int, int]):
        super(Exception, self).__init__('Line {} column {}: {}'.format(position[0], position[1], message))


class TokenList:

    def __init__(self, lexer: Lexer):
        self.tokens: List[Token] = []
        self.token_index = 0

        # Get all tokens from the lexer in one go.
        while True:
            token = lexer.get_token()
            if not token:
                break
            self.tokens.append(token)
        self.token_count = len(self.tokens)

    def eol(self) -> bool:
        return self.token_index >= self.token_count

    def get(self) -> Optional[Token]:
        if self.token_index >= self.token_count:
            raise TokenListError('Expected a token, got end of file.', (0, 0))

        token = self.tokens[self.token_index]
        self.token_index += 1
        return token

    def peek(self) -> Optional[Token]:
        if self.token_index >= self.token_count:
            return None

        return self.tokens[self.token_index]

    def skip(self, count=1):
        self.token_index += count

    def require(self, token_type: TokenTypeBase) -> Token:
        if self.token_index >= self.token_count:
            raise TokenListError('Expected a token, got end of file.', (0, 0))

        token = self.tokens[self.token_index]
        self.token_index += 1

        if token[0] != token_type:
            raise TokenListError('Expected "{}" token, got "{}".'.format(token_type, token[0]), expand_token_position(token))

        return token

    def skip_until(self, token_type: TokenTypeBase) -> Optional[Token]:
        while self.token_index < self.token_count:
            token = self.tokens[self.token_index]
            self.token_index += 1

            if token[0] == token_type:
                return token

        return None

    def insert(self, other_tokens: TokenList):
        self.tokens[self.token_index:self.token_index] = other_tokens.tokens
