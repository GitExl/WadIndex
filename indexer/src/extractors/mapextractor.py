from io import BytesIO
from pathlib import Path

from archives.archivebase import ArchiveBase
from archives.wadarchive import WADArchive
from doom.binarymapreader import BinaryMapReader
from doom.mapfinder import MapDataFinder, MapFormat
from doom.udmfmapreader import UDMFMapReader
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from indexer.game import Game


class MapExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        archive: ArchiveBase = info.archive
        if archive is None:
            self.logger.warn('Cannot extract maps without an archive.')
            return

        if info.game == Game.UNKNOWN:
            self.logger.warn('Cannot extract maps without a known game.')
            return

        map_data_finder = MapDataFinder()

        # Load maps directly from the archive.
        map_data_finder.add_from_archive(archive)

        # Load maps from maps/*.wad files inside the archive (ZDoom maps/ namespace).
        wad_archives = []
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
                if map:
                    info.maps.append(map)
                    self.logger.debug('Found {} ({}): {} vertices, {} lines, {} sides, {} sectors, {} things.'.format(
                        map.name, map_data.format.name,
                        len(map.vertices), len(map.lines), len(map.sides), len(map.sectors), len(map.things))
                    )

        for archive in wad_archives:
            archive.close()

        self.logger.decision('Found {} valid maps.'.format(len(info.maps)))
