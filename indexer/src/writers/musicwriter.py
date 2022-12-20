import gzip
from pathlib import Path

from extractors.extractedinfo import ExtractedInfo, MusicType
from writers.writerbase import WriterBase


class MusicWriter(WriterBase):

    def write(self, info: ExtractedInfo):
        base_path = Path(self.config.get('writers.music.output_path'))
        base_path.mkdir(parents=True, exist_ok=True)

        for name, music in info.music.items():
            if music is None:
                continue

            existing_id = self.storage.find_music_by_hash(music.hash)
            if existing_id is not None:
                music.id = existing_id

            if music.type == MusicType.MIDI:
                extension = 'mid'
            elif music.type == MusicType.MUS:
                extension = 'mus'
            else:
                extension = 'bin'

            path_file = base_path / '{}.{}.gz'.format(music.hash.hex(), extension)
            if not path_file.exists():
                with open(path_file, 'wb') as f:
                    f.write(gzip.compress(music.data))

            self.storage.save_music(music)

        self.storage.commit()
