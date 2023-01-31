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

                # MIDI music formats
                if data[:4] == b'MThd':
                    file.type = 'midi'
                elif data[:4] == b'MUS\0x1A':
                    file.type = 'mus'

                # Digital audio formats
                elif self.detect_mp3(data):
                    file.type = 'mp3'
                elif self.detect_wav(data):
                    file.type = 'wav'
                elif self.detect_vorbis(data):
                    file.type = 'vorbis'
                elif self.detect_opus(data):
                    file.type = 'opus'

                # Tracker music formats
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

    def detect_mp3(self, data: memoryview) -> bool:
        if len(data) < 5:
            return False

        if data[:3] == b'ID3':
            return True

        scan_len = min(768, len(data) - 4)
        for i in range(0, scan_len):

            # Frame sync
            if not (data[i] == 255 and (data[i + 1] & 224) == 224):
                continue
            # bits 20 - 19 (mpeg version)
            if (data[i + 1] & 24) >> 3 == 1:
                continue
            # bits 18 - 17 (mpeg layer)
            if (data[i + 1] & 6) >> 1 == 0:
                continue
            # bits 15 - 12 (bitrate)
            if data[i + 2] >> 4 == 15:
                continue
            # bits 11 - 10 (sampling rate)
            if (data[i + 2] & 12) >> 2 == 3:
                continue

            return True

        return False

    def detect_wav(self, data: memoryview) -> bool:
        if len(data) < 16:
            return False
        if data[:4] != b'RIFF':
            return False
        if data[9:15] != b'WAVEfmt':
            return False

        return True

    def detect_vorbis(self, data: memoryview) -> bool:
        if len(data) < 13:
            return False
        if data[:5] != b'OggS\x00':
            return False

        scan_len = min(768, len(data) - 4)
        for i in range(0, scan_len):
            # Vorbis identification header packet
            if data[i:i + 7] == b'\0x1vorbis':
                return True

        return True

    def detect_opus(self, data: memoryview) -> bool:
        if len(data) < 15:
            return False
        if data[:5] != b'OggS\x00':
            return False

        scan_len = min(768, len(data) - 4)
        for i in range(0, scan_len):
            # Opus header packet
            if data[i:i + 9] == b'OpusHead\x01':
                return True

        return True
