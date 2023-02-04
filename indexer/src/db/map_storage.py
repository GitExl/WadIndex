from db.author_storage import AuthorStorage
from db.db import DB
from db.storage_base import StorageBase
from doom.map.map import Map


class MapStorage(StorageBase):

    def __init__(self, db: DB, authors: AuthorStorage):
        super().__init__(db)

        self._authors = authors

    def save(self, entry_id: int, map: Map):
        fields = [
            'entry_id',
            'name',
            'title',
            'format',
            'line_count',
            'side_count',
            'thing_count',
            'sector_count',
            'allow_jump',
            'allow_crouch',
            'par_time',
            'music',
            'next',
            'next_secret',
            'cluster',
            'complexity',
            'nodes',
            'nodes_gl',
        ]
        fields_concat = ','.join(fields)
        fields_concat_placeholder = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'

        self.db.cursor.execute(
            'INSERT INTO maps ({}) VALUES ({})'.format(fields_concat, fields_concat_placeholder),
            (
                entry_id,
                map.name[:8],
                map.title[:1022] if map.title is not None else None,
                map.format.value,
                len(map.lines),
                len(map.sides),
                len(map.things),
                len(map.sectors),
                map.allow_jump,
                map.allow_crouch,
                map.par_time & 0xFFFFFFFF if map.par_time is not None else None,
                map.music[:255] if map.music is not None else None,
                map.next[:255] if map.next is not None else None,
                map.next_secret[:255] if map.next_secret is not None else None,
                map.cluster & 0xFFFFFFFF if map.cluster is not None else None,
                map.complexity,
                map.nodes_type.value,
                map.nodes_gl_type.value,
            )
        )
        db_id = self.db.cursor.lastrowid

        # Add authors.
        author_ids = self._authors.get_or_create_multiple(map.authors)
        for author_id in author_ids:
            self.db.cursor.execute('INSERT INTO map_authors VALUES (%s, %s)', (db_id, author_id))

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM maps WHERE entry_id NOT IN (SELECT id FROM entry)')