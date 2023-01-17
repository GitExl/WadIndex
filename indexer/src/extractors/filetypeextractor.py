from doom.doomimage import DoomImage
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
                if data[:4] == b'MThd':
                    filetype = 'midi'
                elif data[:4] == b'MUS\0x1A':
                    filetype = 'mus'
                # elif DoomImage.is_valid(data):
                #     filetype = 'doom_image'
                else:
                    continue

                file.type = filetype
