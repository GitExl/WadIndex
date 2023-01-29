from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase


class FileTypeExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if info.archive_list is None:
            self.logger.debug('Cannot extract file types without an archive list.')
            return

        archive_list = info.archive_list

        for archive in archive_list.archives:
            if archive.is_main:
                continue

            for file in archive.files:
                if file.type is not None:
                    continue

                data = memoryview(file.get_data())

                # MIDI formats
                if data[:4] == b'MThd':
                    file.type = 'midi'
                elif data[:4] == b'MUS\0x1A':
                    file.type = 'mus'

                # Digital music formats
                # elif self.detect_mp3(data):
                #     file.type = 'mp3'
                # elif self.detect_ogg(data):
                #     file.type = 'ogg'
                # elif self.detect_opus(data):
                #     file.type = 'opus'

                # Tracker formats
                elif data[:17] == 'Extended module: ':
                    file.type = 'xm'
                elif data[1080:1084] in {'4FLT', '8FLT', 'M.K.', '4CHN', '6CHN', '8CHN'}:
                    file.type = 'mod'
                # elif data[:] == '':
                #     file.type = 'it'
                # elif data[:] == '':
                #     file.type = 's3m'

                # Graphics
                # elif DoomImage.is_valid(data):
                #     file.type = 'doom_image'
