from typing import Dict, Optional, List

from doom.map.map import Map
from extractors.extractedinfo import MusicInfo, GraphicInfo
from indexer.engine import Engine
from indexer.game import Game
from utils.author_parser import Author


class Entry:

    def __init__(self, collection: str, path: str, file_modified: int, file_size: int, entry_updated: int):
        self.collection: str = collection
        self.path: str = path
        self.file_modified: int = file_modified
        self.file_size: int = file_size
        self.entry_updated: int = entry_updated

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

        self.maps: List[Map] = []
        self.authors: List[Author] = []
        self.text_contents: Optional[str] = None
        self.graphics: Dict[str, GraphicInfo] = {}
        self.music: Dict[str, MusicInfo] = {}

    def __repr__(self):
        return '{}, {}: {}'.format(self.id, self.path, self.title)

    def to_row(self) -> Dict[str, any]:
        return {
            'collection': self.collection,
            'path': self.path,
            'directory_id': self.directory_id,
            'file_modified': self.file_modified,
            'entry_updated': self.entry_updated,
            'file_size': self.file_size,
            'title': self.title,
            'game': self.game.value if self.game is not None else None,
            'engine': self.engine.value if self.engine is not None else None,
            'is_singleplayer': self.is_singleplayer,
            'is_cooperative': self.is_cooperative,
            'is_deathmatch': self.is_deathmatch,
            'description': self.description,
            'tools_used': self.tools_used,
            'known_bugs': self.known_bugs,
            'credits': self.credits,
            'build_time': self.build_time,
            'comments': self.comments,
        }

    @staticmethod
    def from_row(row: Dict):
        entry = Entry(
            row['collection'],
            row['path'],
            row['file_modified'],
            row['file_size'],
            row['entry_updated']
        )

        entry.id = row['id']
        # directory_id

        entry.title = row['title']
        entry.game = Game(row['game'])
        entry.engine = Engine(row['engine'])
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

        # maps
        # authors
        # text_contents
        # graphics
        # music

        return entry
