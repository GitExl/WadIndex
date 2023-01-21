from io import BytesIO
from math import ceil
from typing import List, Optional

from PIL import Image

from archives.archivefilebase import ArchiveFileBase
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from doom.doom_image import DoomImage
from doom.palette import Palette
from extractors.extractedinfo import GraphicInfo


GRAPHIC_LUMP_NAMES: List[str] = [
    'titlepic',
    'title',
    'interpic',
    'bossback',
    'endpic',
    'pfub1',
    'victory2',
    'pfub2',
    'wimap0',
    'wimap1',
    'wimap2',
    'credit',
    'help',
    'help1',
    'help2',
]

GRAPHIC_LUMP_NAMES_PRIMARY: List[str] = [
    'titlepic',
    'title',
    'interpic',
]

THUMB_WIDTH = 280
THUMB_HEIGHT = 210


class GraphicsExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if info.archive_list is None:
            self.logger.debug('Cannot extract graphics without an archive list.')
            return

        archive_list = info.archive_list
        playpal = archive_list.file_find_basename('playpal')
        if not playpal:
            self.logger.error('No PLAYPAL lump in archive list.')
            return
        palette = Palette.from_playpal_data(playpal.get_data())

        for filename in GRAPHIC_LUMP_NAMES:
            file = archive_list.file_find_basename(filename, include_main=False)
            if not file:
                continue

            image = self.read_lump_as_image(file, palette)
            if image:
                if image.width > image.height:
                    thumb_width = THUMB_WIDTH
                    thumb_height = ceil(image.height * (THUMB_WIDTH / image.width))
                else:
                    thumb_width = ceil(image.width * (THUMB_HEIGHT / image.height))
                    thumb_height = THUMB_HEIGHT

                image_thumb = image.resize((thumb_width, thumb_height), Image.BICUBIC)
                info.graphics[filename] = GraphicInfo(image, image_thumb)

        # Determine primary graphic.
        for name in GRAPHIC_LUMP_NAMES_PRIMARY:
            if name in info.graphics:
                info.graphics[name].is_primary = True
                break

    def read_lump_as_image(self, file: ArchiveFileBase, palette: Palette) -> Optional[Image.Image]:
        image: Optional[Image.Image] = None

        # Attempt to identify the file looking for PNG or partial JPEG magic bytes.
        data = file.get_data()
        if data[0:8] == b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' or data[0:3] == b'\xFF\xD8\xFF':
            try:
                image = Image.open(BytesIO(data))
                image = image.convert('RGB')
            except IOError:
                image = None

        elif DoomImage.is_valid(data):
            doom_image = DoomImage.from_data(data, palette)
            image = doom_image.get_pillow_image()

        # File sizes for planar 320x200 and 640x480 match Heretic and Hexen screens.
        elif file.size == 320 * 200:
            image = self.read_raw_graphic(320, 200, data, palette)
        elif file.size == 640 * 480:
            image = self.read_raw_graphic(640, 480, data, palette)

        # Apply 4:3 aspect ratio correction, to 8:5 aspect ratio screens. Increase height by 20%.
        if image:
            width, height = image.width, image.height
            aspect_ratio = width / height
            if aspect_ratio == 8.0 / 5.0:
                height = ceil(height * 1.2)
                image = image.resize((width, height), Image.BICUBIC)

        if not image:
            self.logger.stream('unknown_graphics_format', 'Cannot identify or read {}'.format(file.name))
            self.logger.warn('Graphics data is of unknown type.')

        return image

    @staticmethod
    def read_raw_graphic(width: int, height: int, data: bytes, palette: Palette) -> Image.Image:
        image = Image.frombytes('P', (width, height), data)
        image.putpalette(palette.raw)
        return image.convert('RGB')
