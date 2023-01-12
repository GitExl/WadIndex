from enum import Enum
from typing import Tuple, Optional, List

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.mapinfoparserbase import MapInfoParserBase, MapInfoMap
from utils import lexer
from utils.lexer import Lexer, Rule, expand_token_position, Token


class UMapInfoParserError(Exception):
    def __init__(self, message: str, position: Tuple[int, int]):
        super(Exception, self).__init__('Line {} column {}: {}'.format(position[0], position[1], message))


class UMapInfoToken(Enum):
    WHITESPACE: str = 'white'
    COMMENT: str = 'comment'
    IDENTIFIER: str = 'ident'
    BLOCK_START: str = 'bstart'
    BLOCK_END: str = 'bend'
    ASSIGN: str = 'assign'
    SEPARATOR: str = 'sep'
    INTEGER: str = 'int'
    FLOAT: str = 'float'
    KEYWORD: str = 'keyword'
    STRING: str = 'str'


def get_lexer() -> Lexer:
    return Lexer(
        [
            Rule(UMapInfoToken.WHITESPACE, r'[\s\n\r]+', skip=True),
            Rule(UMapInfoToken.COMMENT, r'//.*?\r?\n', skip=True),
            Rule(UMapInfoToken.COMMENT, r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', skip=True),
            Rule(UMapInfoToken.ASSIGN, '='),
            Rule(UMapInfoToken.SEPARATOR, ','),
            Rule(UMapInfoToken.BLOCK_START, '{'),
            Rule(UMapInfoToken.BLOCK_END, '}'),
            Rule(UMapInfoToken.IDENTIFIER, '[A-Za-z_]+[A-Za-z0-9_]*'),
            Rule(UMapInfoToken.FLOAT, '[+-]?[0-9]+\\.[0-9]*(?:[eE][+-]?[0-9]+)?', process=lexer.process_float),
            Rule(UMapInfoToken.INTEGER, '[+-]?[1-9]\\d*|0', process=lexer.process_int),
            Rule(UMapInfoToken.INTEGER, '0[0-9]+', process=lexer.process_int_base8),
            Rule(UMapInfoToken.INTEGER, '0x[0-9A-Fa-f]+', process=lexer.process_int_base16),
            Rule(UMapInfoToken.KEYWORD, '[^{}();"\'\n\t ]+'),
            Rule(UMapInfoToken.STRING, '"(?:[^"\\\\]|\\\\.)*"', process=lexer.process_string),
        ]
    )


def get_file_tokens(file: ArchiveFileBase):
    text = file.get_data().decode('latin1')

    file_lexer = get_lexer()
    file_lexer.input(text)

    tokens = []
    while True:
        token = file_lexer.get_token()
        if not token:
            break
        tokens.append(token)
    tokens.reverse()

    return tokens


class UMapInfoParser(MapInfoParserBase):

    def __init__(self, archive: ArchiveBase):
        super().__init__(archive)

        self.tokens: List[Token] = []

    def parse(self, file: ArchiveFileBase):
        self.tokens = get_file_tokens(file)
        while len(self.tokens):
            token = self.tokens.pop()

            if token[0] != UMapInfoToken.IDENTIFIER:
                raise UMapInfoParserError('Expected an identifier, got "{}".'.format(token[1]), expand_token_position(token))
            identifier = token[1].lower()

            if identifier == 'map':
                map = self.parse_map()
                self.maps[map.map_lump] = map
            else:
                raise UMapInfoParserError('Unknown root identifier "{}".'.format(identifier), expand_token_position(token))

    def get_token(self) -> Optional[Token]:
        if not len(self.tokens):
            raise UMapInfoParserError('Expected a token, got end of file.', (0, 0))
        return self.tokens.pop()

    def peek_token(self) -> Optional[Token]:
        if not len(self.tokens):
            return None
        return self.tokens[-1]

    def require_token(self, token_type) -> Token:
        token = self.tokens.pop()
        if token[0] != token_type:
            raise UMapInfoParserError('Expected "{}" token, got "{}".'.format(token_type, token[0]), expand_token_position(token))

        return token

    def parse_map(self) -> MapInfoMap:
        map = MapInfoMap()
        map.map_lump = self.require_token(UMapInfoToken.IDENTIFIER)[1]

        self.require_token(UMapInfoToken.BLOCK_START)

        while len(self.tokens):
            token = self.tokens.pop()
            if token[0] == UMapInfoToken.BLOCK_END:
                break
            elif token[0] != UMapInfoToken.IDENTIFIER:
                raise UMapInfoParserError('Expected an identifier, got "{}".'.format(token[1]), expand_token_position(token))

            identifier = token[1].lower()
            self.require_token(UMapInfoToken.ASSIGN)

            if identifier == 'levelname':
                map.title = self.require_token(UMapInfoToken.STRING)[1]
            elif identifier == 'author':
                map.author = self.require_token(UMapInfoToken.STRING)[1]
            elif identifier == 'label':
                self.get_token()
            elif identifier == 'levelpic':
                self.get_token()
            elif identifier == 'next':
                map.next = self.require_token(UMapInfoToken.STRING)[1]
            elif identifier == 'nextsecret':
                map.next_secret = self.require_token(UMapInfoToken.STRING)[1]
            elif identifier == 'skytexture':
                self.get_token()
            elif identifier == 'music':
                map.music = self.require_token(UMapInfoToken.STRING)[1]
            elif identifier == 'exitpic':
                self.get_token()
            elif identifier == 'enterpic':
                self.get_token()
            elif identifier == 'partime':
                map.par_time = self.require_token(UMapInfoToken.INTEGER)[1]
            elif identifier == 'endgame':
                self.get_token()
            elif identifier == 'endpic':
                self.get_token()
            elif identifier == 'endbunny':
                self.get_token()
            elif identifier == 'endcast':
                self.get_token()
            elif identifier == 'nointermission':
                self.get_token()
            elif identifier == 'intertext':
                self.parse_multiline_string()
            elif identifier == 'intertextsecret':
                self.parse_multiline_string()
            elif identifier == 'interbackdrop':
                self.get_token()
            elif identifier == 'intermusic':
                self.get_token()
            elif identifier == 'episode':
                token = self.get_token()
                if token[1].lower() != 'clear':
                    self.require_token(UMapInfoToken.SEPARATOR)
                    self.get_token()
                    self.require_token(UMapInfoToken.SEPARATOR)
                    self.get_token()
            elif identifier == 'bossaction':
                token = self.get_token()
                if token[1].lower() != 'clear':
                    self.require_token(UMapInfoToken.SEPARATOR)
                    self.get_token()
                    self.require_token(UMapInfoToken.SEPARATOR)
                    self.get_token()
            else:
                raise UMapInfoParserError('Unknown UMAPINFO map key "{}".'.format(token[1]), expand_token_position(token))

        return map

    def parse_multiline_string(self) -> Optional[str]:
        parts: List[str] = []

        while len(self.tokens):
            token = self.peek_token()
            if token[0] != UMapInfoToken.STRING and token[0] != UMapInfoToken.SEPARATOR:
                return None

            token = self.get_token()
            if token[0] == UMapInfoToken.STRING:
                parts.append(token[1])
            elif token[0] == UMapInfoToken.SEPARATOR:
                continue
            else:
                raise UMapInfoParserError('Error parsing UMAPINFO multiline string.'.format(token[1]), expand_token_position(token))

        return str.join('\n', parts)
