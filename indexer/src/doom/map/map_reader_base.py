from doom.map.map import Map
from doom.map.map_data_finder import MapData
from indexer.game import Game
from utils.logger import Logger


class MapReaderBase:

    def __init__(self, game: Game, logger: Logger):
        self.game: Game = game
        self.logger: Logger = logger

    def read(self, map_data: MapData) -> Map:
        pass
