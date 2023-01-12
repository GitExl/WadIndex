from typing import Optional

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.map import Map
from doom.mapinfoparserbase import MapInfoParserBase, MapInfoParserError
from doom.zmapinfoparser import ZMapInfoParser, MapInfoMap, ZMapInfoParserError
from doom.umapinfoparser import UMapInfoParser
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from utils.lexer import LexerError


FILE_ORDER = [
    'ZMAPINFO',
    'EMAPINFO',
    'RMAPINFO',
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

        parser: MapInfoParserBase
        if file.name == 'MAPINFO' or file.name == 'ZMAPINFO':
            parser = ZMapInfoParser(info.archive)
        elif file.name == 'UMAPINFO':
            parser = UMapInfoParser(info.archive)
        else:
            return

        try:
            parser.parse(file)
        except LexerError as e:
            self.logger.stream('mapinfo_lexer_error', info.path_idgames.as_posix())
            self.logger.stream('mapinfo_lexer_error', str(e))
        except MapInfoParserError as e:
            self.logger.stream('mapinfo_parser_error', info.path_idgames.as_posix())
            self.logger.stream('mapinfo_parser_error', str(e))

        # Match mapinfo data to maps.
        for map in info.maps:
            for map_key, map_info in parser.maps.items():
                if map_key.lower() == map.name.lower():
                    assign_mapinfo_to_map(map, map_info)
