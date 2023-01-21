from typing import Optional, List

from archives.archivefilebase import ArchiveFileBase
from doom.mapinfo.mapinfo_parser_base import MapInfoParserBase, MapInfoMap, MapInfoParserError
from utils.lexer import Lexer, Rule, expand_token_position, TokenTypeBase, process_float, process_int, \
    process_int_base8, process_int_base16, process_string
from utils.token_list import TokenList


class UMapInfoToken(TokenTypeBase):
    WHITESPACE = 0
    COMMENT = 1
    IDENTIFIER = 2
    BLOCK_START = 3
    BLOCK_END = 4
    ASSIGN = 5
    SEPARATOR = 6
    INTEGER = 7
    FLOAT = 8
    KEYWORD = 9
    STRING = 10


def get_lexer() -> Lexer:
    return Lexer(
        [
            Rule(UMapInfoToken.WHITESPACE, r'[\s\n\r]+', skip=True),
            Rule(UMapInfoToken.COMMENT, r'//.*?(?=[\n\r])', skip=True),
            Rule(UMapInfoToken.COMMENT, r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', skip=True),
            Rule(UMapInfoToken.ASSIGN, '='),
            Rule(UMapInfoToken.SEPARATOR, ','),
            Rule(UMapInfoToken.BLOCK_START, '{'),
            Rule(UMapInfoToken.BLOCK_END, '}'),
            Rule(UMapInfoToken.IDENTIFIER, '[A-Za-z_]+[A-Za-z0-9_]*'),
            Rule(UMapInfoToken.FLOAT, '[+-]?[0-9]+\\.[0-9]*(?:[eE][+-]?[0-9]+)?', process=process_float),
            Rule(UMapInfoToken.INTEGER, '[+-]?[1-9]\\d*|0', process=process_int),
            Rule(UMapInfoToken.INTEGER, '0[0-9]+', process=process_int_base8),
            Rule(UMapInfoToken.INTEGER, '0x[0-9A-Fa-f]+', process=process_int_base16),
            Rule(UMapInfoToken.KEYWORD, '[^{}();"\'\n\t ]+'),
            Rule(UMapInfoToken.STRING, '"(?:[^"\\\\]|\\\\.)*"', process=process_string),
        ]
    )


class UMapInfoParser(MapInfoParserBase):

    def __init__(self, file: ArchiveFileBase):
        super().__init__(file)

        text = self.file.get_data().decode('latin1')
        lexer = get_lexer()
        lexer.input(text)

        self.tokens: TokenList = TokenList(lexer)

    def parse(self):
        while not self.tokens.eol():
            token = self.tokens.get()

            if token[0] != UMapInfoToken.IDENTIFIER:
                raise MapInfoParserError('Expected an identifier, got "{}".'.format(token[1]), expand_token_position(token))
            identifier = token[1].lower()

            if identifier == 'map':
                map = self.parse_map()
                self.maps[map.map_lump] = map
            else:
                raise MapInfoParserError('Unknown root identifier "{}".'.format(identifier), expand_token_position(token))

    def parse_map(self) -> MapInfoMap:
        map = MapInfoMap()
        map.map_lump = self.tokens.require(UMapInfoToken.IDENTIFIER)[1]

        self.tokens.require(UMapInfoToken.BLOCK_START)

        while not self.tokens.eol():
            token = self.tokens.get()
            if token[0] == UMapInfoToken.BLOCK_END:
                break
            elif token[0] != UMapInfoToken.IDENTIFIER:
                raise MapInfoParserError('Expected an identifier, got "{}".'.format(token[1]), expand_token_position(token))

            identifier = token[1].lower()
            self.tokens.require(UMapInfoToken.ASSIGN)

            if identifier == 'levelname':
                map.title = self.tokens.require(UMapInfoToken.STRING)[1]
            elif identifier == 'author':
                map.authors = [self.tokens.require(UMapInfoToken.STRING)[1]]
            elif identifier == 'label':
                self.tokens.get()
            elif identifier == 'levelpic':
                self.tokens.get()
            elif identifier == 'next':
                map.next = self.tokens.require(UMapInfoToken.STRING)[1]
            elif identifier == 'nextsecret' or identifier == 'secretnext':
                map.next_secret = self.tokens.require(UMapInfoToken.STRING)[1]
            elif identifier == 'skytexture' or identifier == 'sky':
                self.tokens.get()
            elif identifier == 'music':
                map.music = self.tokens.require(UMapInfoToken.STRING)[1]
            elif identifier == 'exitpic':
                self.tokens.get()
            elif identifier == 'enterpic':
                self.tokens.get()
            elif identifier == 'partime' or identifier == 'par':
                map.par_time = self.tokens.require(UMapInfoToken.INTEGER)[1]
            elif identifier == 'endgame':
                self.tokens.get()
            elif identifier == 'endpic':
                self.tokens.get()
            elif identifier == 'endbunny':
                self.tokens.get()
            elif identifier == 'endcast':
                self.tokens.get()
            elif identifier == 'nointermission':
                self.tokens.get()
            elif identifier == 'intertext':
                self.parse_multiline_string()
            elif identifier == 'intertextsecret':
                self.parse_multiline_string()
            elif identifier == 'interbackdrop':
                self.tokens.get()
            elif identifier == 'intermusic':
                self.tokens.get()
            elif identifier == 'episode':
                token = self.tokens.get()
                if token[1].lower() != 'clear':
                    self.tokens.require(UMapInfoToken.SEPARATOR)
                    self.tokens.get()
                    self.tokens.require(UMapInfoToken.SEPARATOR)
                    self.tokens.get()
            elif identifier == 'bossaction':
                token = self.tokens.get()
                if token[1].lower() != 'clear':
                    self.tokens.require(UMapInfoToken.SEPARATOR)
                    self.tokens.get()
                    self.tokens.require(UMapInfoToken.SEPARATOR)
                    self.tokens.get()
            else:
                raise MapInfoParserError('Unknown UMAPINFO map key "{}".'.format(token[1]), expand_token_position(token))

        return map

    def parse_multiline_string(self) -> Optional[str]:
        parts: List[str] = []

        token = self.tokens.peek()
        if token[0] == UMapInfoToken.IDENTIFIER and token[1].lower() == 'clear':
            self.tokens.get()
            return None

        while not self.tokens.eol():
            token = self.tokens.peek()
            if token[0] != UMapInfoToken.STRING and token[0] != UMapInfoToken.SEPARATOR:
                return None

            token = self.tokens.get()
            if token[0] == UMapInfoToken.STRING:
                parts.append(token[1])
            elif token[0] == UMapInfoToken.SEPARATOR:
                continue
            else:
                raise MapInfoParserError('Error parsing UMAPINFO multiline string.'.format(token[1]), expand_token_position(token))

        return str.join('\n', parts)
