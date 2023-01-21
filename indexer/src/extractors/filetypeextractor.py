from doom.doom_image import DoomImage
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

                data = file.get_data()

                # MIDI formats
                if data[:4] == b'MThd':
                    filetype = 'midi'
                elif data[:4] == b'MUS\0x1A':
                    filetype = 'mus'

                # Digital music formats
                # elif self.detect_mp3(data):
                #     filetype = 'mp3'
                # elif self.detect_ogg(data):
                #     filetype = 'ogg'
                # elif self.detect_opus(data):
                #     filetype = 'opus'

                # Tracker formats
                elif data[:17] == 'Extended module: ':
                    filetype = 'xm'
                elif data[1080:1084] in {'4FLT', '8FLT', 'M.K.', '4CHN', '6CHN', '8CHN'}:
                    filetype = 'mod'
                # elif data[:] == '':
                #     filetype = 'it'
                # elif data[:] == '':
                #     filetype = 's3m'

                # Graphics
                # elif DoomImage.is_valid(data):
                #     filetype = 'doom_image'

                else:
                    continue

                file.type = filetype
