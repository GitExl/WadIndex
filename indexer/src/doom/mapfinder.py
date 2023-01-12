from typing import Dict, Optional, Set

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase
from doom.map import MapFormat, MapNamespace


MAP_LUMP_NAMES: Set[str] = {
    'THINGS',
    'LINEDEFS',
    'SIDEDEFS',
    'VERTEXES',
    'SEGS',
    'SSECTORS',
    'NODES',
    'SECTORS',
    'REJECT',
    'BLOCKMAP',
    'BEHAVIOR',
    'SCRIPTS',
    'DIALOGUE',
}


class MapData:

    def __init__(self, name: str):
        self.name: str = name
        self.files: Dict[str, ArchiveFileBase] = {}
        self.format: MapFormat = MapFormat.DOOM
        self.namespace: MapNamespace = MapNamespace.DOOM

    def add(self, file: ArchiveFileBase):
        self.files[file.name] = file

        if file.name == 'TEXTMAP':
            self.format = MapFormat.UDMF
        elif self.format != MapFormat.UDMF and file.name == 'BEHAVIOR':
            self.format = MapFormat.HEXEN


class MapDataFinder:

    def __init__(self):
        self.map_data: Dict[str, MapData] = {}

    def add_from_archive(self, archive: ArchiveBase, name: Optional[str] = None):
        for index, file in enumerate(archive.files):
            if file.name != 'THINGS' and file.name != 'TEXTMAP':
                continue

            map_data = MapDataFinder._collect_map_data(archive, index - 1)
            if name is not None:
                map_data.name = name[0:8]
            self.map_data[map_data.name] = map_data

    @staticmethod
    def _collect_map_data(archive: ArchiveBase, header_index: int) -> MapData:
        header_file = archive.files[header_index]
        map_data: MapData = MapData(header_file.name)

        # Collect UDMF map lumps between the header and ENDMAP
        lump_index_max = min(len(archive.files), header_index + 20)
        next_lump = archive.files[header_index + 1]
        if next_lump.name == 'TEXTMAP':
            for index in range(header_index + 1, lump_index_max):
                file = archive.files[index]
                if file.name == 'ENDMAP':
                    break

                map_data.add(file)

        # Collect valid Doom\Hexen map lumps.
        else:
            for index in range(header_index + 1, lump_index_max):
                file = archive.files[index]
                if file.name not in MAP_LUMP_NAMES and not file.name.startswith('GL_'):
                    break

                map_data.add(file)

        return map_data
