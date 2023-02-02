from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from utils.mp3_detect import mp3_detect


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
                elif data[:4] == b'MUS\x1A':
                    file.type = 'mus'

                # Digital audio formats
                elif mp3_detect(data):
                    file.type = 'mp3'
                elif self.detect_wav(data):
                    file.type = 'wav'
                elif self.detect_vorbis(data):
                    file.type = 'vorbis'
                elif self.detect_opus(data):
                    file.type = 'opus'

                # Assume an ASF file header GUID always indicates WMA audio.
                elif data[:16] == b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C':
                    file.type = 'wma'

                # Tracker music formats
                elif data[:17] == b'Extended Module: ':
                    file.type = 'xm'
                elif data[1080:1084] in {b'4FLT', b'8FLT', b'M.K.', b'4CHN', b'6CHN', b'8CHN'}:
                    file.type = 'mod'
                elif data[:4] == b'IMPM':
                    file.type = 'it'
                elif data[28:32] == b'\x1A\x10\x00\x00' and data[44:48] == b'SCRM':
                    file.type = 's3m'

                # Graphics
                # elif DoomImage.is_valid(data):
                #     file.type = 'doom_image'

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
