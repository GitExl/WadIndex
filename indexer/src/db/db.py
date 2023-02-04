from mysql.connector import MySQLConnection, connection
from mysql.connector.cursor import CursorBase

from utils.config import Config


class DB:

    def __init__(self, config: Config):
        self._db: MySQLConnection = connection.MySQLConnection(
            user=config.get('db.user'),
            password=config.get('db.password'),
            host=config.get('db.host'),
            database=config.get('db.database'),
        )
        self._db.autocommit = False

        self._cursor: CursorBase = self._db.cursor(dictionary=True)

    def transaction_start(self):
        self._db.start_transaction()

    def transaction_commit(self):
        self._db.commit()

    def close(self):
        self._cursor.close()
        self._db.close()

    @property
    def cursor(self) -> CursorBase:
        return self._cursor
