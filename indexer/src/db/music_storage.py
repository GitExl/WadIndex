from db.storage_base import StorageBase
from extractors.extractedinfo import MusicInfo


class MusicStorage(StorageBase):

    def save(self, music: MusicInfo):
        row = music.to_row()
        args = list(row.values())

        self.db.cursor.execute('SELECT id FROM music WHERE hash=%s LIMIT 1', (music.hash,))
        existing_row = self.db.cursor.fetchone()

        if existing_row is not None:
            set_stmt = ['{}=%s'.format(key) for key in row.keys()]
            existing_id = existing_row['id']
            query = 'UPDATE music SET {} WHERE id={}'.format(','.join(set_stmt), existing_id)
            self.db.cursor.execute(query, args)
            music.id = existing_id

        else:
            col_names = row.keys()
            value_subs = ['%s'] * len(row)
            query = 'INSERT INTO music ({}) VALUES ({})'.format(','.join(col_names), ','.join(value_subs))
            self.db.cursor.execute(query, args)
            music.id = self.db.cursor.lastrowid

    def remove_orphans(self):
        self.db.cursor.execute('DELETE FROM music WHERE id NOT IN (SELECT entry_id FROM entry_music)')