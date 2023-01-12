import os
from typing import Dict

from archives.archivelist import ArchiveList
from archives.wadarchive import WADArchive
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase

from indexer.game import Game
from utils.config import Config
from utils.logger import Logger


class ArchiveListExtractor(ExtractorBase):

    def __init__(self, logger: Logger, config: Config):
        super().__init__(logger, config)

        self.iwads: Dict[Game, WADArchive] = {}

        self._add_iwad(Game.DOOM2, 'DOOM2.WAD')
        self._add_iwad(Game.DOOM, 'DOOM.WAD')
        self._add_iwad(Game.HERETIC, 'HERETIC.WAD')
        self._add_iwad(Game.HEXEN, 'HEXEN.WAD')
        self._add_iwad(Game.TNT, 'TNT.WAD')
        self._add_iwad(Game.PLUTONIA, 'PLUTONIA.WAD')
        self._add_iwad(Game.STRIFE, 'STRIFE0.WAD')
        self._add_iwad(Game.HACX, 'HACX.WAD')

    def extract(self, info: ExtractedInfo):
        if info.archive is None:
            self.logger.warn('Cannot create archive list without main archive.')
            return

        if info.game not in self.iwads:
            self.logger.warn('Cannot create archive list for archive for an unknown game.')
            return

        iwad = self.iwads[info.game]

        self.logger.decision('Using "{}" as IWAD.'.format(os.path.basename(iwad.file.name)))

        info.archive_list = ArchiveList()
        info.archive_list.append(iwad)
        info.archive_list.append(info.archive)

    def cleanup(self, info: ExtractedInfo):
        if info.archive_list is None:
            return

        info.archive_list.close(iwads=False)

    def _add_iwad(self, game: Game, filename: str):
        wad_path = '{}/{}'.format(self.config.get('paths.iwads'), filename)
        self.iwads[game] = WADArchive.from_path(wad_path, self.logger)

    def close(self):
        for iwad in self.iwads.values():
            iwad.close()
