import cProfile
import time
from pathlib import Path
from typing import List, Optional, Tuple
from optparse import OptionParser

from extractors.archiveextractor import ArchiveExtractor
from extractors.archivelistextractor import ArchiveListExtractor
from extractors.engineextractor import EngineExtractor
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from extractors.filetypeextractor import FileTypeExtractor
from extractors.gameextractor import GameExtractor
from extractors.levelextractor import LevelExtractor
from extractors.graphicsextractor import GraphicsExtractor
from extractors.mapinfoextractor import MapInfoExtractor
from extractors.musicextractor import MusicExtractor
from extractors.propertyextractor import PropertyExtractor
from extractors.textextractor import TextExtractor
from idgames.dbstorage import DBStorage
from idgames.entry import Entry
from utils.config import Config
from writers.appdatabasewriter import AppDatabaseWriter

from writers.graphicswriter import GraphicsWriter

from idgames.ignorelist import must_ignore
from utils.logger import Logger
from writers.musicwriter import MusicWriter
from writers.writerbase import WriterBase


EXTRACTORS = [
    ArchiveExtractor,
    TextExtractor,
    GameExtractor,
    PropertyExtractor,
    ArchiveListExtractor,
    FileTypeExtractor,
    MusicExtractor,
    LevelExtractor,
    MapInfoExtractor,
    EngineExtractor,
    GraphicsExtractor,
]

WRITERS = [
    GraphicsWriter,
    # AppDatabaseWriter,
    MusicWriter,
]


class Extract:

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

    def process_file(self, path_local: Path, force_update: bool) -> Tuple[Optional[ExtractedInfo], Optional[Entry]]:
        path_local_base = path_local.parents[0] / path_local.stem
        path_idgames = path_local.relative_to(self.config.get('paths.idgames'))
        path_idgames_base = path_idgames.parents[0] / path_idgames.stem
        filename_base = path_local.stem

        self.logger.info('Processing {}...'.format(path_idgames))
        entry = self.storage.get_entry_by_path(path_idgames)

        # Bail if the file has not been updated since the last scan.
        if not force_update and entry is not None and entry.file_modified >= int(path_local.stat().st_mtime):
            self.logger.decision('Skipping {} because it is not updated.'.format(path_idgames))
            return None, None

        # Ignore some files we'd rather not analyse.
        ignore_reason = must_ignore(path_idgames)
        if ignore_reason is not None:
            self.logger.decision('Ignoring {} because: {}'.format(path_idgames, ignore_reason))
            return None, None

        info = ExtractedInfo(
            path_local,
            path_local_base,
            path_idgames,
            path_idgames_base,
            filename_base,
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


def run():
    parser = OptionParser()
    parser.add_option("--file", dest="filename",
                      help="Extract info from a single file only.")
    parser.add_option("--force", dest="force",
                      action="store_true", default=False,
                      help="Force updates of entries even if they have not changed.")
    parser.add_option("--clean", dest="clean",
                      action="store_true", default=False,
                      help="Cleans up database after processing.")
    parser.add_option("--verbosity", dest="verbosity",
                      default=Logger.VERBOSITY_INFO, type='int',
                      help="Set visible logging verbosity level. From 0 for least to 4 for most verbose.")

    (options, args) = parser.parse_args()

    config = Config()
    logger = Logger(config.get('paths.logs'), options.verbosity)

    logger.info('Setting up...')
    storage = DBStorage(config)
    extract = Extract(config, logger, storage)

    time_now = int(time.time())

    if options.filename:
        paths_system = [Path(options.filename)]
    else:
        idgames_local_root = Path(config.get('paths.idgames'))
        paths_system = list(idgames_local_root.rglob('*.zip'))

    for path_system in paths_system:
        info, entry = extract.process_file(path_system, options.force)
        if info is None:
            continue

        if entry is None:
            entry = Entry(
                info.path_idgames.as_posix(),
                int(info.path_local.stat().st_mtime),
                time_now,
            )
        else:
            entry.entry_updated = time_now

        entry.title = info.title
        entry.game = info.game
        entry.engine = info.engine
        entry.is_singleplayer = info.is_singleplayer
        entry.is_cooperative = info.is_cooperative
        entry.is_deathmatch = info.is_deathmatch
        entry.description = info.description
        entry.tools_used = info.tools_used
        entry.known_bugs = info.known_bugs
        entry.credits = info.credits
        entry.build_time = info.build_time
        entry.comments = info.comments

        entry.id = storage.save_entry(entry)
        storage.save_entry_authors(entry, info.authors)
        storage.save_entry_levels(entry, info.levels)
        storage.save_entry_textfile(entry, info.text_contents)
        storage.save_entry_images(entry, info.graphics)
        storage.save_entry_music(entry, info.music)
        storage.commit()

    if options.clean:

        # Only remove dead entries if all entries were scanned.
        if not options.filename:
            logger.info('Removing dead entries...')
            storage.remove_dead_entries(paths_system)

        logger.info('Removing orphaned authors...')
        storage.remove_orphan_authors()
        logger.info('Removing orphaned levels...')
        storage.remove_orphan_levels()
        logger.info('Removing orphaned text files...')
        storage.remove_orphan_textfiles()
        logger.info('Removing orphaned images...')
        storage.remove_orphan_images()
        logger.info('Removing orphaned music...')
        storage.remove_orphan_music()

    storage.commit()

    storage.close()
    extract.close()


#cProfile.run('run()', sort='tottime')
run()
