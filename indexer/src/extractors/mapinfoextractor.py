from typing import Optional

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.map import Map
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
    # 'RMAPINFO',
    'UMAPINFO',
    'MAPINFO',
]


def assign_mapinfo_to_map(map: Map, map_info: MapInfoMap):
    if map_info.title is not None:
        map.title = map_info.title
    if map_info.music is not None:
        map.music = map_info.music
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
    if map_info.authors is not None:
        map.authors = author_parser.parse(map_info.authors)


class MapInfoExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if not len(info.maps):
            return

        archive: ArchiveBase = info.archive
        if archive is None:
            self.logger.warn('Cannot extract map info without an archive.')
            return

        file: Optional[ArchiveFileBase] = None
        for filename in FILE_ORDER:
            file = archive.file_find_basename(filename)
            if file is not None:
                break

        if file is None:
            return

        parser: Optional[MapInfoParserBase] = None
        try:
            if file.name == 'MAPINFO' or file.name == 'ZMAPINFO':
                parser = ZMapInfoParser(file)
            elif file.name == 'UMAPINFO':
                parser = UMapInfoParser(file)
            else:
                return
        except LexerError as e:
            self.logger.stream('mapinfo_lexer_error', info.path_idgames.as_posix())
            self.logger.stream('mapinfo_lexer_error', str(e))

        if parser is None:
            return

        try:
            parser.parse()
        except MapInfoParserError as e:
            self.logger.stream('mapinfo_parser_error', info.path_idgames.as_posix())
            self.logger.stream('mapinfo_parser_error', str(e))
        except TokenListError as e:
            self.logger.stream('mapinfo_token_list_error', info.path_idgames.as_posix())
            self.logger.stream('mapinfo_token_list_error', str(e))

        # Match mapinfo data to maps.
        for map in info.maps:
            for map_key, map_info in parser.maps.items():
                if map_key.lower() == map.name.lower():
                    assign_mapinfo_to_map(map, map_info)
