import json
from typing import Dict, Set, List

from archives.archivebase import ArchiveBase
from doom.map.map import Map
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from indexer.engine import Engine
from indexer.game import Game
from textparser.textkeys import TEXT_ENGINE
from textparser.textparser import TextParser
from utils.config import Config
from utils.logger import Logger


EngineLumps = Dict[Engine, Set[str]]
DoomednumScores = Dict[int, Dict[Engine, float]]


class EngineExtractor(ExtractorBase):

    def __init__(self, logger: Logger, config: Config):
        super().__init__(logger, config)

        self.engine_lumps: EngineLumps = self._load_engine_lumps()
        self.doomednum_scores: DoomednumScores = self._load_doomednum_scores()

    def _load_engine_lumps(self) -> EngineLumps:
        engine_lumps: EngineLumps = {}

        with open(self.config.get('extractors.engine.lump_table'), 'r') as f:
            engines_data = json.load(f)

        for engine_key in engines_data.keys():
            engine = Engine[engine_key]
            engine_lumps[engine] = self._get_engine_lumps(engines_data, engine_key)

        return engine_lumps

    def _get_engine_lumps(self, engines_data: Dict[str, any], engine_key: str) -> Set[str]:
        engine_info = engines_data.get(engine_key)
        inherit = engine_info.get('inherits', None)
        if inherit is not None:
            lumps = self._get_engine_lumps(engines_data, engine_key)
        else:
            lumps = set()

        lumps.update(engine_info.get('lumps'))

        return lumps

    def _load_doomednum_scores(self) -> DoomednumScores:
        scores: DoomednumScores = {}

        with open(self.config.get('extractors.engine.doomednum_scores'), 'r') as f:
            engines = json.load(f)

        for doomednum, engine_scores in engines.items():
            scores[int(doomednum)] = engine_scores

        return scores

    def extract(self, info: ExtractedInfo):
        engine = Engine.UNKNOWN

        # Only try to detect the engine if one is not set already.
        if 'engine' in info.text_keys and info.text_keys['engine'] != Engine.UNKNOWN:
            engine = info.text_keys['engine']
            self.logger.decision('Detected engine "{}" from parsed text file.'.format(engine.name))

        # Detect from map data.
        if engine == Engine.UNKNOWN and len(info.maps):
            engine = self.detect_from_maps(info.maps)
            if engine != Game.UNKNOWN:
                self.logger.decision('Detected engine "{}" from map data.'.format(engine.name))

        # Detect from lump names.
        if engine == Engine.UNKNOWN and info.main_archive is not None:
            engine = self.detect_from_lumps(info.archive)
            if engine != Game.UNKNOWN:
                self.logger.decision('Detected engine "{}" from lump names.'.format(engine.name))

        # Last ditch effort, just use the entire text file.
        if engine == Engine.UNKNOWN and info.text_contents:
            engine = self.detect_from_text(info.text_contents)
            if engine != Engine.UNKNOWN:
                self.logger.decision('Detected engine "{}" from complete text file contents.'.format(engine.name))

        if engine == Engine.UNKNOWN:
            self.logger.stream('engine_unknown', info.path_idgames.as_posix())
            return

        info.engine = engine

    def detect_from_lumps(self, archive: ArchiveBase) -> Engine:
        scores: Dict[Engine, float] = {}
        for engine, lump_set in self.engine_lumps.items():

            for lump_name in lump_set:
                if archive.file_find_basename(lump_name) is not None:
                    if engine not in scores:
                        scores[engine] = 1
                    else:
                        scores[engine] += 1

        if len(scores):
            engine = max(scores.keys(), key=(lambda k: scores[k]))
            if scores[engine] >= 1:
                return Engine(engine)

        return Engine.UNKNOWN

    def detect_from_maps(self, maps: List[Map]) -> Engine:
        scores: Dict[str, float] = {}
        for map in maps:

            for thing in map.things:
                score = self.doomednum_scores.get(thing.id, None)
                if not score:
                    continue

                for engine_key, engine_score in scores.items():
                    if engine_key not in scores:
                        scores[engine_key] = engine_score
                    else:
                        scores[engine_key] += engine_score

        if len(scores):
            engine = max(scores.keys(), key=(lambda k: scores[k]))
            if scores[engine] >= 5:
                return Engine(engine)

        return Engine.UNKNOWN

    @staticmethod
    def detect_from_text(text_file: str) -> Engine:
        text_data = text_file.lower()
        key, data = TextParser.match_key(text_data, TEXT_ENGINE)
        if key:
            return Engine(key)

        return Engine.UNKNOWN
