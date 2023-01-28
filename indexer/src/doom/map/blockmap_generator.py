from dataclasses import dataclass
from math import floor, ceil, sqrt
from typing import List, Optional, Tuple

from doom.map.map import Map


@dataclass(frozen=True)
class BBox:
    x1: int
    y1: int

    x2: int
    y2: int

    width: int
    height: int


@dataclass
class BlockmapBlock:
    total_length: int = 0


Blockmap = List[Optional[BlockmapBlock]]


class BlockmapGenerator:

    def __init__(self, map: Map, block_size=256):
        self.block_size: int = block_size
        self.map: Map = map

        self.bbox: BBox = self.determine_bbox()
        self.block_width: int = ceil(self.bbox.width / self.block_size) + 1
        self.block_height: int = ceil(self.bbox.height / self.block_size) + 1

        self.blockmap: Blockmap = self.build_blockmap()

    def build_blockmap(self) -> Blockmap:
        blockmap: Blockmap = [None] * (self.block_width * self.block_height)

        for line_index, line in enumerate(self.map.lines):
            if line.vertex_start >= len(self.map.vertices):
                continue
            if line.vertex_end >= len(self.map.vertices):
                continue

            v1 = self.map.vertices[line.vertex_start]
            v2 = self.map.vertices[line.vertex_end]

            line_x1 = v1.x - self.bbox.x1
            line_y1 = v1.y - self.bbox.y1
            line_x2 = v2.x - self.bbox.x1
            line_y2 = v2.y - self.bbox.y1

            x1 = floor(line_x1 / self.block_size)
            y1 = floor(line_y1 / self.block_size)
            x2 = floor(line_x2 / self.block_size)
            y2 = floor(line_y2 / self.block_size)

            # Find the sides and sector for the front and back of the line.
            side_front = None
            side_back = None
            sector_front = None
            sector_back = None
            if 0 <= line.side_front < len(self.map.sides):
                side_front = self.map.sides[line.side_front]
                if 0 <= side_front.sector < len(self.map.sectors):
                    sector_front = self.map.sectors[side_front.sector]
            if 0 <= line.side_back < len(self.map.sides):
                side_back = self.map.sides[line.side_back]
                if 0 <= side_back.sector < len(self.map.sectors):
                    sector_back = self.map.sectors[side_back.sector]

            surface_count = 0

            # Count the number of visible middle textures.
            if side_front is not None and side_front.texture_mid != '-':
                surface_count += 1
            if side_back is not None and side_back.texture_mid != '-':
                surface_count += 1

            # Count the number of visible upper and lower surfaces with textures.
            if sector_front is not None and sector_back is not None:

                # Differences in sector textures count.
                if sector_front.texture_floor != sector_back.texture_floor:
                    surface_count += 1
                if sector_front.texture_ceiling != sector_back.texture_ceiling:
                    surface_count += 1

                # Difference in light levels counts.
                if sector_front.light != sector_back.light:
                    surface_count += 1

                # Upper/lower textures are surfaces.
                if sector_front.z_floor > sector_back.z_floor and side_back.texture_lower != '-':
                    surface_count += 1
                elif sector_back.z_floor > sector_front.z_floor and side_front.texture_lower != '-':
                    surface_count += 1

                if sector_front.z_ceiling > sector_back.z_ceiling and side_back.texture_upper != '-':
                    surface_count += 1
                elif sector_back.z_ceiling > sector_front.z_ceiling and side_front.texture_upper != '-':
                    surface_count += 1

            if not surface_count:
                continue

            # http://www.edepot.com/linec.html
            y_longer = False
            short_len = y2 - y1
            long_len = x2 - x1
            if abs(short_len) > abs(long_len):
                swap = short_len
                short_len = long_len
                long_len = swap
                y_longer = True

            end_val = long_len
            if long_len < 0:
                increment_val = -1
                long_len = -long_len
            else:
                increment_val = 1

            if long_len == 0:
                dec_inc = float(short_len)
            else:
                dec_inc = float(short_len) / float(long_len)

            j = 0.0
            if y_longer:
                for i in range(0, end_val, increment_val):
                    x = x1 + int(j)
                    y = y1 + i
                    self.assign_line_to_block(blockmap, x, y, line_x1, line_y1, line_x2, line_y2, surface_count)
                    j += dec_inc
            else:
                for i in range(0, end_val, increment_val):
                    x = x1 + i
                    y = y1 + int(j)
                    self.assign_line_to_block(blockmap, x, y, line_x1, line_y1, line_x2, line_y2, surface_count)
                    j += dec_inc

        return blockmap

    def assign_line_to_block(self, blockmap: Blockmap, block_x: int, block_y: int, line_x1: float, line_y1: float, line_x2: float, line_y2: float, surface_count: int):
        block_index = block_x + block_y * self.block_width

        block = blockmap[block_index]
        if block is None:
            blockmap[block_index] = block = BlockmapBlock()

        block_x1 = block_x * self.block_size
        block_y1 = block_y * self.block_size
        block_x2 = block_x1 + self.block_size
        block_y2 = block_y1 + self.block_size

        inter = self.get_box_intersection(line_x1, line_y1, line_x2, line_y2, block_x1, block_y1, block_x2, block_y2)
        if inter is not None:
            line_len = sqrt(
                (abs(inter[2] - inter[0]) ** 2) +
                (abs(inter[3] - inter[1]) ** 2)
            )

            block.total_length += line_len * surface_count

    @staticmethod
    def get_intersection(x1, y1, x2, y2, x3, y3, x4, y4, sa=False, sb=False) -> Optional[Tuple[float, float]]:
        x1x2 = x1 - x2
        y1y2 = y1 - y2
        x1x3 = x1 - x3
        y1y3 = y1 - y3
        x3x4 = x3 - x4
        y3y4 = y3 - y4

        d = x1x2 * y3y4 - y1y2 * x3x4

        # parallel or coincident
        if d == 0:
            return None

        t = (x1x3 * y3y4 - y1y3 * x3x4) / d
        u = -(x1x2 * y1y3 - y1y2 * x1x3) / d

        ist = 0 <= t <= 1
        isu = 0 <= u <= 1

        if sa and sb and ist and isu or sa and not sb and ist or not sa and sb and isu or not sa and not sb:
            return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

        return None

    def get_box_intersection(self, x1: float, y1: float, x2: float, y2: float, b1: float, b2: float, b3: float, b4: float) -> Optional[Tuple[float, float, float, float]]:
        _i1 = self.get_intersection(x1, y1, x2, y2, b1, b2, b1, b4, False, True)  # left
        _i2 = self.get_intersection(x1, y1, x2, y2, b1, b2, b3, b2, False, True)  # top
        _i3 = self.get_intersection(x1, y1, x2, y2, b3, b2, b3, b4, False, True)  # right
        _i4 = self.get_intersection(x1, y1, x2, y2, b1, b4, b3, b4, False, True)  # bottom

        dx = x2 - x1
        dy = y2 - y1

        i1: Optional[Tuple[float, float]] = None
        i2: Optional[Tuple[float, float]] = None

        if _i1:
            if dx > 0:
                i1 = _i1
            if dx < 0:
                i2 = _i1

        if _i2:
            if dy > 0:
                i1 = _i2
            if dy < 0:
                i2 = _i2

        if _i3:
            if dx < 0:
                i1 = _i3
            if dx > 0:
                i2 = _i3

        if _i4:
            if dy < 0:
                i1 = _i4
            if dy > 0:
                i2 = _i4

        if i1 is None or i2 is None:
            return None

        return (
            i1[0], i1[1],
            i2[0], i2[1],
        )

    def determine_bbox(self) -> BBox:
        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0

        for vertex in self.map.vertices:
            x1 = min(x1, vertex.x)
            y1 = min(y1, vertex.y)

            x2 = max(x2, vertex.x)
            y2 = max(y2, vertex.y)

        return BBox(
            floor(x1), floor(y1),
            ceil(x2), ceil(y2),
            ceil(x2 - x1), ceil(y2 - y1)
        )
