from db.db import DB


class StorageBase:

    def __init__(self, db: DB):
        self.db: DB = db
