import cProfile
import time
from pathlib import Path
from typing import Set, Dict, List
from optparse import OptionParser

from indexer.dbstorage import DBStorage
from indexer.entry import Entry
from indexer.indexer import Indexer
from utils.config import Config

from utils.logger import Logger


def run():
    parser = OptionParser()
    parser.add_option("--index", dest="index",
                      action="store_true", default=False,
                      help="Index new or updated entries.")
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
        indexer = Indexer(config, logger, storage)
        time_now = int(time.time())

        paths_system: Dict[str, List[Path]]
        if options.filename:
            collection = 'idgames'   # TODO: detect from path
            paths_system = {
                collection: [Path(options.filename)]
            }
        else:
            paths_system = {}
            for collection, collection_path in config.get('paths.collections').items():

                collection_local_root = Path(collection_path)
                paths_system[collection] = list(collection_local_root.rglob('*.zip'))
                paths_system[collection].sort()

        for collection, collection_paths in paths_system.items():
            for path_system in collection_paths:
                info, entry = indexer.process_file(collection, path_system, options.force)
                if info is None:
                    continue

                # Transfer indexed information to an entry.
                if entry is None:
                    entry = Entry(
                        collection,
                        info.path_idgames.as_posix(),
                        info.file_modified,
                        info.file_size,
                        time_now
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

                # Combine authors from the main entry and every map.
                author_set: Set[str] = set(info.authors)
                for map in info.maps:
                    author_set.update(map.authors)

                # Store or update entry.
                entry.id = storage.save_entry(entry)
                storage.save_entry_authors(entry, author_set)
                storage.save_entry_maps(entry, info.maps)
                storage.save_entry_textfile(entry, info.text_contents)
                storage.save_entry_images(entry, info.graphics)
                storage.save_entry_music(entry, info.music)
                storage.commit()

        # Only remove dead entries if all entries were scanned.
        # Otherwise, unscanned entries will be removed.
        if options.clean and not options.filename:
            logger.info('Removing dead entries...')
            storage.remove_dead_entries(paths_system)

        indexer.close()

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
