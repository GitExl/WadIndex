from dataclasses import dataclass
from typing import List

from doom.map.map import Vertex


@dataclass(frozen=True)
class Segment:
    __slots__ = [
        'v1', 'v2',
        'line',
        'side',
    ]

    v1: int
    v2: int
    line: int
    side: int


@dataclass(frozen=True)
class SubSector:
    __slots__ = [
        'segments',
    ]

    segments: List[int]


@dataclass(frozen=True)
class Node:
    __slots__ = [
        'x', 'y',
        'dx', 'dy',
        'right_top', 'right_bottom', 'right_left', 'right_right',
        'left_top', 'left_bottom', 'left_left', 'left_right',
        'child_right', 'child_left',
    ]

    x: int
    y: int
    dx: int
    dy: int

    right_top: int
    right_bottom: int
    right_left: int
    right_right: int

    left_top: int
    left_bottom: int
    left_left: int
    left_right: int

    child_right: int
    child_left: int


CHILD_IS_SUBSECTOR = 0x7FFFFFFF


class Nodes:

    def __init__(self, vertices: List[Vertex], segments: List[Segment], sub_sectors: List[SubSector], nodes: List[Node]):
        self.vertices: List[Vertex] = vertices
        self.segments: List[Segment] = segments
        self.sub_sectors: List[SubSector] = sub_sectors
        self.nodes: List[Node] = nodes
