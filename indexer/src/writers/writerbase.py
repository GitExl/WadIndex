from extractors.extractedinfo import ExtractedInfo
from indexer.dbstorage import DBStorage
from utils.config import Config
from utils.logger import Logger


class WriterBase:

    def __init__(self, logger: Logger, config: Config, storage: DBStorage):
        self.logger: Logger = logger
        self.config: Config = config
        self.storage: DBStorage = storage

    def write(self, info: ExtractedInfo):
        pass

    def close(self):
        pass
