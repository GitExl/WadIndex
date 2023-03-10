from io import BytesIO
from pathlib import Path
from statistics import fmean

from archives.archivelist import ArchiveList
from archives.wadarchive import WADArchive
from doom.map.binary_map_reader import BinaryMapReader
from doom.map.blockmap_generator import BlockmapGenerator
from doom.map.map import MapFormat
from doom.map.map_data_finder import MapDataFinder
from doom.map.udmf_map_reader import UDMFMapReader
from doom.nodes.nodes_finder import NodesFinder
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from indexer.game import Game


class MapExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        archive_list: ArchiveList = info.archive_list
        if archive_list is None:
            self.logger.debug('Cannot extract maps without an archive list.')
            return

        if info.game == Game.UNKNOWN:
            self.logger.debug('Cannot extract maps without a known game.')
            return

        map_data_finder = MapDataFinder()

        # Load maps directly from the archive.
        wad_archives = []
        for archive in archive_list.archives:
            if archive.is_main:
                continue

            map_data_finder.add_from_archive(archive)

            # Load maps from maps/*.wad files inside the archive (ZDoom maps/ namespace).
            map_wads = archive.file_find_all_regexp(r'maps/.*\.wad')
            for wad in map_wads:
                wad_base_name = Path(wad.name).stem
                wad_data = BytesIO(wad.get_data())
                wad_archive = WADArchive(wad.name, wad_data, self.logger)
                map_data_finder.add_from_archive(wad_archive, wad_base_name)

                wad_archives.append(wad_archive)

        # Some safeguarding against dumb map bomb entries.
        if len(map_data_finder.map_data) > 500:
            self.logger.warn('Ignoring all maps inside possible map bomb.')
        else:
            for map_name, map_data in map_data_finder.map_data.items():
                if map_data.format == MapFormat.UDMF:
                    reader = UDMFMapReader(info.game, self.logger)
                else:
                    reader = BinaryMapReader(info.game, self.logger)

                map = reader.read(map_data)
                if map is not None:
                    info.maps.append(map)
                    self.logger.debug('Found {} ({}): {} vertices, {} lines, {} sides, {} sectors, {} things.'.format(
                        map.name, map_data.format.name,
                        len(map.vertices), len(map.lines), len(map.sides), len(map.sectors), len(map.things))
                    )

                    # Detect node data.
                    nodes_finder = NodesFinder(map, map_data, self.logger, info.path_idgames.as_posix())
                    map.nodes_type = nodes_finder.nodes_type
                    map.nodes_gl_type = nodes_finder.nodes_gl_type

                    # Load node data.
                    # nodes_reader = nodes_finder.get_reader()
                    # if nodes_reader is not None:
                    #     nodes = nodes_reader.read()

                    # Calculate complexity.
                    # blockmap_generator = BlockmapGenerator(map, 128)
                    # blockmap = blockmap_generator.blockmap
                    # line_lengths = []
                    # for block in blockmap:
                    #     if block is None:
                    #         continue
                    #     line_lengths.append(block.total_length)
                    # if len(line_lengths):
                    #     map.complexity = len(map.sectors) / fmean(line_lengths)

        for archive in wad_archives:
            archive.close()

        self.logger.decision('Found {} valid maps.'.format(len(info.maps)))
