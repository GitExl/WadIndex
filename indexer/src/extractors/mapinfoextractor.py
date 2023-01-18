from typing import Optional, List

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.strings_builtin import BUILTIN_STRINGS, MUSIC_NAMES_DOOM, MUSIC_NAMES_DOOM2, MUSIC_NAMES_HERETIC, \
    MUSIC_NAMES_HEXEN, MUSIC_NAMES_STRIFE
from doom.map import Map
from indexer.game import Game
from mapinfo.mapinfoparserbase import MapInfoParserBase, MapInfoParserError, MapInfoMap
from mapinfo.zmapinfoparser import ZMapInfoParser
from mapinfo.umapinfoparser import UMapInfoParser
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from utils import author_parser
from utils.lexer import LexerError
from utils.token_list import TokenListError


FILE_ORDER = [
    'ZMAPINFO',
    # 'EMAPINFO',
    'RMAPINFO',
    'UMAPINFO',
    'MAPINFO',
]


class MapInfoExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if not len(info.maps):
            return

        archive: ArchiveBase = info.archive
        if archive is None:
            self.logger.debug('Cannot extract map info without an archive.')
            return

        mapinfo_files: List[ArchiveFileBase] = []
        for filename in FILE_ORDER:
            file = archive.file_find_basename(filename)
            if file is not None:
                mapinfo_files.append(file)

        for file in mapinfo_files:
            parser: Optional[MapInfoParserBase] = None
            try:
                if file.name == 'MAPINFO' or file.name == 'ZMAPINFO' or file.name == 'RMAPINFO':
                    parser = ZMapInfoParser(file)
                elif file.name == 'UMAPINFO':
                    parser = UMapInfoParser(file)
                else:
                    continue
            except LexerError as e:
                self.logger.stream('mapinfo_lexer_error', '{}: {}'.format(info.path_idgames.as_posix(), str(e)))

            if parser is None:
                continue

            try:
                parser.parse()
            except MapInfoParserError as e:
                self.logger.stream('mapinfo_parser_error', '{}: {}'.format(info.path_idgames.as_posix(), str(e)))
            except TokenListError as e:
                self.logger.stream('mapinfo_token_list_error', '{}: {}'.format(info.path_idgames.as_posix(), str(e)))

            # Match mapinfo data to maps.
            for map in info.maps:
                for map_key, map_info in parser.maps.items():
                    if map_key.lower() == map.name.lower():
                        self.assign_mapinfo_to_map(map, map_info, info)

        # Set default music for maps depending on the game.
        if info.game != Game.UNKNOWN:
            self.assign_game_music_defaults(info)

    @staticmethod
    def assign_game_music_defaults(info: ExtractedInfo):
        if info.game == Game.DOOM or info.game == Game.CHEX:
            name_source = MUSIC_NAMES_DOOM
        elif info.game == Game.DOOM2 or info.game == Game.TNT or info.game == Game.PLUTONIA or info.game == Game.HACX:
            name_source = MUSIC_NAMES_DOOM2
        elif info.game == Game.HERETIC:
            name_source = MUSIC_NAMES_HERETIC
        elif info.game == Game.HEXEN:
            name_source = MUSIC_NAMES_HEXEN
        elif info.game == Game.STRIFE:
            name_source = MUSIC_NAMES_STRIFE
        else:
            return

        for map in info.maps:
            if map.music is not None:
                continue

            # If the archive contains the default music, assign it.
            default_music = name_source.get(map.name, None)
            if default_music is None:
                continue
            if info.archive_list.file_find_basename(default_music, False) is not None:
                map.music = default_music

    def assign_mapinfo_to_map(self, map: Map, map_info: MapInfoMap, info: ExtractedInfo):
        if map_info.title is not None:
            title = self.replace_language_lookup(map_info.title, info)
            if title is not None and title != '':
                map.title = title

        if map_info.music is not None:
            music = self.replace_language_lookup(map_info.music, info)
            if music is not None and music != '':
                map.music = music

        if map_info.authors is not None:
            map.authors = author_parser.parse(map_info.authors)

        if map_info.allow_jump is not None:
            map.allow_jump = map_info.allow_jump
        if map_info.allow_crouch is not None:
            map.allow_crouch = map_info.allow_crouch
        if map_info.par_time is not None:
            map.par_time = map_info.par_time
        if map_info.cluster_index is not None:
            map.cluster = map_info.cluster_index
        if map_info.next is not None:
            map.next = map_info.next
        if map_info.next_secret is not None:
            map.next_secret = map_info.next_secret

    @staticmethod
    def replace_language_lookup(key: Optional[str], info: ExtractedInfo) -> Optional[str]:
        if key is None:
            return None
        if not key.startswith('$'):
            return key

        key = key[1:]
        if key in BUILTIN_STRINGS:
            return BUILTIN_STRINGS[key]
        if info.locale_strings is None:
            return key

        replacement = info.locale_strings.get_default(key)
        if replacement is None:
            return key

        return replacement
