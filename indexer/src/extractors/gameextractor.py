import json
from pathlib import Path
from typing import Dict

from archives.archivelist import ArchiveList
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from indexer.game import Game
from textparser.textkeys import TEXT_GAMES
from textparser.textparser import TextParser
from utils.config import Config
from utils.logger import Logger


LumpScores = Dict[str, Dict[Game, float]]


class GameExtractor(ExtractorBase):

    def __init__(self, logger: Logger, config: Config):
        super().__init__(logger, config)

        self.lump_scores: LumpScores = self._load_lump_scores()

    def _load_lump_scores(self) -> LumpScores:
        lump_scores: LumpScores = {}

        with open(self.config.get('extractors.game.lump_score_table'), 'r') as f:
            scores = json.load(f)

        for file_name, scores in scores.items():
            lump_scores[file_name] = {}

            for game, score in scores.items():
                game = Game[game]
                lump_scores[file_name][game] = score

        return lump_scores

    def extract(self, info: ExtractedInfo):
        game = Game.UNKNOWN

        # Only try to detect the game if one is not set already.
        if 'game' in info.text_keys and info.text_keys['game'] != Game.UNKNOWN:
            game = info.text_keys['game']
            self.logger.decision('Detected game "{}" from parsed text file.'.format(game.name))

        # Detect from idgames path.
        if game == Game.UNKNOWN:
            game = self.detect_from_path(info.path_idgames)
            if game != Game.UNKNOWN:
                self.logger.decision('Detected game "{}" from path.'.format(game.name))

        # Detect from certain lump names.
        if game == Game.UNKNOWN and info.archive_list is not None:
            game = self.detect_from_archive_list(info.archive_list)
            if game != Game.UNKNOWN:
                self.logger.decision('Detected game "{}" from lump names.'.format(game.name))

        # Last ditch effort, just use the entire text file.
        if game == Game.UNKNOWN and info.text_contents:
            game = self.detect_from_text(info.text_contents)
            if game != Game.UNKNOWN:
                self.logger.decision('Detected game "{}" from complete text file contents.'.format(game.name))

        if game == Game.UNKNOWN:
            self.logger.warn('Cannot determine game.')
            self.logger.stream('game_unknown', info.path_idgames.as_posix())
            return

        info.game = game

    @staticmethod
    def detect_from_path(path: Path) -> Game:
        path_str = path.as_posix()
        if path_str.find('doom2') > -1:
            return Game.DOOM2
        elif path_str.find('doom') > -1:
            return Game.DOOM
        elif path_str.find('heretic') > -1:
            return Game.HERETIC
        elif path_str.find('hexen') > -1:
            return Game.HEXEN
        elif path_str.find('strife') > -1:
            return Game.HEXEN
        elif path_str.find('hacx') > -1:
            return Game.HACX

        return Game.UNKNOWN

    @staticmethod
    def detect_from_text(text_file: str) -> Game:
        text_data = text_file.lower()
        key, data = TextParser.match_key(text_data, TEXT_GAMES)
        if key:
            return Game(key)

        return Game.UNKNOWN

    def detect_from_archive_list(self, archive_list: ArchiveList) -> Game:

        # TODO: is this still necessary or is the lump score method better?
        if archive_list.file_find_basename('bossback', False) or archive_list.file_find_regexp('VILE', False) or archive_list.file_find_regexp('CPOS', False) or archive_list.file_find_basename('help', False):
            return Game.DOOM2

        elif archive_list.file_find_basename('rsky1', False) or archive_list.file_find_basename('rsky2', False) or archive_list.file_find_basename('rsky3', False) or archive_list.file_find_basename('rsky4', False):
            return Game.DOOM2

        elif archive_list.file_find_basename('m_doom', False) or archive_list.file_find_regexp('^CWILV.*', False):
            return Game.DOOM2

        elif archive_list.file_find_basename('m_htic', False) or archive_list.file_find_basename('title', False):
            return Game.HERETIC

        elif archive_list.file_find_basename('help1', False) and not archive_list.file_find_basename('help2', False) or archive_list.file_find_regexp('^WILV.*', False):
            return Game.DOOM

        # Attempt detection through lump scores.
        scores = {}
        for archive in archive_list.archives:
            for file in archive.files:
                if file.name in self.lump_scores:
                    for game, score in self.lump_scores[file.name].items():
                        if game in scores:
                            scores[game] += score
                        else:
                            scores[game] = score

        if len(scores):
            game = max(scores.keys(), key=(lambda k: scores[k]))
            return game

        return Game.UNKNOWN
