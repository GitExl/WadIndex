from struct import Struct
from typing import Tuple, List

from doom.map.map import Map, Vertex
from doom.map.map_data_finder import MapData
from doom.nodes.nodes import Segment, Node, Nodes, CHILD_IS_SUBSECTOR, SubSector
from doom.nodes.nodes_reader_base import NodesReaderBase


STRUCT_VERTEX1: Struct = Struct('<hh')
STRUCT_VERTEX2: Struct = Struct('<II')

STRUCT_SEGMENT1: Struct = Struct('<HHHHH')
STRUCT_SEGMENT35: Struct = Struct('<IIHHI')

STRUCT_SUB_SECTOR_RAW1: Struct = Struct('<HH')
STRUCT_SUB_SECTOR_RAW3: Struct = Struct('<II')

STRUCT_NODE1: Struct = Struct('<hhhhhhhhhhhhHH')
STRUCT_NODE4: Struct = Struct('<hhhhhhhhhhhhII')


def unpack_vertex1(values: Tuple):
    return Vertex(values[0], values[1])


def unpack_vertex2(values: Tuple):
    return Vertex(values[0] / 65536.0, values[1] / 65536.0)


def unpack_subsector_raw(values: Tuple):
    return values[0], values[1]


def unpack_segment(values: Tuple):
    return Segment(values[0], values[1], values[2], values[3])


def unpack_node1(values: Tuple):

    # Remap subsector flag.
    child_left = values[12]
    child_right = values[13]
    if child_left & 0x8000:
        child_left = (values[12] & 0x7FFF) | CHILD_IS_SUBSECTOR
    if child_right & 0x8000:
        child_right = (values[13] & 0x7FFF) | CHILD_IS_SUBSECTOR

    return Node(
        values[0], values[1], values[2], values[3],
        values[4], values[5], values[6], values[7],
        values[8], values[9], values[10], values[11],
        child_left, child_right
    )


def unpack_node4(values: Tuple):
    return Node(
        values[0], values[1], values[2], values[3],
        values[4], values[5], values[6], values[7],
        values[8], values[9], values[10], values[11],
        values[12], values[13]
    )


class NodesReaderGLBSP(NodesReaderBase):

    def __init__(self, map: Map, map_data: MapData, version: int):
        super().__init__(map, map_data)

        self.version: int = version

    def read(self) -> Nodes:

        # Nothing really supports version 4, and subsector structure is not documented.
        if self.version == 4:
            return Nodes([], [], [], [])

        vertex_data = self.map_data.files.get('GL_VERT').get_data()
        segment_data = self.map_data.files.get('GL_SEGS').get_data()
        sub_sector_data = self.map_data.files.get('GL_SSECT').get_data()
        node_data = self.map_data.files.get('GL_NODES').get_data()

        struct_vertex = STRUCT_VERTEX1
        struct_segment = STRUCT_SEGMENT1
        struct_sub_sector = STRUCT_SUB_SECTOR_RAW1
        struct_node = STRUCT_NODE1

        func_unpack_vertex = unpack_vertex1
        func_unpack_node = unpack_node1

        vertex_gl_bit = 0x8000

        # Determine what data structures to actually use based on the version. What a mess.
        # Also strip magic bytes from lumps that may have them.
        if self.version == 2:
            struct_vertex = STRUCT_VERTEX2

            func_unpack_vertex = unpack_vertex2

            vertex_data = vertex_data[4:]

        elif self.version == 3:
            struct_vertex = STRUCT_VERTEX2
            struct_segment = STRUCT_SEGMENT35
            struct_sub_sector = STRUCT_SUB_SECTOR_RAW3

            func_unpack_vertex = unpack_vertex2

            vertex_data = vertex_data[4:]
            segment_data = segment_data[4:]
            sub_sector_data = sub_sector_data[4:]

            vertex_gl_bit = 0x40000000

        elif self.version == 5:
            struct_vertex = STRUCT_VERTEX2
            struct_segment = STRUCT_SEGMENT35
            struct_sub_sector = STRUCT_SUB_SECTOR_RAW3
            struct_node = STRUCT_NODE4

            func_unpack_vertex = unpack_vertex2
            func_unpack_node = unpack_node4

            vertex_data = vertex_data[4:]

            vertex_gl_bit = 0x80000000

        vertices: List[Vertex] = self.read_binary_data(vertex_data, func_unpack_vertex, struct_vertex)
        segments: List[Segment] = self.read_binary_data(segment_data, unpack_segment, struct_segment)
        sub_sectors_raw = self.read_binary_data(sub_sector_data, unpack_subsector_raw, struct_sub_sector)
        nodes: List[Node] = self.read_binary_data(node_data, func_unpack_node, struct_node)

        # Remap GL vertex indices.
        base_vertex_count = len(self.map.vertices)
        for index, segment in enumerate(segments):
            if segment.v1 & vertex_gl_bit or segment.v2 & vertex_gl_bit:
                v1 = segment.v1
                v2 = segment.v2
                if segment.v1 & vertex_gl_bit:
                    v1 += base_vertex_count
                if segment.v2 & vertex_gl_bit:
                    v2 += base_vertex_count
                segments[index] = Segment(v1, v2, segment.line, segment.side)

        # Build segment lists from index offset data.
        sub_sectors: List[SubSector] = []
        for raw_sub_sector in sub_sectors_raw:
            seg_count, seg_first = raw_sub_sector[0], raw_sub_sector[1]
            sub_sector = SubSector(list(range(seg_first, seg_first + seg_count)))
            sub_sectors.append(sub_sector)

        return Nodes(self.map.vertices + vertices, segments, sub_sectors, nodes)
