import multiprocessing
import time
from math import ceil
from multiprocessing import Process, Queue, Lock
from pathlib import Path
from typing import Set, Dict, List
from optparse import OptionParser, OptionGroup

from indexer.entry import Entry
from indexer.indexer import Indexer
from indexer.storage import Storage
from utils.author_parser import Author
from utils.config import Config
from indexer.ignorelist import must_ignore, must_skip_graphics
from utils.logger import Logger
from utils.logger_stream import LoggerStream


def index_process(verbosity: int, stream_queue: Queue, task_queue: Queue, db_lock: Lock) -> None:
    config: Config = Config()
    logger: Logger = Logger(config.get('paths.logs'), stream_queue, verbosity)
    storage: Storage = Storage(config)

    indexer = Indexer(config, logger)

    for (collection, path_system, path_collection_file, start_time) in iter(task_queue.get, None):
        logger.info('Processing {}...'.format(path_collection_file))

        skip_graphics_reason = must_skip_graphics(path_collection_file)
        if skip_graphics_reason is not None:
            logger.info('Skipping graphics for {} because {}.'.format(path_system, skip_graphics_reason))

        info = indexer.index_file(path_system, path_collection_file, skip_graphics_reason is not None)
        if info is None:
            return None

        # Transfer indexed information to an entry.
        entry = storage.entries.get_by_path(collection, path_collection_file)
        if entry is None:
            entry = Entry(
                collection,
                info.path_idgames.as_posix(),
                info.file_modified,
                info.file_size,
                start_time,
                start_time,
            )
        else:
            entry.entry_updated = start_time
            entry.file_modified = info.file_modified
            entry.file_size = info.file_size

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
        author_set: Set[Author] = set(info.authors)
        for map in entry.maps:
            author_set.update(map.authors)
        entry.authors = author_set

        # Store or update entry.
        with db_lock:
            storage.transaction_commit()
            storage.transaction_start()
            for music in entry.music.values():
                storage.music.save(music)
            entry.id = storage.entries.save(entry)
            storage.transaction_commit()

    indexer.close()


def index(options):
    config = Config()

    logger_stream = LoggerStream(config.get('paths.logs'))
    logger = Logger(config.get('paths.logs'), logger_stream.queue, options.verbosity)
    logger_stream.start()

    storage = Storage(config)

    time_now = int(time.time())

    # Index a single file.
    paths_system: Dict[str, List[Path]]
    if options.filename:
        collection = None
        path_file_local = Path(options.filename)
        file_local = path_file_local.as_posix()
        for collection, path_collection in config.get('paths.collections').items():
            path_collection = Path(path_collection).as_posix()
            if file_local.startswith(path_collection):
                break

        if collection is None:
            logger.error('File to index is not part of a known collection.')
            return

        paths_system = {
            collection: [path_file_local]
        }

    # Get a list of files to index, per collection.
    else:
        paths_system = {}
        for collection, path_collection in config.get('paths.collections').items():
            collection_local_root = Path(path_collection)
            paths_system[collection] = list(collection_local_root.rglob('*.zip'))
            paths_system[collection].sort()

    # Determine number of processes to spawn.
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
        worker = Process(target=index_process, args=(options.verbosity, logger_stream.queue, task_queue, db_lock), name='index-{:02}'.format(i + 1))
        workers.append(worker)
        worker.start()

    # Generate tasks for each file that needs indexing.
    for collection, path_collections in paths_system.items():
        path_collection = config.get('paths.collections')[collection]

        for path_system in path_collections:
            path_collection_file = path_system.relative_to(path_collection)

            # Skip entries that do not need updating.
            if not options.force:
                timestamp = storage.entries.get_timestamp_by_path(collection, path_collection_file)
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

    # Stop logger stream.
    logger_stream.stop()
    logger_stream.join()

    storage.transaction_commit()


def clean(options):
    config = Config()
    logger = Logger(config.get('paths.logs'), options.verbosity)
    storage = Storage(config)

    # TODO: get local files and clean
    # Only remove dead entries if all entries were scanned.
    # Otherwise, any unscanned entries will also be removed.
    # if options.clean and not options.filename:
    #     logger.info('Removing dead entries...')
    #
    # for collection, paths_local in existing_paths.items():
    #     collection_path = self.config.get('paths.collections')[collection]
    #
    #     # Build a list of local paths relative to each collection.
    #     local_paths = set()
    #     for path_local in paths_local:
    #         local_paths.add(path_local.relative_to(collection_path).as_posix())
    #
    #     storage.remove_dead_entries(paths_system, local_paths)

    logger.info('Removing orphaned maps...')
    storage.maps.remove_orphans()
    logger.info('Removing orphaned entries...')
    storage.entries.remove_orphans()
    logger.info('Removing orphaned music...')
    storage.music.remove_orphans()
    logger.info('Removing orphaned authors...')
    storage.authors.remove_orphans()
    logger.info('Removing empty directories...')
    storage.directories.remove_orphans()

    storage.transaction_commit()


def run():
    parser = OptionParser('Usage: index.py action [options]')

    parser.add_option("--verbosity", dest="verbosity",
                      default=Logger.VERBOSITY_INFO, type='int',
                      help="Set visible logging verbosity level. From 0 for least to 4 for most verbose.")

    group = OptionGroup(parser, '"index" action', 'Index all collections or a single file.')
    group.add_option("--processes", dest="processes",
                      default=0, type='int',
                      help="Sets the number of CPU processes to use. Use a value less than 1 to autodetect (the default).")
    group.add_option("--file", dest="filename",
                      help="The full path to a single file to index. Must be used together with --index.")
    group.add_option("--force", dest="force",
                      action="store_true", default=False,
                      help="Force indexing entries even if their files have not changed.")
    parser.add_option_group(group)

    group = OptionGroup(parser, '"clean" action', 'Clean database from deleted or orphaned data.')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    if not len(args):
        parser.error('Missing action argument.')

    action = args[0].lower()
    if action == 'index':
        index(options)
    elif action == 'clean':
        clean(options)
    else:
        parser.error('Unknown action argument "{}"'.format(action))


run()
