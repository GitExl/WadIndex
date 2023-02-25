import os
from typing import Optional, List

from archives.archivefilebase import ArchiveFileBase
from archives.archivelist import ArchiveList
from doom.strings_builtin import STRINGS_BUILTIN
from doom.map.map import Map
from doom.mapinfo.mapinfo_parser_base import MapInfoParserBase, MapInfoParserError, MapInfoMap
from doom.mapinfo.zmapinfo_parser import ZMapInfoParser
from doom.mapinfo.umapinfo_parser import UMapInfoParser
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

        archive_list: ArchiveList = info.archive_list
        if archive_list is None:
            self.logger.debug('Cannot extract map info without an archive list.')
            return

        mapinfo_files: List[ArchiveFileBase] = []
        for filename in FILE_ORDER:
            files = archive_list.file_find_all_basename(filename, False)
            mapinfo_files.extend(files)
        mapinfo_files.reverse()

        for file in mapinfo_files:
            filename = os.path.splitext(file.name.lower())[0]

            parser: Optional[MapInfoParserBase] = None
            try:
                if filename == 'mapinfo' or filename == 'zmapinfo' or filename == 'rmapinfo':
                    parser = ZMapInfoParser(file)
                elif filename == 'umapinfo':
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
        if key in STRINGS_BUILTIN:
            return STRINGS_BUILTIN[key]
        if info.locale_strings is None:
            return key

        replacement = info.locale_strings.get_default(key)
        if replacement is None:
            return key

        return replacement
