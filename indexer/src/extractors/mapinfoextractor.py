import re
from typing import Optional, Pattern

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.level import Level
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


def assign_mapinfo_to_level(level: Level, map_info: MapInfoMap):
    level.title = map_info.title
    level.music = map_info.music
    level.allow_jump = map_info.allow_jump
    level.allow_crouch = map_info.allow_crouch
    level.par_time = map_info.par_time
    level.cluster = map_info.cluster_index
    level.next = map_info.next
    level.next_secret = map_info.next_secret


class MapInfoExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if not len(info.levels):
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

        # Match mapinfo data to levels.
        for level in info.levels:
            for map_key, map_info in parser.maps.items():
                if map_key.lower() == level.name.lower():
                    assign_mapinfo_to_level(level, map_info)
