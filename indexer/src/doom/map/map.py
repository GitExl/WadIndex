from dataclasses import dataclass
from enum import Enum, Flag, auto
from typing import List, Optional, Dict, Tuple

from doom.nodes.node_types import NodeTypes, NodeTypesGL
from utils.author_parser import Author


class MapFormat(Enum):
    DOOM = 0
    HEXEN = 1
    UDMF = 2


class MapNamespace(Enum):
    DOOM = 'doom'
    HERETIC = 'heretic'
    STRIFE = 'strife'
    HEXEN = 'hexen'
    ETERNITY = 'eternity'
    ZDOOM = 'zdoom'


class ThingFlags(Flag):
    NONE = 0

    SKILL_1 = auto()
    SKILL_2 = auto()
    SKILL_3 = auto()
    SKILL_4 = auto()
    SKILL_5 = auto()
    AMBUSH = auto()

    NOT_SP = auto()
    NOT_DM = auto()
    NOT_COOP = auto()

    SP = auto()
    DM = auto()
    COOP = auto()

    # MBF
    FRIEND = auto()

    # Hexen
    DORMANT = auto()
    CLASS1 = auto()
    CLASS2 = auto()
    CLASS3 = auto()

    # Strife
    STANDING = auto()
    STRIFE_ALLY = auto()
    TRANSLUCENT25 = auto()
    TRANSLUCENT75 = auto()
    INVISIBLE = auto()

    # ZDoom
    SECRET = auto()


class LineFlags(Flag):
    NONE = 0

    BLOCK = auto()
    BLOCK_MONSTER = auto()
    TWO_SIDED = auto()
    UNPEG_TOP = auto()
    UNPEG_BOTTOM = auto()
    SECRET = auto()
    BLOCK_SOUND = auto()
    HIDDEN = auto()
    MAPPED = auto()

    # Boom
    PASS_USE = auto()

    # Strife
    TRANSLUCENT25 = auto()
    TRANSLUCENT75 = auto()
    JUMP_OVER = auto()
    BLOCK_FLOAT = auto()

    # Eternity
    WALKABLE = auto()

    # ZDoom
    MONSTER_ACTIVATES = auto()
    BLOCK_PLAYERS = auto()
    BLOCK_ALL = auto()

    # Special activation
    PLAYER_CROSS = auto()
    PLAYER_USE = auto()
    MONSTER_CROSS = auto()
    MONSTER_USE = auto()
    IMPACT = auto()
    PLAYER_PUSH = auto()
    MONSTER_PUSH = auto()
    MISSILE_CROSS = auto()
    REPEATS = auto()


@dataclass(frozen=True)
class Vertex:
    __slots__ = ['x', 'y']

    x: float
    y: float


@dataclass(frozen=True)
class Line:
    __slots__ = [
        'vertex_start', 'vertex_end',
        'side_front', 'side_back',
        'flags',
        'type',
        'ids',
        'arg0', 'arg1', 'arg2', 'arg3', 'arg4',
        'arg0str',
    ]

    vertex_start: int
    vertex_end: int
    side_front: int
    side_back: int
    flags: LineFlags
    type: int
    ids: List[int]
    arg0: int
    arg1: int
    arg2: int
    arg3: int
    arg4: int
    arg0str: Optional[str]


@dataclass(frozen=True)
class Side:
    __slots__ = ['sector', 'texture_upper', 'texture_mid', 'texture_lower', 'texture_x', 'texture_y']

    sector: int
    texture_upper: str
    texture_mid: str
    texture_lower: str
    texture_x: int
    texture_y: int


@dataclass(frozen=True)
class Sector:
    __slots__ = ['z_floor', 'z_ceiling', 'texture_floor', 'texture_ceiling', 'ids', 'type', 'light']

    z_floor: int
    z_ceiling: int
    texture_floor: str
    texture_ceiling: str
    ids: List[int]
    type: int
    light: int


@dataclass(frozen=True)
class Thing:
    __slots__ = [
        'x', 'y', 'z',
        'angle',
        'type',
        'flags',
        'id',
        'special',
        'arg0', 'arg1', 'arg2', 'arg3', 'arg4',
        'arg0str',
    ]

    x: float
    y: float
    z: float
    angle: int
    type: int
    flags: ThingFlags
    id: int
    special: int
    arg0: int
    arg1: int
    arg2: int
    arg3: int
    arg4: int
    arg0str: Optional[str]


MapBounds = Tuple[float, float, float, float]


class Map:

    def __init__(self, name: str, namespace: MapNamespace, format: MapFormat,
                 vertices: List[Vertex] = None, lines: Optional[List[Line]] = None, sides: Optional[List[Side]] = None,
                 sectors: Optional[List[Sector]] = None, things: Optional[List[Thing]] = None):

        self.name: str = name
        self.namespace = namespace
        self.format: MapFormat = format

        self.id: Optional[int] = None
        self.entry_id: Optional[int] = None

        self.vertices: List[Vertex] = [] if vertices is None else vertices
        self.lines: List[Line] = [] if lines is None else lines
        self.sides: List[Side] = [] if sides is None else sides
        self.sectors: List[Sector] = [] if sectors is None else sectors
        self.things: List[Thing] = [] if things is None else things

        self.title: Optional[str] = None
        self.allow_jump: Optional[bool] = None
        self.allow_crouch: Optional[bool] = None
        self.par_time: Optional[int] = None
        self.next: Optional[str] = None
        self.next_secret: Optional[str] = None
        self.music: Optional[str] = None
        self.cluster: Optional[int] = None
        self.authors: List[Author] = []
        self.complexity: int = 0
        self.nodes_type: NodeTypes = NodeTypes.NONE
        self.nodes_gl_type: NodeTypesGL = NodeTypesGL.NONE

        self.enemy_count_sp: Optional[int] = None
        self.enemy_count_coop: Optional[int] = None
        self.enemy_count_dm: Optional[int] = None

        self._bounds: Optional[MapBounds] = None

    def get_bounds(self) -> MapBounds:
        if self._bounds is not None:
            return self._bounds

        x1 = 32678.0
        y1 = 32678.0
        x2 = -32678.0
        y2 = -32678.0
        for v in self.vertices:
            x1 = min(x1, v.x)
            y1 = min(y1, v.y)
            x2 = max(x2, v.x)
            y2 = max(y2, v.y)

        self._bounds = (x1, y1, x2, y2)
        return self._bounds

    def to_row(self) -> Dict[str, any]:
        return {
            'entry_id': self.entry_id,
            'name': self.name[:8],
            'title': self.title[:1022] if self.title is not None else None,
            'format': self.format.value,
            'line_count': len(self.lines),
            'side_count': len(self.sides),
            'thing_count': len(self.things),
            'sector_count': len(self.sectors),
            'allow_jump': self.allow_jump,
            'allow_crouch': self.allow_crouch,
            'par_time': self.par_time & 0xFFFFFFFF if self.par_time is not None else None,
            'music': self.music[:255] if self.music is not None else None,
            'next': self.next[:255] if self.next is not None else None,
            'next_secret': self.next_secret[:255] if self.next_secret is not None else None,
            'cluster': self.cluster & 0xFFFFFFFF if self.cluster is not None else None,
            'complexity': self.complexity,

            'nodes': self.nodes_type.value,
            'nodes_gl': self.nodes_gl_type.value,

            'enemy_count_sp': self.enemy_count_sp,
            'enemy_count_coop': self.enemy_count_coop,
            'enemy_count_dm': self.enemy_count_dm,
        }
