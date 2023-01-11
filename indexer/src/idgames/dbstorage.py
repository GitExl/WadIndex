from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple

from mysql.connector import MySQLConnection, connection

from doom.map import Map, MAP_FORMAT_TO_INT
from extractors.musicextractor import MusicInfo
from idgames.entry import Entry
from utils.config import Config
import re

from extractors.extractedinfo import GraphicInfo


class DBStorage:

    RE_URL_CLEAN = re.compile(r'[^\w\-]')
    RE_URL_DEDUP = re.compile(r'[\-]{2,}')

    def __init__(self, config: Config):
        self.config: Config = config

        self.db: MySQLConnection = connection.MySQLConnection(
            user=config.get('db.user'),
            password=config.get('db.password'),
            host=config.get('db.host'),
            database=config.get('db.database'),
        )
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def get_entry_by_path(self, path: Path) -> Optional[Entry]:
        self.cursor.execute('SELECT * FROM entry WHERE path=%s LIMIT 1', (path.as_posix(),))

        row = self.cursor.fetchone()
        if row is None:
            return None

        return Entry.from_row(dict(zip(self.cursor.column_names, row)))

    def save_entry(self, entry: Entry) -> int:
        (directory, _, _) = entry.path.rpartition('/')
        entry.directory_id = self.get_or_create_directory_id(directory, entry.collection)

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
        self.cursor.execute(query, args)

        if entry.id is None:
            entry.id = self.cursor.lastrowid

        return entry.id

    def get_or_create_directory_id(self, directory_path: str, collection: str) -> int:
        if directory_path.find('/'):
            (directory_parent, _, directory_name) = directory_path.rpartition('/')
        else:
            directory_parent = None
            directory_name = directory_path

        self.cursor.execute('SELECT id FROM directories WHERE collection=%s AND path=%s LIMIT 1', (collection, directory_path,))
        directory_row = self.cursor.fetchone()
        if directory_row is not None:
            return directory_row[0]

        if directory_parent:
            directory_parent_id = self.get_or_create_directory_id(directory_parent, collection)
        else:
            directory_parent_id = None

        self.cursor.execute('INSERT INTO directories (parent_id, collection, path, name) VALUES (%s, %s, %s, %s)', (directory_parent_id, collection, directory_path, directory_name,))
        return self.cursor.lastrowid

    def remove_orphan_directories(self):
        self.cursor.execute('DELETE FROM directories WHERE id NOT IN (SELECT DISTINCT directory_id FROM entry) AND id NOT IN (SELECT parent_id FROM directories)')

    def save_entry_authors(self, entry: Entry, authors: List[str]):

        # Update (remove + re-add) authors.
        self.cursor.execute('DELETE FROM entry_authors WHERE entry_id=%s', (entry.id,))

        known_author_ids = set()
        for author_name in authors:
            path_alias = self.url_clean(author_name)
            if len(path_alias) < 2:
                continue

            self.cursor.execute('SELECT id FROM author WHERE name=%s LIMIT 1', (author_name,))
            author_row = self.cursor.fetchone()
            if author_row is not None:
                author_id = author_row[0]

                # In some cases the same author can appear multiple times.
                if author_id in known_author_ids:
                    continue

            else:
                self.cursor.execute('INSERT INTO author (name, path_alias) VALUES (%s, %s)', (author_name[:255], path_alias))
                author_id = self.cursor.lastrowid

            self.cursor.execute('INSERT INTO entry_authors VALUES (%s, %s)', (entry.id, author_id))
            known_author_ids.add(author_id)

    def save_entry_maps(self, entry: Entry, entry_maps: List[Map]):
        self.cursor.execute('DELETE FROM maps WHERE entry_id=%s', (entry.id,))

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
        ]
        fields_concat = ','.join(fields)
        fields_concat_placeholder = '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'

        for entry_map in entry_maps:
            self.cursor.execute(
                'INSERT INTO maps ({}) VALUES ({})'.format(fields_concat, fields_concat_placeholder),
                (
                    entry.id,
                    entry_map.name[:8],
                    entry_map.title[:1022] if entry_map.title is not None else None,
                    MAP_FORMAT_TO_INT.get(entry_map.format),
                    len(entry_map.lines),
                    len(entry_map.sides),
                    len(entry_map.things),
                    len(entry_map.sectors),
                    entry_map.allow_jump,
                    entry_map.allow_crouch,
                    entry_map.par_time & 0xFFFFFFFF if entry_map.par_time is not None else None,
                    entry_map.music[:255] if entry_map.music is not None else None,
                    entry_map.next[:255] if entry_map.next is not None else None,
                    entry_map.next_secret[:255] if entry_map.next_secret is not None else None,
                    entry_map.cluster & 0xFFFFFFFF if entry_map.cluster is not None else None
                )
            )

    def save_entry_textfile(self, entry: Entry, text_file: Optional[str]):
        self.cursor.execute('DELETE FROM entry_textfile WHERE entry_id=%s', (entry.id,))
        if text_file is not None and len(text_file):
            self.cursor.execute('INSERT INTO entry_textfile VALUES (%s, %s)', (entry.id, text_file))

    def save_entry_images(self, entry: Entry, graphics: Dict[str, GraphicInfo]):
        self.cursor.execute('DELETE FROM entry_images WHERE entry_id=%s', (entry.id,))
        for name, graphic in graphics.items():
            self.cursor.execute('INSERT INTO entry_images VALUES (%s, %s, %s, %s, %s)', (entry.id, name, graphic.image.width, graphic.image.height, graphic.is_primary))

    def save_entry_music(self, entry: Entry, music: Dict[str, MusicInfo]):
        self.cursor.execute('DELETE FROM entry_music WHERE entry_id=%s', (entry.id,))
        for name, music in music.items():
            self.cursor.execute('INSERT INTO entry_music VALUES (%s, %s, %s)', (entry.id, music.id, name))

    def remove_orphan_authors(self):
        self.cursor.execute('DELETE FROM author WHERE id NOT IN (SELECT DISTINCT author_id FROM entry_authors)')

    def remove_orphan_maps(self):
        self.cursor.execute('DELETE FROM maps WHERE entry_id NOT IN (SELECT id FROM entry)')

    def remove_orphan_textfiles(self):
        self.cursor.execute('DELETE FROM entry_textfile WHERE entry_id NOT IN (SELECT id FROM entry)')

    def remove_orphan_images(self):
        self.cursor.execute('DELETE FROM entry_images WHERE entry_id NOT IN (SELECT id FROM entry)')

    def remove_orphan_music(self):
        self.cursor.execute('DELETE FROM entry_music WHERE entry_id NOT IN (SELECT id FROM entry)')

    def remove_dead_entries(self, existing_paths: List[Path]):
        local_paths = set()
        for path_local in existing_paths:
            local_paths.add(path_local.relative_to(self.config.get('paths.idgames')).as_posix())

        self.cursor.execute('SELECT id, path FROM entry')
        path_rows = self.cursor.fetchall()
        db_paths = dict((path, id) for (id, path) in path_rows)

        for db_path, db_id in db_paths.items():
            if db_path in local_paths:
                continue

            self.cursor.execute('DELETE FROM entry WHERE id=%s', (db_id,))

    def find_music_by_hash(self, data_hash: bytes) -> Optional[int]:
        self.cursor.execute('SELECT id FROM music WHERE hash=%s', (data_hash,))
        music_row = self.cursor.fetchone()
        if music_row is not None:
            return music_row[0]

        return None

    def save_music(self, music: MusicInfo) -> int:
        row = music.to_row()
        args = list(row.values())

        if music.id:
            args.append(music.id)
            set_stmt = ['{}=%s'.format(key) for key in row.keys()]
            query = 'UPDATE music SET {} WHERE id=%s'.format(','.join(set_stmt))

        else:
            col_names = row.keys()
            value_subs = ['%s'] * len(row)
            query = 'INSERT INTO music ({}) VALUES ({})'.format(','.join(col_names), ','.join(value_subs))
        self.cursor.execute(query, args)

        if music.id is None:
            music.id = self.cursor.lastrowid

        return music.id

    def commit(self):
        self.db.commit()

    def url_clean(self, url: str) -> str:
        url = url.replace(' ', '-').replace('_', '-').lower()
        url = self.RE_URL_CLEAN.sub('', url)
        url = self.RE_URL_DEDUP.sub('-', url)
        return url[:255].strip()

    def rebuild_directory(self):
        directories: Set[Tuple[str, str]] = set()

        self.cursor.execute('SELECT path FROM entry')
        for path in self.cursor.fetchall():
            (directory, _, _) = path[0].rpartition('/')
            if directory.find('/'):
                (parent, _, _) = directory.rpartition('/')
            else:
                parent = None

            directories.add((directory, parent))

        print(directories)