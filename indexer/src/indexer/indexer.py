from pathlib import Path
from typing import List, Optional, Tuple

from extractors.archiveextractor import ArchiveExtractor
from extractors.archivelistextractor import ArchiveListExtractor
from extractors.engineextractor import EngineExtractor
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from extractors.filetypeextractor import FileTypeExtractor
from extractors.gameextractor import GameExtractor
from extractors.mapextractor import MapExtractor
from extractors.graphicsextractor import GraphicsExtractor
from extractors.mapinfoextractor import MapInfoExtractor
from extractors.musicextractor import MusicExtractor
from extractors.propertyextractor import PropertyExtractor
from extractors.textextractor import TextExtractor

from utils.config import Config
from utils.logger import Logger

from writers.musicwriter import MusicWriter
from writers.writerbase import WriterBase
from writers.graphicswriter import GraphicsWriter

from indexer.dbstorage import DBStorage
from indexer.entry import Entry
from indexer.ignorelist import must_ignore


EXTRACTORS = [
    ArchiveExtractor,
    TextExtractor,
    GameExtractor,
    PropertyExtractor,
    ArchiveListExtractor,
    FileTypeExtractor,
    MusicExtractor,
    MapExtractor,
    MapInfoExtractor,
    EngineExtractor,
    GraphicsExtractor,
]

WRITERS = [
    GraphicsWriter,
    MusicWriter,
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

    def process_file(self, collection: str, path_local: Path, force_update: bool) -> Tuple[Optional[ExtractedInfo], Optional[Entry]]:
        path_local_base = path_local.parents[0] / path_local.stem
        path_collection = path_local.relative_to(self.config.get('paths.collections')[collection])
        path_collection_base = path_collection.parents[0] / path_collection.stem
        filename_base = path_local.stem

        self.logger.info('Processing {}...'.format(path_collection))
        entry = self.storage.get_entry_by_path(path_collection)

        # Bail if the file has not been updated since the last scan.
        if not force_update and entry is not None and entry.file_modified >= int(path_local.stat().st_mtime):
            self.logger.decision('Skipping {} because it is not updated.'.format(path_collection))
            return None, None

        # Ignore some files we'd rather not analyse.
        ignore_reason = must_ignore(path_collection)
        if ignore_reason is not None:
            self.logger.decision('Ignoring {} because: {}'.format(path_collection, ignore_reason))
            return None, None

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

        return info, entry

    def close(self):
        # Close extractor and writer classes.
        for writer in reversed(self.writers):
            writer.close()
        for extractor in reversed(self.extractors):
            extractor.close()

