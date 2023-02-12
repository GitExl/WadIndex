from typing import Iterable, Set

from db.storage_base import StorageBase
from utils.author_parser import Author


class AuthorStorage(StorageBase):

    def get_or_create_multiple(self, authors: Iterable[Author]) -> Set[int]:
        author_ids = set()
        for author in authors:
            if len(author.alias) < 2:
                continue

            self.db.cursor.execute('SELECT id FROM authors WHERE alias=%s LIMIT 1', (author.alias,))
            row = self.db.cursor.fetchone()
            if row is not None:
                author_id = row['id']
            else:
                self.db.cursor.execute('INSERT INTO authors (name, full_name, nickname, alias) VALUES (%s, %s, %s, %s)', (
                    author.name[:255],
                    author.full_name[:255] if author.full_name else None,
                    author.nickname[:127] if author.nickname else None,
                    author.alias[:255],
                ))
                author_id = self.db.cursor.lastrowid

            author_ids.add(author_id)

        return author_ids

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM authors WHERE id NOT IN (SELECT DISTINCT author_id FROM entry_authors UNION SELECT DISTINCT author_id FROM map_authors)')