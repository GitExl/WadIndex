from typing import Iterable, Set

from db.storage_base import StorageBase
from utils.url_clean import url_clean


class AuthorStorage(StorageBase):

    def get_or_create_multiple(self, authors: Iterable[str]) -> Set[int]:
        author_ids = set()
        for author_name in authors:
            path_alias = url_clean(author_name)
            if len(path_alias) < 2:
                continue

            self.db.cursor.execute('SELECT id FROM authors WHERE name=%s LIMIT 1', (author_name,))
            row = self.db.cursor.fetchone()
            if row is not None:
                author_id = row['id']
            else:
                self.db.cursor.execute('INSERT INTO authors (name, path_alias) VALUES (%s, %s)', (author_name[:255], path_alias))
                author_id = self.db.cursor.lastrowid

            author_ids.add(author_id)

        return author_ids

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM authors WHERE id NOT IN (SELECT DISTINCT author_id FROM entry_authors UNION SELECT DISTINCT author_id FROM map_authors)')