from typing import Optional, Dict, List, Tuple

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase


class MapInfoParserError(Exception):
    def __init__(self, message: str, position: Tuple[int, int]):
        super(Exception, self).__init__('Line {} column {}: {}'.format(position[0], position[1], message))


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


class MapInfoParserBase:

    def __init__(self, file: ArchiveFileBase):
        self.archive: ArchiveBase = file.owner
        self.file: ArchiveFileBase = file

        self.maps: Dict[str, MapInfoMap] = {}
        self.episodes: List[MapInfoEpisode] = []

    def parse(self):
        pass
