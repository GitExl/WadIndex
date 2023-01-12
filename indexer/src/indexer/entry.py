from typing import Dict, Optional

from indexer.engine import Engine
from indexer.game import Game


INT_TO_GAME: Dict[int, Game] = {
    0: Game.UNKNOWN,
    1: Game.DOOM,
    2: Game.DOOM2,
    3: Game.TNT,
    4: Game.PLUTONIA,
    5: Game.HERETIC,
    6: Game.HEXEN,
    7: Game.STRIFE,
    8: Game.CHEX,
    9: Game.HACX,
}

GAME_TO_INT: Dict[Game, int] = {
    Game.UNKNOWN: 0,
    Game.DOOM: 1,
    Game.DOOM2: 2,
    Game.TNT: 3,
    Game.PLUTONIA: 4,
    Game.HERETIC: 5,
    Game.HEXEN: 6,
    Game.STRIFE: 7,
    Game.CHEX: 8,
    Game.HACX: 9,
}

INT_TO_ENGINE: Dict[int, Engine] = {
    0: Engine.UNKNOWN,
    1: Engine.DOOM,
    2: Engine.HERETIC,
    3: Engine.HEXEN,
    4: Engine.STRIFE,
    5: Engine.NOLIMITS,
    6: Engine.BOOM,
    7: Engine.MBF,
    8: Engine.ZDOOM,
    9: Engine.GZDOOM,
    10: Engine.LEGACY,
    11: Engine.SKULLTAG,
    12: Engine.ZDAEMON,
    13: Engine.DOOMSDAY,
    14: Engine.EDGE,
    15: Engine.ETERNITY,
    16: Engine.DOOMRETRO,
    17: Engine.ZANDRONUM,
    18: Engine.ODAMEX,
}

ENGINE_TO_INT: Dict[Engine, int] = {
    Engine.UNKNOWN: 0,
    Engine.DOOM: 1,
    Engine.HERETIC: 2,
    Engine.HEXEN: 3,
    Engine.STRIFE: 4,
    Engine.NOLIMITS: 5,
    Engine.BOOM: 6,
    Engine.MBF: 7,
    Engine.ZDOOM: 8,
    Engine.GZDOOM: 9,
    Engine.LEGACY: 10,
    Engine.SKULLTAG: 11,
    Engine.ZDAEMON: 12,
    Engine.DOOMSDAY: 13,
    Engine.EDGE: 14,
    Engine.ETERNITY: 15,
    Engine.DOOMRETRO: 16,
    Engine.ZANDRONUM: 17,
    Engine.ODAMEX: 18,
}


class Entry:

    def __init__(self, collection: str, path: str, file_modified: int, file_size: int, entry_updated: int):
        self.collection: str = collection
        self.path: str = path
        self.file_modified: int = file_modified
        self.entry_updated: int = entry_updated
        self.file_size: int = file_size

        self.id: Optional[int] = None
        self.directory_id: Optional[int] = None

        self.title: Optional[str] = None
        self.game: Optional[Game] = None
        self.engine: Optional[Engine] = None
        self.is_singleplayer: Optional[bool] = None
        self.is_cooperative: Optional[bool] = None
        self.is_deathmatch: Optional[bool] = None
        self.description: Optional[str] = None
        self.tools_used: Optional[str] = None
        self.known_bugs: Optional[str] = None
        self.credits: Optional[str] = None
        self.build_time: Optional[str] = None
        self.comments: Optional[str] = None

    def __repr__(self):
        return '{}, {}: {}'.format(self.id, self.path, self.title)

    def to_row(self) -> Dict[str, any]:
        game = None
        if self.game in GAME_TO_INT:
            game = GAME_TO_INT.get(self.game)

        engine = None
        if self.engine in ENGINE_TO_INT:
            engine = ENGINE_TO_INT.get(self.engine)

        return {
            'collection': self.collection,
            'path': self.path,
            'directory_id': self.directory_id,
            'file_modified': self.file_modified,
            'entry_updated': self.entry_updated,
            'file_size': self.file_size,
            'title': self.title,
            'game': game,
            'engine': engine,
            'is_singleplayer': self.is_singleplayer,
            'is_cooperative': self.is_cooperative,
            'is_deathmatch': self.is_deathmatch,
            'description': self.description,
            'description_preview': self.description[:199] if self.description is not None else None,
            'tools_used': self.tools_used,
            'known_bugs': self.known_bugs,
            'credits': self.credits,
            'build_time': self.build_time,
            'comments': self.comments,
        }

    @staticmethod
    def from_row(row: Dict):
        game: Game = Game.UNKNOWN
        if row['game'] in INT_TO_GAME:
            game = INT_TO_GAME.get(row['game'])

        engine: Engine = Engine.UNKNOWN
        if row['engine'] in INT_TO_ENGINE:
            engine = INT_TO_ENGINE.get(row['engine'])

        entry = Entry(
            row['collection'],
            row['path'],
            row['file_modified'],
            row['file_size'],
            row['entry_updated']
        )
        entry.id = row['id']
        entry.title = row['title']
        entry.game = game
        entry.engine = engine
        entry.directory_id = row['directory_id']
        entry.file_size = row['file_size']
        entry.is_singleplayer = row['is_singleplayer']
        entry.is_cooperative = row['is_cooperative']
        entry.is_deathmatch = row['is_deathmatch']
        entry.description = row['description']
        entry.tools_used = row['tools_used']
        entry.known_bugs = row['known_bugs']
        entry.credits = row['credits']
        entry.build_time = row['build_time']
        entry.comments = row['comments']

        return entry
