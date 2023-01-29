from struct import Struct
from typing import Tuple, List

from doom.map.map import Map, Vertex
from doom.map.map_data_finder import MapData
from doom.nodes.nodes import Segment, Node, Nodes, SubSector
from doom.nodes.nodes_reader_base import NodesReaderBase


STRUCT_VERTICES_HEADER: Struct = Struct('<II')
STRUCT_VERTEX: Struct = Struct('<II')

STRUCT_SUB_SECTORS_HEADER: Struct = Struct('<I')
STRUCT_SUB_SECTOR_RAW: Struct = Struct('<I')

STRUCT_SEGS_HEADER: Struct = Struct('<I')
STRUCT_SEG: Struct = Struct('<IIHB')
STRUCT_SEG_EXT: Struct = Struct('<IIIB')

STRUCT_NODES_HEADER: Struct = Struct('<I')
STRUCT_NODE: Struct = Struct('<hhhhhhhhhhhhII')
STRUCT_NODE_EXT: Struct = Struct('<iiiihhhhhhhhII')


def unpack_vertex(values: Tuple):
    return Vertex(values[0] / 65536.0, values[1] / 65536.0)


def unpack_subsector_raw(values: Tuple):
    return values[0]


def unpack_segment(values: Tuple):
    return Segment(values[0], values[1], values[2], values[3])


def unpack_node(values: Tuple):
    return Node(
        values[0], values[1], values[2], values[3],
        values[4], values[5], values[6], values[7],
        values[8], values[9], values[10], values[11],
        values[12], values[13]
    )


def unpack_node_ext(values: Tuple):
    return Node(
        values[0] / 65536.0, values[1] / 65536.0,
        values[2] / 65536.0, values[3] / 65536.0,
        values[4], values[5], values[6], values[7],
        values[8], values[9], values[10], values[11],
        values[12], values[13]
    )


class NodesReaderZDoomGL(NodesReaderBase):

    def __init__(self, map: Map, map_data: MapData, data: bytes, version: int):
        super().__init__(map, map_data)

        self.data: bytes = data
        self.version = version

    def read(self) -> Nodes:
        offset = 0

        # New vertices
        vertex_count_original, vertex_count_new = STRUCT_VERTICES_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_VERTICES_HEADER.size

        vertex_data = memoryview(self.data)[offset:offset + vertex_count_new * STRUCT_VERTEX.size]
        vertices: List[Vertex] = self.read_binary_data_memoryview(vertex_data, unpack_vertex, STRUCT_VERTEX)
        offset += len(vertex_data)

        # Subsectors
        sub_sector_count, = STRUCT_SUB_SECTORS_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_SUB_SECTORS_HEADER.size

        sub_sector_data = memoryview(self.data)[offset:offset + sub_sector_count * STRUCT_SUB_SECTOR_RAW.size]
        raw_sub_sectors = self.read_binary_data_memoryview(sub_sector_data, unpack_subsector_raw, STRUCT_SUB_SECTOR_RAW)
        offset += len(sub_sector_data)

        # Segments
        if self.version >= 2:
            struct_segment = STRUCT_SEG_EXT
        else:
            struct_segment = STRUCT_SEG

        segment_count, = STRUCT_SEGS_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_SEGS_HEADER.size

        segment_data = memoryview(self.data)[offset:offset + segment_count * struct_segment.size]
        segments: List[Segment] = self.read_binary_data_memoryview(segment_data, unpack_segment, struct_segment)
        offset += len(segment_data)

        # Nodes
        if self.version >= 3:
            struct_node = STRUCT_NODE_EXT
            unpack_func_node = unpack_node_ext
        else:
            struct_node = STRUCT_NODE
            unpack_func_node = unpack_node

        node_count, = STRUCT_NODES_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_NODES_HEADER.size

        nodes_data = memoryview(self.data)[offset:offset + node_count * struct_node.size]
        nodes: List[Node] = self.read_binary_data_memoryview(nodes_data, unpack_func_node, struct_node)
        offset += len(nodes_data)

        # Build segment lists from index offset data.
        sub_sectors = []
        segment_index = 0
        seg_count = len(segments)
        for sub_sector_seg_count in raw_sub_sectors:
            sub_sector = SubSector(list(range(segment_index, segment_index + sub_sector_seg_count)))
            sub_sectors.append(sub_sector)
            segment_index += sub_sector_seg_count

            # Rewrite segments so that they refer to a second vertex instead of partner seg.
            v_start = segments[sub_sector.segments[0]].v1
            for seg_index in sub_sector.segments:
                segment = segments[seg_index]

                # Last seg or bad seg reference, like in KDiZD Z1M10. End subsector.
                if segment.v2 == 0xFFFFFFFF or segment.v2 >= seg_count:
                    v2 = v_start
                else:
                    partner_seg = segments[segment.v2]
                    v2 = partner_seg.v1

                segments[seg_index] = Segment(segment.v1, v2, segment.line, segment.side)

        return Nodes(self.map.vertices + vertices, segments, sub_sectors, nodes)
