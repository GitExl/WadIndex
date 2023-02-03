import gzip

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
                if file.size < 4:
                    continue

                data = file.get_data()

                # Decompress GZipped data
                if data[:3] == b'\x1F\x8B\x08' and data[4] & 0xE0 == 0:
                    data = gzip.decompress(data)

                data = memoryview(data)

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
                elif data[:4] == b'fLaC':
                    file.type = 'flac'
                elif len(data) > 5 and data[:5] == b'OggS\x00':
                    if self.detect_vorbis(data):
                        file.type = 'vorbis'
                    elif self.detect_opus(data):
                        file.type = 'opus'

                # Assume an ASF file header GUID always indicates WMA audio.
                elif len(data) > 16 and data[:16] == b'\x30\x26\xB2\x75\x8E\x66\xCF\x11\xA6\xD9\x00\xAA\x00\x62\xCE\x6C':
                    file.type = 'wma'

                # Tracker music formats
                elif len(data) > 17 and data[:17] == b'Extended Module: ':
                    file.type = 'xm'
                elif len(data) > 1100 and data[1080:1084] in {b'4FLT', b'8FLT', b'M.K.', b'4CHN', b'6CHN', b'8CHN'}:
                    file.type = 'mod'
                elif data[:4] == b'IMPM':
                    file.type = 'it'
                elif len(data) > 32 and data[28:32] == b'\x1A\x10\x00\x00' and data[44:48] == b'SCRM':
                    file.type = 's3m'

                # Video game music
                elif data[:4] == b'Vgm\x20':
                    file.type = 'vgm'
                elif len(data) > 33 and data[:33] == b'SNES-SPC700 Sound File Data v0.30':
                    file.type = 'spc'

                # Graphics
                # elif DoomImage.is_valid(data):
                #     file.type = 'doom_image'

    def detect_wav(self, data: memoryview) -> bool:
        if len(data) < 16:
            return False
        if data[:4] != b'RIFF':
            return False
        if data[8:15] != b'WAVEfmt':
            return False

        return True

    def detect_vorbis(self, data: memoryview) -> bool:
        if len(data) < 13:
            return False

        scan_len = min(1024, len(data) - 4)
        for i in range(0, scan_len):
            # Vorbis identification header packet
            if data[i:i + 7] == b'\0x1vorbis':
                return True

        return True

    def detect_opus(self, data: memoryview) -> bool:
        if len(data) < 15:
            return False

        scan_len = min(1024, len(data) - 4)
        for i in range(0, scan_len):
            # Opus header packet
            if data[i:i + 9] == b'OpusHead\x01':
                return True

        return True
