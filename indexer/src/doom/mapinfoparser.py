import re
from copy import copy
from enum import Enum
from re import Pattern
from typing import Tuple, Optional, List, Dict

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from utils import lexer
from utils.lexer import Lexer, Rule, Token, expand_token_position


RE_CLEAN: Pattern = re.compile('[\x00\xff\x1a]')


class MapInfoParserError(Exception):
    def __init__(self, message: str, position: Tuple[int, int]):
        super(Exception, self).__init__('Line {} column {}: {}'.format(position[0], position[1], message))


class MapInfoToken(Enum):
    EOL: str = 'eol'
    WHITESPACE: str = 'white'
    COMMENT: str = 'comment'
    IDENTIFIER: str = 'ident'
    ASSIGN: str = 'assign'
    BLOCK_START: str = 'blstart'
    BLOCK_END: str = 'blend'
    STRING: str = 'str'
    SEPARATOR: str = 'sep'


class ParseMode(Enum):
    NONE: int = 0
    MAP: int = 1
    EPISODE: int = 2


class MapInfoMap:
    map_lump: Optional[str] = None
    title: Optional[str] = None
    next: Optional[str] = None
    next_secret: Optional[str] = None
    cluster_index: Optional[int] = None
    par_time: Optional[int] = None
    music: Optional[str] = None
    allow_jump: Optional[bool] = None
    allow_crouch: Optional[bool] = None


class MapInfoEpisode:
    map_lump: Optional[str] = None
    title: Optional[str] = None


def get_lexer() -> Lexer:
    return Lexer(
        [
            Rule(MapInfoToken.EOL, r'[\n\r]+'),
            Rule(MapInfoToken.WHITESPACE, r'[\s]+', skip=True),
            Rule(MapInfoToken.COMMENT, r'(?:;).*?\r?\n', skip=True),
            Rule(MapInfoToken.COMMENT, r'//.*?\r?\n', skip=True),
            Rule(MapInfoToken.COMMENT, r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', skip=True),
            Rule(MapInfoToken.ASSIGN, '='),
            Rule(MapInfoToken.BLOCK_START, '{'),
            Rule(MapInfoToken.BLOCK_END, '}'),
            Rule(MapInfoToken.SEPARATOR, ','),
            Rule(MapInfoToken.IDENTIFIER, r'[\\?!\\$\\:`@A-Za-z0-9_\-\+\\-\\.]+'),
            Rule(MapInfoToken.STRING, r'"(?:\\.|[^"])*(?:"|$)', process=lexer.process_string),
        ]
    )


def get_file_tokens(file: ArchiveFileBase):
    text = file.get_data().decode('latin1')
    text = RE_CLEAN.sub('', text)

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


class MapInfoParser:

    def __init__(self, archive: ArchiveBase):
        self.archive = archive

        self.maps: Dict[str, MapInfoMap] = {}
        self.episodes: List[MapInfoEpisode] = []
        self.new_format = False
        self.tokens: List[Token] = []

    def parse(self, file: ArchiveFileBase):
        self.tokens = get_file_tokens(file)

        default_map: MapInfoMap = MapInfoMap()
        current_map: MapInfoMap = MapInfoMap()
        current_episode: MapInfoEpisode = MapInfoEpisode()
        parse_mode = ParseMode.NONE
        self.new_format = False

        # Manually consume tokens so that we can peek ahead.
        while len(self.tokens):
            key_token = self.tokens.pop()

            if key_token[0] == MapInfoToken.EOL:
                continue
            elif key_token[0] == MapInfoToken.BLOCK_START:
                self.new_format = True
                continue
            elif key_token[0] == MapInfoToken.BLOCK_END:
                self.new_format = False
                parse_mode = ParseMode.NONE
                continue

            key = key_token[1].lower()
            if key == 'include':
                include_filename = str(self.get_token()[1])
                include_file = self.archive.file_find_regexp(include_filename)
                if include_file:
                    include_tokens = get_file_tokens(include_file)
                    self.tokens.extend(include_tokens)
                else:
                    raise MapInfoParserError('Cannot find include file "{}".'.format(include_filename), expand_token_position(key_token))
                continue

            elif key == 'defaultmap':
                default_map = MapInfoMap()
                current_map = default_map
                parse_mode = ParseMode.MAP
                continue

            elif key == 'adddefaultmap':
                current_map = default_map
                parse_mode = ParseMode.MAP
                continue

            elif key == 'map':
                current_map = copy(default_map)
                self.parse_map_header(current_map)
                self.maps[current_map.map_lump] = current_map
                parse_mode = ParseMode.MAP
                continue

            elif key == 'clearepisodes':
                self.episodes.clear()
                current_episode = MapInfoEpisode()
                continue

            elif key == 'episode':
                current_episode = MapInfoEpisode()
                self.parse_episode_header(current_episode)
                self.episodes.append(current_episode)
                parse_mode = ParseMode.EPISODE
                continue

            elif parse_mode == ParseMode.MAP:
                if key == 'next':
                    self.parse_assignment()
                    current_map.next = self.parse_next_map()
                elif key == 'title':
                    self.parse_assignment()
                    current_map.title = self.parse_title()
                elif key == 'par':
                    self.parse_assignment()
                    current_map.par_time = self.parse_integer()
                elif key == 'secretnext':
                    self.parse_assignment()
                    current_map.next_secret = self.parse_next_map()
                elif key == 'cluster':
                    self.parse_assignment()
                    current_map.cluster_index = self.parse_integer()
                elif key == 'music':
                    self.parse_assignment()
                    current_map.music = self.parse_music()
                elif key == 'nocrouch':
                    current_map.allow_crouch = False
                elif key == 'crouchallowed':
                    current_map.allow_crouch = True
                elif key == 'nojump':
                    current_map.allow_jump = False
                elif key == 'jumpallowed':
                    current_map.allow_jump = True
                else:
                    self.skip_until(MapInfoToken.EOL)

            elif parse_mode == ParseMode.EPISODE:
                if key == 'title':
                    self.parse_assignment()
                    current_episode.title = self.parse_string()
                elif key == 'lookup':
                    self.parse_assignment()
                    current_episode.title = '${}'.format(self.parse_string())
                else:
                    self.skip_until(MapInfoToken.EOL)

            else:
                self.skip_until(MapInfoToken.EOL)

    def get_token(self) -> Optional[Token]:
        if not len(self.tokens):
            raise MapInfoParserError('Expected a token, got end of file.', (0, 0))
        return self.tokens.pop()

    def peek_token(self) -> Optional[Token]:
        if not len(self.tokens):
            return None
        return self.tokens[-1]

    def require_token(self, token_type) -> Token:
        token = self.tokens.pop()
        if token[0] != token_type:
            raise MapInfoParserError('Expected "{}" token, got "{}".'.format(token_type, token[0]), expand_token_position(token))

        return token

    def skip_until(self, token_type):
        while len(self.tokens):
            token = self.get_token()
            if token is None:
                break
            elif token[0] == token_type:
                break

    def parse_assignment(self):
        if self.new_format:
            self.require_token(MapInfoToken.ASSIGN)

    def parse_map_header(self, mapinfo_map: MapInfoMap):
        lump_token = self.get_token()
        mapinfo_map.map_lump = str(lump_token[1])

        title_token = self.get_token()
        if str(title_token[1]).lower() == 'lookup':
            lookup_token = self.get_token()
            mapinfo_map.title = '${}'.format(str(lookup_token[1]))
        else:
            mapinfo_map.title = str(title_token[1])

    def parse_episode_header(self, mapinfo_episode: MapInfoEpisode):
        lump_token = self.get_token()
        mapinfo_episode.map_lump = str(lump_token[1])

        title_token = self.get_token()
        mapinfo_episode.title = str(title_token[1])

        # episode MAP01 teaser DEMO01
        next_token = self.peek_token()
        if next_token is not None and next_token[0] == MapInfoToken.IDENTIFIER and next_token[1].lower() == 'teaser':
            self.get_token()
            self.get_token()

    def parse_next_map(self) -> str:
        token = self.get_token()
        if token[1].isdigit():
            next_map = 'MAP{:02}'.format(int(token[1]))
        elif token[0] == MapInfoToken.STRING or MapInfoToken.IDENTIFIER:
            next_map = str(token[1])
        else:
            raise MapInfoParserError(
                'Invalid value "{}" for map lump, expected integer, string or identifier.'.format(token[1]),
                expand_token_position(token))

        if next_map.lower() == 'endpic':
            next_token = self.peek_token()
            if next_token[0] == MapInfoToken.SEPARATOR:
                self.get_token()
            pic = self.get_token()
            next_map = 'endpic:{}'.format(str(pic[1]))
        elif next_map.lower() == 'endgame':
            self.skip_until(MapInfoToken.BLOCK_END)
            next_map = 'endgame'
        elif next_map.lower() == 'endsequence':
            next_token = self.peek_token()
            if next_token[0] == MapInfoToken.SEPARATOR:
                self.get_token()
            sequence = self.get_token()
            next_map = 'endsequence:{}'.format(str(sequence[1]))

        return next_map

    def parse_music(self) -> str:
        token = self.get_token()
        if token[0] == MapInfoToken.STRING or token[0] == MapInfoToken.IDENTIFIER:
            music = token[1]
        else:
            raise MapInfoParserError('Invalid value "{}" for music name, expected string or identifier.'.format(token[1]),
                                     expand_token_position(token))

        next_token = self.peek_token()
        if next_token is not None and next_token[1] == ':':
            self.get_token()
            index_token = self.get_token()
            return '{}:{}'.format(music, index_token[1])

        return music

    def parse_title(self) -> str:
        next_token = self.get_token()
        if next_token[0] == MapInfoToken.IDENTIFIER and next_token[1] == 'lookup':
            lookup_key = self.get_token()
            title = '${}'.format(str(lookup_key[1]))
        else:
            title = str(next_token[1])

        return title

    def parse_integer(self) -> int:
        value = self.get_token()
        try:
            return int(value[1])
        except ValueError:
            return 0

    def parse_string(self) -> str:
        value = self.get_token()
        if value[0] != MapInfoToken.STRING and value[0] != MapInfoToken.IDENTIFIER:
            raise MapInfoParserError('Invalid value "{}", expected string or identifier.'.format(value[1]),
                                     expand_token_position(value))

        return value[1]
