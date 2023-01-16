from __future__ import annotations

from copy import copy
from typing import Tuple, Optional, List, Set, Dict

from indexer.game import Game
from utils.lexer import TokenTypeBase, Lexer, Rule, process_string
from utils.token_list import TokenList


class LanguageToken(TokenTypeBase):
    WHITESPACE = 1
    COMMENT = 2
    IDENTIFIER = 3
    ASSIGN = 4
    END = 5
    STRING = 6
    HEADER = 7
    CONDITION = 8


class LanguageParserError(Exception):
    def __init__(self, message: str, position: Tuple[int, int]):
        super(Exception, self).__init__('Line {} column {}: {}'.format(position[0], position[1], message))


def process_condition(s: str):
    return s[1:-1].split('(')


def parse_game(s: str) -> Optional[Game]:
    if s == 'doom':
        return Game.DOOM
    elif s == 'heretic':
        return Game.HERETIC
    elif s == 'hexen':
        return Game.HEXEN
    elif s == 'strife':
        return Game.STRIFE
    elif s == 'chex':
        return Game.CHEX

    return None


class LocaleStrings:

    def __init__(self):
        self.strings: Dict[str, Dict[str, str]] = {
            'default': {}
        }

    def add(self, language: str, key: str, value: str):
        if language not in self.strings:
            self.strings[language] = {}
        self.strings[language][key] = value

    def get_default(self, key: str) -> Optional[str]:
        return self.strings['default'].get(key, None)

    def add_from(self, other: LocaleStrings):
        for language, strings in other.strings.items():
            if language not in self.strings:
                self.strings[language] = copy(other.strings[language])
            else:
                for key, value in strings.items():
                    self.strings[language][key] = value


class LanguageParser:

    def __init__(self, text: str):
        lexer: Lexer = Lexer(
            [
                Rule(LanguageToken.WHITESPACE, r'[\s\n\r]+', skip=True),
                Rule(LanguageToken.COMMENT, r'//.*?\r?\n', skip=True),
                Rule(LanguageToken.COMMENT, r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', skip=True),
                Rule(LanguageToken.ASSIGN, '='),
                Rule(LanguageToken.HEADER, r'\[(?:.*)\]'),
                Rule(LanguageToken.END, ';'),
                Rule(LanguageToken.STRING, '"(?:[^"\\\\]|\\\\.)*"', process=process_string),
                Rule(LanguageToken.CONDITION, r'\$.*?\(.*?\)', process=process_condition),
                Rule(LanguageToken.IDENTIFIER, r'[A-Za-z0-9_]*'),
            ]
        )
        lexer.input(text)
        self.tokens: TokenList = TokenList(lexer)

    def parse_locale_strings(self, game: Game) -> LocaleStrings:
        if game == Game.DOOM2 or game == Game.PLUTONIA or game == Game.TNT or game == Game.HACX:
            game = Game.DOOM

        strings: LocaleStrings = LocaleStrings()

        current_languages: Set[str] = set()
        next_game = None

        while not self.tokens.eol():
            token = self.tokens.get()
            if token is None:
                break

            # Language header
            if token[0] == LanguageToken.HEADER:
                current_languages.clear()
                languages = token[1][1:-1].split(' ')
                for language in languages:
                    language = language.lower()
                    current_languages.add(language)

            # Condition
            elif token[0] == LanguageToken.CONDITION:
                if token[1][0] == 'ifgame':
                    next_game = parse_game(token[1][1])

            # Key
            elif token[0] == LanguageToken.IDENTIFIER:
                key = token[1].rstrip()
                self.tokens.require(LanguageToken.ASSIGN)
                value = self.parse_string()

                if next_game is None or game == next_game:
                    for language in current_languages:
                        strings.add(language, key, value)

                next_game = None

        return strings

    def parse_string(self) -> str:
        parts: List[str] = []

        while not self.tokens.eol():
            token = self.tokens.peek()

            # Strings (or identifiers, thanks darkbase.pk3!)
            if token[0] == LanguageToken.STRING or token[0] == LanguageToken.IDENTIFIER:
                parts.append(token[1])
                self.tokens.skip()

            # Attempt to work with missing semicolons (thanks, lilith.pk3!)
            elif token[0] == LanguageToken.END:
                self.tokens.skip()
                break

            else:
                break

        return ''.join(parts)
