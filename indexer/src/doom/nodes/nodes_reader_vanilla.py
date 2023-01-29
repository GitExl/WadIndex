from struct import Struct
from typing import Tuple

from doom.map.map import Map
from doom.map.map_data_finder import MapData

from doom.nodes.nodes import Segment, Node, Nodes, SubSector
from doom.nodes.nodes_reader_base import NodesReaderBase


STRUCT_SEG: Struct = Struct('<HHhHhh')
STRUCT_SEG_DEEP: Struct = Struct('<IIhHhh')

STRUCT_SUB_SECTOR_RAW: Struct = Struct('<hh')
STRUCT_SUB_SECTOR_RAW_DEEP: Struct = Struct('<hI')

STRUCT_NODE: Struct = Struct('<hhhhhhhhhhhhHH')
STRUCT_NODE_DEEP: Struct = Struct('<hhhhhhhhhhhhII')


def unpack_segment(values: Tuple):
    return Segment(values[0], values[1], values[3], values[4])


def unpack_subsector_raw(values: Tuple):
    return values[0], values[1]


def unpack_node(values: Tuple):
    return Node(
        values[0], values[1], values[2], values[3],
        values[4], values[5], values[6], values[7],
        values[8], values[9], values[10], values[11],
        values[12], values[13]
    )


class NodesReaderVanilla(NodesReaderBase):

    def __init__(self, map: Map, map_data: MapData, deep: bool = False):
        super().__init__(map, map_data)

        self.deep: bool = deep

    def read(self) -> Nodes:
        if self.deep:
            struct_seg = STRUCT_SEG_DEEP
            struct_node = STRUCT_NODE_DEEP
            struct_sub_sector = STRUCT_SUB_SECTOR_RAW_DEEP
        else:
            struct_seg = STRUCT_SEG
            struct_node = STRUCT_NODE
            struct_sub_sector = STRUCT_SUB_SECTOR_RAW

        segments = self.read_binary_data_lump('SEGS', unpack_segment, struct_seg)
        nodes = self.read_binary_data_lump('NODES', unpack_node, struct_node)

        # Build segment lists from index offset data.
        sub_sectors = []
        raw_sub_sectors = self.read_binary_data_lump('SSECTORS', unpack_subsector_raw, struct_sub_sector)
        for raw_sub_sector in raw_sub_sectors:
            seg_count, seg_first = raw_sub_sector[0], raw_sub_sector[1]
            sub_sector = SubSector(segments[seg_first:seg_first + seg_count])
            sub_sectors.append(sub_sector)

        return Nodes(self.map.vertices, segments, sub_sectors, nodes)
