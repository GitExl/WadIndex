from pathlib import Path
from random import randrange
from typing import Optional, Set

from db.author_storage import AuthorStorage
from db.db import DB
from db.directory_storage import DirectoryStorage
from db.map_storage import MapStorage
from db.storage_base import StorageBase
from indexer.entry import Entry


class EntryStorage(StorageBase):

    def __init__(self, db: DB, authors: AuthorStorage, directories: DirectoryStorage, maps: MapStorage):
        super().__init__(db)

        self._authors = authors
        self._directories = directories
        self._maps = maps

    def get_by_path(self, collection: str, path: Path) -> Optional[Entry]:
        self.db.cursor.execute('SELECT * FROM entry WHERE COLLECTION=%s AND path=%s LIMIT 1', (collection, path.as_posix(),))

        row = self.db.cursor.fetchone()
        if row is None:
            return None

        return Entry.from_row(row)

    def get_timestamp_by_path(self, collection: str, path: Path) -> Optional[int]:
        self.db.cursor.execute('SELECT file_modified FROM entry WHERE COLLECTION=%s AND path=%s LIMIT 1', (collection, path.as_posix(),))

        row = self.db.cursor.fetchone()
        if row is None:
            return None

        return row['file_modified']

    def save(self, entry: Entry) -> int:
        (directory, _, _) = entry.path.rpartition('/')
        entry.directory_id = self._directories.get_or_create(directory, entry.collection)

        row = entry.to_row()

        args = list(row.values())
        if entry.id is not None:
            args.append(entry.id)
            set_stmt = ['{}=%s'.format(key) for key in row.keys()]
            query = 'UPDATE entry SET {} WHERE id=%s'.format(','.join(set_stmt))
        else:
            col_names = row.keys()
            value_subs = ['%s'] * len(row)
            query = 'INSERT INTO entry ({}) VALUES ({})'.format(','.join(col_names), ','.join(value_subs))
        self.db.cursor.execute(query, args)

        if entry.id is None:
            entry.id = self.db.cursor.lastrowid

        for map in entry.maps:
            self._maps.save(entry.id, map)

        if entry.text_contents is not None and len(entry.text_contents):
            self.db.cursor.execute('INSERT INTO entry_textfile VALUES (%s, %s) ON DUPLICATE KEY UPDATE text=%s', (
                entry.id,
                entry.text_contents,
                entry.text_contents,
            ))
        else:
            self.db.cursor.execute('DELETE FROM entry_textfile WHERE entry_id=%s', (entry.id,))

        self.db.cursor.execute('DELETE FROM entry_images WHERE entry_id=%s', (entry.id,))
        for name, graphic in entry.graphics.items():
            self.db.cursor.execute('INSERT INTO entry_images VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (
                entry.id,
                name,
                graphic.index,
                graphic.image.width,
                graphic.image.height,
                graphic.is_primary,
                graphic.aspect_ratio,
                randrange(0, 0xFFFFFFFF),
            ))

        self.db.cursor.execute('DELETE FROM entry_music WHERE entry_id=%s', (entry.id,))
        for name, music in entry.music.items():
            name = name[:63] if name is not None else None
            self.db.cursor.execute('INSERT INTO entry_music VALUES (%s, %s, %s)', (entry.id, music.id, name))

        self.db.cursor.execute('DELETE FROM entry_authors WHERE entry_id=%s', (entry.id,))
        author_ids = self._authors.get_or_create_multiple(entry.authors)
        for author_id in author_ids:
            self.db.cursor.execute('INSERT INTO entry_authors VALUES (%s, %s)', (entry.id, author_id))

        return entry.id

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM entry_textfile WHERE entry_id NOT IN (SELECT id FROM entry)')
        self.db.cursor.execute('DELETE FROM entry_images WHERE entry_id NOT IN (SELECT id FROM entry)')

    def remove_if_missing(self, collection: str, local_paths: Set[str]):

        self.db.cursor.execute('SELECT id, path FROM entry WHERE collection=%s', (collection,))
        path_rows = self.db.cursor.fetchall()
        db_paths = dict((path, id) for (id, path) in path_rows)

        for db_path, db_id in db_paths.items():
            if db_path in local_paths:
                continue

            self.db.cursor.execute('DELETE FROM entry WHERE id=%s', (db_id,))
            self.db.cursor.execute('DELETE FROM entry_authors WHERE entry_id=%s', (db_id,))
            self.db.cursor.execute('DELETE FROM entry_images WHERE entry_id=%s', (db_id,))
            self.db.cursor.execute('DELETE FROM entry_music WHERE entry_id=%s', (db_id,))
