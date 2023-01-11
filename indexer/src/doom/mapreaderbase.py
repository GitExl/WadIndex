from doom.map import Map
from doom.mapfinder import MapData
from idgames.game import Game
from utils.logger import Logger


class MapReaderBase:

    def __init__(self, game: Game, logger: Logger):
        self.game: Game = game
        self.logger: Logger = logger

    def read(self, map_data: MapData) -> Map:
        pass
