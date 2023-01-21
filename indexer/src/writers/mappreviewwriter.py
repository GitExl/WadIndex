import gzip
import io
import struct
from pathlib import Path

from doom.map.map import LineFlags
from extractors.extractedinfo import ExtractedInfo
from writers.writerbase import WriterBase


S_HEADER = struct.Struct('<4sIII')
S_LINE = struct.Struct('<hhhh')


class MapPreviewWriter(WriterBase):

    def write(self, info: ExtractedInfo):
        base_path = Path(self.config.get('writers.map_previews.output_path'))

        path_dir = (base_path / info.path_idgames).parents[0]
        path_dir.mkdir(parents=True, exist_ok=True)

        for map in info.maps:
            vertex_count = len(map.vertices)
            side_count = len(map.sides)
            sector_count = len(map.sectors)

            data_blocking = io.BytesIO()
            data_ceil = io.BytesIO()
            data_floor = io.BytesIO()
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
                    write_to = data_blocking

                # Ceiling or floor differences.
                elif 0 <= line.side_front < side_count and 0 <= line.side_back < side_count:
                    side_front = map.sides[line.side_front]
                    side_back = map.sides[line.side_back]
                    if side_front.sector < 0 or side_front.sector >= sector_count or side_back.sector < 0 or side_back.sector >= sector_count:
                        continue

                    sector_front = map.sectors[side_front.sector]
                    sector_back = map.sectors[side_back.sector]
                    if sector_front.z_ceiling != sector_back.z_ceiling:
                        write_to = data_ceil
                    elif sector_front.z_floor != sector_back.z_floor:
                        write_to = data_floor
                    else:
                        continue

                else:
                    continue

                v1 = map.vertices[line.vertex_start]
                v2 = map.vertices[line.vertex_end]
                write_to.write(S_LINE.pack(
                    int(v1.x), int(v1.y),
                    int(v2.x), int(v2.y)
                ))

            path_file = path_dir / '{}_{}.gz'.format(info.filename_base, map.name)
            with open(path_file, 'wb') as f:
                data_bytes_blocking = data_blocking.getbuffer().tobytes()
                data_bytes_ceil = data_ceil.getbuffer().tobytes()
                data_bytes_floor = data_floor.getbuffer().tobytes()
                data_header = S_HEADER.pack(
                    b'MAPP',
                    len(data_bytes_blocking) // S_LINE.size,
                    len(data_bytes_ceil) // S_LINE.size,
                    len(data_bytes_floor) // S_LINE.size
                )

                f.write(gzip.compress(data_header + data_bytes_blocking + data_bytes_ceil + data_bytes_floor))
