from db.author_storage import AuthorStorage
from db.db import DB
from db.storage_base import StorageBase
from doom.map.map import Map


class MapStorage(StorageBase):

    def __init__(self, db: DB, authors: AuthorStorage):
        super().__init__(db)

        self._authors = authors

    def save(self, entry_id: int, map: Map):
        map.entry_id = entry_id
        row = map.to_row()
        args = list(row.values())

        self.db.cursor.execute('SELECT id FROM maps WHERE entry_id=%s AND name=%s LIMIT 1', (row['entry_id'], row['name'],))
        existing_row = self.db.cursor.fetchone()

        if existing_row is not None:
            set_stmt = ['{}=%s'.format(key) for key in row.keys()]
            existing_id = existing_row['id']
            query = 'UPDATE maps SET {} WHERE id={}'.format(','.join(set_stmt), existing_id)
            self.db.cursor.execute(query, args)
            map.id = existing_id

        else:
            col_names = row.keys()
            value_subs = ['%s'] * len(row)
            query = 'INSERT INTO maps ({}) VALUES ({})'.format(','.join(col_names), ','.join(value_subs))
            self.db.cursor.execute(query, args)
            map.id = self.db.cursor.lastrowid

        # Re-add authors.
        self.db.cursor.execute('DELETE FROM map_authors WHERE map_id=%s', (map.id,))
        author_ids = self._authors.get_or_create_multiple(map.authors)
        for author_id in author_ids:
            self.db.cursor.execute('INSERT INTO map_authors VALUES (%s, %s)', (map.id, author_id))

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM maps WHERE entry_id NOT IN (SELECT id FROM entry)')