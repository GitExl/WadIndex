from dataclasses import dataclass
from enum import Enum
from typing import List


class NodeTypes(Enum):
    NONE = 0
    VANILLA = 1
    DEEP = 2
    EXTENDED = 3
    EXTENDED_COMPRESSED = 4


class NodeTypesGL(Enum):
    NONE = 0
    UNKNOWN = 1
    ZDOOM_GL = 2
    ZDOOM_GL2 = 3
    ZDOOM_GL3 = 4
    ZDOOM_GL_COMPRESSED = 5
    ZDOOM_GL2_COMPRESSED = 6
    ZDOOM_GL3_COMPRESSED = 7
    GLBSP1 = 8
    GLBSP2 = 9
    GLBSP3 = 10
    GLBSP4 = 11
    GLBSP5 = 12


@dataclass(frozen=True)
class Segment:
    __slots__ = [
        'v1', 'v2'
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

    segments: List[Segment]
