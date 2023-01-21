import re
from copy import copy
from enum import Enum
from re import Pattern
from archives.archivefilebase import ArchiveFileBase
from doom.mapinfo.mapinfo_parser_base import MapInfoMap, MapInfoParserBase, MapInfoEpisode, MapInfoParserError
from utils.lexer import Lexer, Rule, expand_token_position, TokenTypeBase, process_string
from utils.token_list import TokenList


RE_CLEAN: Pattern = re.compile('[\x00\xff\x1a]')


class ZMapInfoToken(TokenTypeBase):
    EOL = 0
    WHITESPACE = 1
    COMMENT = 2
    IDENTIFIER = 3
    ASSIGN = 4
    BLOCK_START = 5
    BLOCK_END = 6
    STRING = 7
    SEPARATOR = 8


class ZParseMode(Enum):
    NONE = 0
    MAP = 1
    EPISODE = 2
    CLUSTER = 3


def get_lexer() -> Lexer:
    return Lexer(
        [
            Rule(ZMapInfoToken.EOL, r'[\n\r]+'),
            Rule(ZMapInfoToken.WHITESPACE, r'[ \t]+', skip=True),
            Rule(ZMapInfoToken.COMMENT, r'(?:;).*?\r?\n', skip=True),
            Rule(ZMapInfoToken.COMMENT, r'//.*?(?=[\n\r])', skip=True),
            Rule(ZMapInfoToken.COMMENT, r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', skip=True),
            Rule(ZMapInfoToken.ASSIGN, '='),
            Rule(ZMapInfoToken.BLOCK_START, '{'),
            Rule(ZMapInfoToken.BLOCK_END, '}'),
            Rule(ZMapInfoToken.SEPARATOR, ','),
            Rule(ZMapInfoToken.IDENTIFIER, r'[\\?!\\$\\:`@A-Za-z0-9_\-\+\\-\\.]+'),
            Rule(ZMapInfoToken.STRING, r'"(?:\\.|[^"])*(?:"|$)', process=process_string),
        ]
    )


def get_file_tokens(file: ArchiveFileBase) -> TokenList:
    text = file.get_data().decode('latin1')
    text = RE_CLEAN.sub('', text)

    lexer = get_lexer()
    lexer.input(text)

    return TokenList(lexer)


class ZMapInfoParser(MapInfoParserBase):

    def __init__(self, file: ArchiveFileBase):
        super().__init__(file)

        self.new_format = False

        self.tokens = get_file_tokens(file)

    def parse(self):
        default_map: MapInfoMap = MapInfoMap()
        current_map: MapInfoMap = MapInfoMap()
        current_episode: MapInfoEpisode = MapInfoEpisode()
        parse_mode = ZParseMode.NONE
        self.new_format = False

        while not self.tokens.eol():
            key_token = self.tokens.get()

            if key_token[0] == ZMapInfoToken.EOL:
                continue
            elif key_token[0] == ZMapInfoToken.BLOCK_START:
                self.new_format = True
                continue
            elif key_token[0] == ZMapInfoToken.BLOCK_END:
                self.new_format = False
                parse_mode = ZParseMode.NONE
                continue

            key = key_token[1].lower()
            if key == 'include':
                include_filename = str(self.tokens.get()[1])
                include_file = self.archive.file_find_regexp(include_filename)
                if include_file:
                    include_tokens = get_file_tokens(include_file)
                    self.tokens.insert(include_tokens)
                else:
                    raise MapInfoParserError('Cannot find include file "{}".'.format(include_filename), expand_token_position(key_token))
                continue

            elif key == 'defaultmap':
                default_map = MapInfoMap()
                current_map = default_map
                parse_mode = ZParseMode.MAP
                continue

            elif key == 'adddefaultmap':
                current_map = default_map
                parse_mode = ZParseMode.MAP
                continue

            elif key == 'map':
                current_map = copy(default_map)
                self.parse_map_header(current_map)
                self.maps[current_map.map_lump] = current_map
                parse_mode = ZParseMode.MAP
                continue

            elif key == 'clearepisodes':
                self.episodes.clear()
                current_episode = MapInfoEpisode()
                continue

            elif key == 'episode':
                current_episode = MapInfoEpisode()
                self.parse_episode_header(current_episode)
                self.episodes.append(current_episode)
                parse_mode = ZParseMode.EPISODE
                continue

            elif key == 'cluster' and parse_mode == ZParseMode.NONE:
                self.tokens.require(ZMapInfoToken.IDENTIFIER)
                parse_mode = ZParseMode.CLUSTER
                continue

            elif parse_mode == ZParseMode.MAP:
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

                # From RMAPINFO
                elif key == 'author':
                    self.parse_assignment()
                    author = self.parse_string()
                    if author is not None:
                        current_map.authors.append(author[1])
                # What a terrible place to put these two...
                elif key == 'musicartist':
                    self.parse_string()
                elif key == 'musictitle':
                    self.parse_string()

                else:
                    self.tokens.skip_until(ZMapInfoToken.EOL)

            elif parse_mode == ZParseMode.EPISODE:
                if key == 'title':
                    self.parse_assignment()
                    current_episode.title = self.parse_string()
                elif key == 'lookup':
                    self.parse_assignment()
                    current_episode.title = '${}'.format(self.parse_string())
                else:
                    self.tokens.skip_until(ZMapInfoToken.EOL)

            else:
                self.tokens.skip_until(ZMapInfoToken.EOL)

    def parse_assignment(self):
        if self.new_format:
            self.tokens.require(ZMapInfoToken.ASSIGN)

    def parse_map_header(self, mapinfo_map: MapInfoMap):
        lump_token = self.tokens.get()
        mapinfo_map.map_lump = str(lump_token[1])

        title_token = self.tokens.get()
        if str(title_token[1]).lower() == 'lookup':
            lookup_token = self.tokens.get()
            mapinfo_map.title = '${}'.format(str(lookup_token[1]))
        else:
            mapinfo_map.title = str(title_token[1])

    def parse_episode_header(self, mapinfo_episode: MapInfoEpisode):
        lump_token = self.tokens.get()
        mapinfo_episode.map_lump = str(lump_token[1])

        title_token = self.tokens.get()
        mapinfo_episode.title = str(title_token[1])

        # episode MAP01 teaser DEMO01
        next_token = self.tokens.peek()
        if next_token is not None and next_token[0] == ZMapInfoToken.IDENTIFIER and next_token[1].lower() == 'teaser':
            self.tokens.get()
            self.tokens.get()

    def parse_next_map(self) -> str:
        token = self.tokens.get()
        if token[1].isdigit():
            next_map = 'MAP{:02}'.format(int(token[1]))
        elif token[0] == ZMapInfoToken.STRING or ZMapInfoToken.IDENTIFIER:
            next_map = str(token[1])
        else:
            raise MapInfoParserError(
                'Invalid value "{}" for map lump, expected integer, string or identifier.'.format(token[1]),
                expand_token_position(token))

        if next_map.lower() == 'endpic':
            next_token = self.tokens.peek()
            if next_token[0] == ZMapInfoToken.SEPARATOR:
                self.tokens.get()
            pic = self.tokens.get()
            next_map = 'endpic:{}'.format(str(pic[1]))
        elif next_map.lower() == 'endgame':
            self.tokens.skip_until(ZMapInfoToken.BLOCK_END)
            next_map = 'endgame'
        elif next_map.lower() == 'endsequence':
            next_token = self.tokens.peek()
            if next_token[0] == ZMapInfoToken.SEPARATOR:
                self.tokens.get()
            sequence = self.tokens.get()
            next_map = 'endsequence:{}'.format(str(sequence[1]))

        return next_map

    def parse_music(self) -> str:
        token = self.tokens.get()
        if token[0] == ZMapInfoToken.STRING or token[0] == ZMapInfoToken.IDENTIFIER:
            music = token[1]
        else:
            raise MapInfoParserError('Invalid value "{}" for music name, expected string or identifier.'.format(token[1]),
                                      expand_token_position(token))

        next_token = self.tokens.peek()
        if next_token is not None and next_token[1] == ':':
            self.tokens.skip()
            index_token = self.tokens.get()
            return '{}:{}'.format(music, index_token[1])

        return music

    def parse_title(self) -> str:
        next_token = self.tokens.get()
        if next_token[0] == ZMapInfoToken.IDENTIFIER and next_token[1] == 'lookup':
            lookup_key = self.tokens.get()
            title = '${}'.format(str(lookup_key[1]))
        else:
            title = str(next_token[1])

        return title

    def parse_integer(self) -> int:
        value = self.tokens.get()
        try:
            return int(value[1])
        except ValueError:
            return 0

    def parse_string(self) -> str:
        value = self.tokens.get()
        if value[0] != ZMapInfoToken.STRING and value[0] != ZMapInfoToken.IDENTIFIER:
            raise MapInfoParserError('Invalid value "{}", expected string or identifier.'.format(value[1]),
                                      expand_token_position(value))

        return value[1]
