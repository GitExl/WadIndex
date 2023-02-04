from db.storage_base import StorageBase


class DirectoryStorage(StorageBase):

    def get_or_create(self, directory_path: str, collection: str) -> int:
        if directory_path.find('/'):
            (directory_parent, _, directory_name) = directory_path.rpartition('/')
        else:
            directory_parent = None
            directory_name = directory_path

        self.db.cursor.execute('SELECT id FROM directories WHERE collection=%s AND path=%s LIMIT 1',
                            (collection, directory_path,))
        row = self.db.cursor.fetchone()
        if row is not None:
            return row['id']

        if directory_parent:
            directory_parent_id = self.get_or_create(directory_parent, collection)
        else:
            directory_parent_id = None

        self.db.cursor.execute('INSERT INTO directories (parent_id, collection, path, name) VALUES (%s, %s, %s, %s)',
                            (directory_parent_id, collection, directory_path, directory_name,))
        return self.db.cursor.lastrowid

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM directories WHERE id NOT IN (SELECT DISTINCT directory_id FROM entry) AND id NOT IN (SELECT parent_id FROM directories)')
