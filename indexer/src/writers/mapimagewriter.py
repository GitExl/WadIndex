from math import ceil, floor
from pathlib import Path

import cairo
from PIL import Image

from doom.map.map import LineFlags
from extractors.extractedinfo import ExtractedInfo
from writers.writerbase import WriterBase


INDEX_BLOCKING = 0
INDEX_DIFF = 1
INDEX_FLOOR_DIFF = 2

COLORS = (
    (1.0, 1.0, 1.0),
    (0.25, 0.25, 0.25),
    (0.28, 0.36, 0.48),
)

MAX_SIDE = 384


class MapImageWriter(WriterBase):

    def write(self, info: ExtractedInfo):
        base_path = Path(self.config.get('writers.map_images.output_path'))

        path_dir = (base_path / info.path_idgames).parents[0]
        path_dir.mkdir(parents=True, exist_ok=True)

        for map in info.maps:

            lines = (
                [],
                [],
                [],
            )
            x1 = 32768.0
            y1 = 32768.0
            x2 = -32768.0
            y2 = -32768.0

            # TODO: do some of this in the Map class and reuse it in the MapPreviewWriter
            # Collect all drawable lines.
            vertex_count = len(map.vertices)
            side_count = len(map.sides)
            sector_count = len(map.sectors)
            for line in map.lines:
                if line.flags & LineFlags.HIDDEN:
                    continue

                # Invalid lines.
                if line.vertex_start >= vertex_count:
                    continue
                if line.vertex_end >= vertex_count:
                    continue

                # Blocking or secret lines.
                if line.flags & LineFlags.BLOCK or line.flags & LineFlags.SECRET:
                    color_index = INDEX_BLOCKING

                # Ceiling or floor differences.
                elif 0 <= line.side_front < side_count and 0 <= line.side_back < side_count:
                    side_front = map.sides[line.side_front]
                    side_back = map.sides[line.side_back]
                    if side_front.sector < 0 or side_front.sector >= sector_count or side_back.sector < 0 or side_back.sector >= sector_count:
                        continue

                    sector_front = map.sectors[side_front.sector]
                    sector_back = map.sectors[side_back.sector]
                    if sector_front.z_floor != sector_back.z_floor:
                        if abs(sector_front.z_floor - sector_back.z_floor) <= 24:
                            color_index = INDEX_FLOOR_DIFF
                        else:
                            color_index = INDEX_DIFF

                    elif sector_front.z_ceiling != sector_back.z_ceiling:
                        color_index = INDEX_DIFF
                    else:
                        continue

                else:
                    continue

                v1 = map.vertices[line.vertex_start]
                v2 = map.vertices[line.vertex_end]

                x1 = min(v1.x, v2.x, x1)
                y1 = min(v1.y, v2.y, y1)
                x2 = max(v1.x, v2.x, x2)
                y2 = max(v1.y, v2.y, y2)

                lines[color_index].append((v1, v2))

            # Calculate surface size from visible lines.
            width = ceil(x2) - floor(x1)
            height = ceil(y2) - floor(y1)

            # Nothing to see here.
            if width <= 0 or height <= 0:
                continue

            # Scale down longest size.
            scale = 1.0
            longest_side = max(width, height)
            if longest_side > MAX_SIDE:
                scale = MAX_SIDE / longest_side
            scale_inv = 1.0 / scale

            scaled_width = ceil(width / scale_inv)
            scaled_height = ceil(height / scale_inv)

            # Setup target surface.
            surface = cairo.ImageSurface(cairo.FORMAT_RGB24, scaled_width, scaled_height)
            ctx = cairo.Context(surface)
            ctx.set_line_width(scale_inv)
            ctx.scale(scale, scale)
            ctx.translate(-x1, -y1)

            # Draw lines per color.
            for color_index, line_tuples in enumerate(lines):
                color = COLORS[color_index]
                ctx.set_source_rgb(color[0], color[1], color[2])

                for line in line_tuples:
                    ctx.move_to(line[0].x, line[0].y)
                    ctx.line_to(line[1].x, line[1].y)
                ctx.stroke()

            # Convert to Pillow image so that we can save as WebP.
            size = (surface.get_width(), surface.get_height())
            stride = surface.get_stride()
            im = Image.frombuffer('RGB', size, surface.get_data(), 'raw', 'BGRX', stride)

            path_file = path_dir / '{}_{}.webp'.format(info.filename_base, map.name)
            with open(path_file, 'wb') as f:
                im.save(f, lossless=True)

            im.close()
            surface.finish()
