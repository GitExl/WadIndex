import re
from hashlib import sha1
from pathlib import Path

from extractors.extractedinfo import ExtractedInfo, MusicType, MusicInfo
from extractors.extractorbase import ExtractorBase


class MusicExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if info.archive_list is None:
            self.logger.warn('Cannot extract music without an archive list.')
            return

        archive_list = info.archive_list

        for archive in archive_list.archives:
            if archive.is_main:
                continue

            for file in archive.files:
                if file.type == 'midi':
                    music_type = MusicType.MIDI
                elif file.type == 'mus':
                    music_type = MusicType.MUS
                else:
                    continue

                data = file.get_data()
                data_hash = sha1(data).digest()

                name_path = Path(file.name)
                name = name_path.stem[:27]
                name = re.sub(r'[^a-zA-Z0-9_\-]+', '', name)

                info.music[name] = MusicInfo(name, music_type, data, data_hash)
