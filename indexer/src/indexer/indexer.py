from pathlib import Path
from typing import List, Optional, Tuple

from extractors.archiveextractor import ArchiveExtractor
from extractors.archivelistextractor import ArchiveListExtractor
from extractors.dehackedextractor import DehackedExtractor
from extractors.engineextractor import EngineExtractor
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from extractors.filetypeextractor import FileTypeExtractor
from extractors.gameextractor import GameExtractor
from extractors.languageextractor import LanguageExtractor
from extractors.mapextractor import MapExtractor
from extractors.graphicsextractor import GraphicsExtractor
from extractors.mapinfoextractor import MapInfoExtractor
from extractors.musicextractor import MusicExtractor
from extractors.propertyextractor import PropertyExtractor
from extractors.textextractor import TextExtractor

from utils.config import Config
from utils.logger import Logger
from writers.mappreviewwriter import MapPreviewWriter

from writers.musicwriter import MusicWriter
from writers.writerbase import WriterBase
from writers.graphicswriter import GraphicsWriter

from indexer.dbstorage import DBStorage


EXTRACTORS = [
    ArchiveExtractor,
    TextExtractor,
    GameExtractor,
    PropertyExtractor,
    ArchiveListExtractor,
    FileTypeExtractor,
    LanguageExtractor,
    MapExtractor,
    DehackedExtractor,
    MapInfoExtractor,
    MusicExtractor,
    EngineExtractor,
    GraphicsExtractor,
]

WRITERS = [
    GraphicsWriter,
    MusicWriter,
    MapPreviewWriter,
]


class Indexer:

    def __init__(self, config: Config, logger: Logger, storage: DBStorage):
        self.config: Config = config
        self.logger: Logger = logger
        self.storage: DBStorage = storage

        # Initialize processor instances.
        self.extractors: List[ExtractorBase] = []
        for extractor_class in EXTRACTORS:
            self.extractors.append(extractor_class(logger, config))

        self.writers: List[WriterBase] = []
        for writer_class in WRITERS:
            self.writers.append(writer_class(logger, config, storage))

    def index_file(self, path_local: Path, path_collection: Path) -> ExtractedInfo:
        path_local_base = path_local.parents[0] / path_local.stem
        path_collection_base = path_collection.parents[0] / path_collection.stem
        filename_base = path_local.stem

        stat = path_local.stat()
        info = ExtractedInfo(
            path_local,
            path_local_base,
            path_collection,
            path_collection_base,
            filename_base,
            stat.st_size,
            int(stat.st_mtime),
        )

        # Run all extractors and writers in sequence.
        for extractor in self.extractors:
            extractor.extract(info)
        for writer in self.writers:
            writer.write(info)

        # Clean up extractors.
        for extractor in reversed(self.extractors):
            extractor.cleanup(info)

        return info

    def close(self):

        # Close extractor and writer classes.
        for writer in reversed(self.writers):
            writer.close()
        for extractor in reversed(self.extractors):
            extractor.close()

