from db.author_storage import AuthorStorage
from db.db import DB
from db.directory_storage import DirectoryStorage
from db.entry_storage import EntryStorage
from db.map_storage import MapStorage
from db.music_storage import MusicStorage
from utils.config import Config


class Storage:

    def __init__(self, config: Config):
        self._db = DB(config)
        self._authors = AuthorStorage(self._db)
        self._directories = DirectoryStorage(self._db)
        self._maps = MapStorage(self._db, self._authors)
        self._entries = EntryStorage(self._db, self._authors, self._directories, self._maps)
        self._music = MusicStorage(self._db)

    @property
    def authors(self) -> AuthorStorage:
        return self._authors

    @property
    def directories(self) -> DirectoryStorage:
        return self._directories

    @property
    def entries(self) -> EntryStorage:
        return self._entries

    @property
    def maps(self) -> MapStorage:
        return self._maps

    @property
    def music(self) -> MusicStorage:
        return self._music

    def transaction_commit(self):
        self._db.transaction_commit()

    def transaction_start(self):
        self._db.transaction_start()
