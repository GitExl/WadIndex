import gzip
import io
import struct
from pathlib import Path

from doom.map import LineFlags
from extractors.extractedinfo import ExtractedInfo
from writers.writerbase import WriterBase


S_HEADER = struct.Struct('<4sII')
S_LINE = struct.Struct('<hhhh')


class MapPreviewWriter(WriterBase):

    def write(self, info: ExtractedInfo):
        base_path = Path(self.config.get('writers.map_previews.output_path'))

        path_dir = (base_path / info.path_idgames).parents[0]
        path_dir.mkdir(parents=True, exist_ok=True)

        for map in info.maps:
            vertex_count = len(map.vertices)

            data_blocking = io.BytesIO()
            data_2sided = io.BytesIO()
            for line in map.lines:
                if line.flags & LineFlags.SECRET:
                    continue
                if line.flags & LineFlags.HIDDEN:
                    continue

                if line.flags & LineFlags.BLOCK:
                    write_to = data_blocking
                else:
                    write_to = data_2sided

                if line.vertex_start >= vertex_count:
                    continue
                if line.vertex_end >= vertex_count:
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
                data_bytes_2sided = data_2sided.getbuffer().tobytes()
                data_header = S_HEADER.pack(
                    b'MAPP',
                    len(data_bytes_blocking) // S_LINE.size,
                    len(data_bytes_2sided) // S_LINE.size
                )

                f.write(gzip.compress(data_header + data_bytes_blocking + data_bytes_2sided))
