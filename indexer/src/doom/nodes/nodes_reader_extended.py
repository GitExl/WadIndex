from struct import Struct
from typing import Tuple

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

STRUCT_NODES_HEADER: Struct = Struct('<I')
STRUCT_NODE: Struct = Struct('<hhhhhhhhhhhhII')


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


class NodesReaderExtended(NodesReaderBase):

    def __init__(self, map: Map, map_data: MapData, data: bytes):
        super().__init__(map, map_data)

        self.data: bytes = data

    def read(self) -> Nodes:
        offset = 0

        # New vertices
        vertex_count_original, vertex_count_new = STRUCT_VERTICES_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_VERTICES_HEADER.size

        vertex_data = memoryview(self.data)[offset:offset + vertex_count_new * STRUCT_VERTEX.size]
        vertices = self.read_binary_data_memoryview(vertex_data, unpack_vertex, STRUCT_VERTEX)
        offset += len(vertex_data)

        # Subsectors
        sub_sector_count, = STRUCT_SUB_SECTORS_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_SUB_SECTORS_HEADER.size

        sub_sector_data = memoryview(self.data)[offset:offset + sub_sector_count * STRUCT_SUB_SECTOR_RAW.size]
        raw_sub_sectors = self.read_binary_data_memoryview(sub_sector_data, unpack_subsector_raw, STRUCT_SUB_SECTOR_RAW)
        offset += len(sub_sector_data)

        # Segments
        segment_count, = STRUCT_SEGS_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_SEGS_HEADER.size

        segment_data = memoryview(self.data)[offset:offset + segment_count * STRUCT_SEG.size]
        segments = self.read_binary_data_memoryview(segment_data, unpack_segment, STRUCT_SEG)
        offset += len(segment_data)

        # Nodes
        node_count, = STRUCT_NODES_HEADER.unpack_from(self.data, offset)
        offset += STRUCT_NODES_HEADER.size

        nodes_data = memoryview(self.data)[offset:offset + node_count * STRUCT_NODE.size]
        nodes = self.read_binary_data_memoryview(nodes_data, unpack_node, STRUCT_NODE)
        offset += len(nodes_data)

        # Build segment lists from index offset data.
        sub_sectors = []
        segment_index = 0
        for sub_sector_seg_count in raw_sub_sectors:
            sub_sector = SubSector(segments[segment_index:segment_index + sub_sector_seg_count])
            sub_sectors.append(sub_sector)
            segment_index += sub_sector_seg_count

        return Nodes(self.map.vertices + vertices, segments, sub_sectors, nodes)
