from typing import Optional

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.map import Map
from doom.mapinfoparser import MapInfoParser, MapInfoMap, MapInfoParserError
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
    map.title = map_info.title
    map.music = map_info.music
    map.allow_jump = map_info.allow_jump
    map.allow_crouch = map_info.allow_crouch
    map.par_time = map_info.par_time
    map.cluster = map_info.cluster_index
    map.next = map_info.next
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
                if file.name.upper() == 'EMAPINFO':
                    self.logger.warn('EMAPINFO not yet supported.')
                    file = None
                    continue
                elif file.name.upper() == 'UMAPINFO':
                    self.logger.warn('UMAPINFO not yet supported.')
                    file = None
                    continue
                break

        if file is None:
            return

        parser = MapInfoParser(info.archive)
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
