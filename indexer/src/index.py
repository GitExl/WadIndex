import cProfile
import multiprocessing
import os
import time
from math import ceil
from multiprocessing import Process, Queue, Lock
from pathlib import Path
from typing import Set, Dict, List
from optparse import OptionParser

from indexer.dbstorage import DBStorage
from indexer.entry import Entry
from indexer.indexer import Indexer
from utils.config import Config
from indexer.ignorelist import must_ignore
from utils.logger import Logger


class IndexProcess(Process):

    def __init__(self, verbosity: int, task_queue: Queue, db_lock: Lock):
        Process.__init__(self)

        self.config: Config = Config()
        self.logger: Logger = Logger(self.config.get('paths.logs'), verbosity)
        self.storage: DBStorage = DBStorage(self.config)
        self.db_lock: Lock = db_lock

        self.task_queue: Queue = task_queue

    def run(self) -> None:
        indexer = Indexer(self.config, self.logger, self.storage)

        for (collection, path_system, path_collection_file, start_time) in iter(self.task_queue.get, None):
            self.logger.info('Processing {}...'.format(path_collection_file))

            info = indexer.index_file(path_system, path_collection_file)
            if info is None:
                return None

            # Transfer indexed information to an entry.
            entry = self.storage.get_entry_by_path(collection, path_collection_file)
            if entry is None:
                entry = Entry(
                    collection,
                    info.path_idgames.as_posix(),
                    info.file_modified,
                    info.file_size,
                    start_time
                )
            else:
                entry.entry_updated = start_time

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
            entry.maps = info.maps
            entry.text_contents = info.text_contents
            entry.graphics = info.graphics
            entry.music = info.music

            # Combine authors from the main entry and every map.
            author_set: Set[str] = set(info.authors)
            for map in entry.maps:
                author_set.update(map.authors)
            entry.authors = author_set

            # Store or update entry.
            self.db_lock.acquire()
            entry.id = self.storage.save_entry(entry)
            self.storage.save_entry_authors(entry, entry.authors)
            self.storage.save_entry_maps(entry, entry.maps)
            self.storage.save_entry_textfile(entry, entry.text_contents)
            self.storage.save_entry_images(entry, entry.graphics)
            self.storage.save_entry_music(entry, entry.music)
            self.storage.commit()
            self.db_lock.release()

        indexer.close()


def run():
    parser = OptionParser()
    parser.add_option("--index", dest="index",
                      action="store_true", default=False,
                      help="Index new or updated entries.")
    parser.add_option("--processes", dest="processes",
                      default=0, type='int',
                      help="Sets the number of CPU processes to use. Use a value less than 1 to autodetect.")
    parser.add_option("--file", dest="filename",
                      help="Index a single file only (must be used together with --index).")
    parser.add_option("--force", dest="force",
                      action="store_true", default=False,
                      help="Force indexing entries even if their files have not changed.")
    parser.add_option("--clean", dest="clean",
                      action="store_true", default=False,
                      help="Cleans up database.")
    parser.add_option("--verbosity", dest="verbosity",
                      default=Logger.VERBOSITY_INFO, type='int',
                      help="Set visible logging verbosity level. From 0 for least to 4 for most verbose.")

    (options, args) = parser.parse_args()

    config = Config()
    logger = Logger(config.get('paths.logs'), options.verbosity)

    logger.info('Setting up...')
    storage = DBStorage(config)

    if options.index:
        time_now = int(time.time())

        # Get a list of files to index, per collection.
        paths_system: Dict[str, List[Path]]
        if options.filename:
            collection = 'idgames'   # TODO: detect from path
            paths_system = {
                collection: [Path(options.filename)]
            }
        else:
            paths_system = {}
            for collection, path_collection in config.get('paths.collections').items():
                collection_local_root = Path(path_collection)
                paths_system[collection] = list(collection_local_root.rglob('*.zip'))
                paths_system[collection].sort()

        if options.processes > 0:
            proc_count = options.processes
        else:
            proc_count = max(ceil(multiprocessing.cpu_count() * 0.6) - 1, 1)
        logger.info('Using {} processes.'.format(proc_count))

        # Start worker processes.
        task_queue = Queue()
        db_lock = Lock()
        workers = []
        for i in range(proc_count):
            worker = IndexProcess(options.verbosity, task_queue, db_lock)
            workers.append(worker)
            worker.start()

        # Generate tasks for each file that needs indexing.
        for collection, path_collections in paths_system.items():
            path_collection = config.get('paths.collections')[collection]

            for path_system in path_collections:
                path_collection_file = path_system.relative_to(path_collection)

                # Skip entries that do not need updating.
                if not options.force:
                    timestamp = storage.get_entry_timestamp_by_path(collection, path_collection_file)
                    if timestamp is not None and timestamp >= int(path_system.stat().st_mtime):
                        logger.decision('Skipping {}.'.format(path_system))
                        continue

                # Ignore some files we'd rather not analyse.
                ignore_reason = must_ignore(path_collection_file)
                if ignore_reason is not None:
                    logger.decision('Ignoring {} because: {}'.format(path_system, ignore_reason))
                    continue

                task_queue.put((collection, path_system, path_collection_file, time_now))

        # Instruct processes to terminate.
        for _ in range(proc_count):
            task_queue.put(None)

        # Wait for processes to complete.
        for worker in workers:
            worker.join()

        # Only remove dead entries if all entries were scanned.
        # Otherwise, any unscanned entries will also be removed.
        if options.clean and not options.filename:
            logger.info('Removing dead entries...')
            storage.remove_dead_entries(paths_system)

    if options.clean:
        logger.info('Removing orphaned maps...')
        storage.remove_orphan_maps()
        logger.info('Removing orphaned text files...')
        storage.remove_orphan_textfiles()
        logger.info('Removing orphaned images...')
        storage.remove_orphan_images()
        logger.info('Removing orphaned music...')
        storage.remove_orphan_music()
        logger.info('Removing orphaned authors...')
        storage.remove_orphan_authors()
        logger.info('Removing empty directories...')
        storage.remove_orphan_directories()

    storage.commit()
    storage.close()


#cProfile.run('run()', sort='tottime')
run()
