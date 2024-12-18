from struct import Struct
from typing import Optional, Tuple, List

from doom.map.map import Map, MapNamespace, Line, LineFlags, Sector, Side, Thing, ThingFlags, Vertex, MapFormat
from doom.map.map_data_finder import MapData
from doom.map.map_reader_base import MapReaderBase
from indexer.game import Game


STRUCT_VERTEX: Struct = Struct('<hh')

STRUCT_LINE_DOOM: Struct = Struct('<HHHHHHH')
STRUCT_LINE_HEXEN: Struct = Struct('<HHHBBBBBBHH')

STRUCT_SIDE: Struct = Struct('<hh8s8s8sh')

STRUCT_SECTOR: Struct = Struct('<hh8s8shhh')

STRUCT_THING_DOOM: Struct = Struct('<hhHHH')
STRUCT_THING_HEXEN: Struct = Struct('<HhhhHHHBBBBBB')


def map_line_flags(value: int, namespace: MapNamespace) -> LineFlags:
    flags: LineFlags = LineFlags.NONE

    if value & 0x0001:
        flags |= LineFlags.BLOCK
    if value & 0x0002:
        flags |= LineFlags.BLOCK_MONSTER
    if value & 0x0004:
        flags |= LineFlags.TWO_SIDED
    if value & 0x0008:
        flags |= LineFlags.UNPEG_TOP
    if value & 0x0010:
        flags |= LineFlags.UNPEG_BOTTOM
    if value & 0x0020:
        flags |= LineFlags.SECRET
    if value & 0x0040:
        flags |= LineFlags.BLOCK_SOUND
    if value & 0x0080:
        flags |= LineFlags.HIDDEN
    if value & 0x0100:
        flags |= LineFlags.MAPPED

    if namespace == MapNamespace.STRIFE:
        if value & 0x0200:
            flags |= LineFlags.JUMP_OVER
        if value & 0x0400:
            flags |= LineFlags.BLOCK_FLOAT
        if value & 0x1000:
            flags |= LineFlags.TRANSLUCENT75
        if value & 0x2000:
            flags |= LineFlags.TRANSLUCENT25

    elif namespace == MapNamespace.ETERNITY:
        if value & 0x0400:
            flags |= LineFlags.WALKABLE

    elif namespace == MapNamespace.HEXEN or namespace == MapNamespace.ZDOOM:
        if value & 0x0200:
            flags |= LineFlags.REPEATS

        if value & 0x1800:
            flags |= LineFlags.PLAYER_USE
            flags |= LineFlags.PASS_USE
        elif value & 0x1400:
            flags |= LineFlags.MISSILE_CROSS
        elif value & 0x1000:
            flags |= LineFlags.PLAYER_PUSH
        elif value & 0x0C00:
            flags |= LineFlags.IMPACT
        elif value & 0x0800:
            flags |= LineFlags.MONSTER_CROSS
        elif value & 0x0400:
            flags |= LineFlags.PLAYER_USE

        if value & 0x2000:
            flags |= LineFlags.MONSTER_ACTIVATES
        if value & 0x4000:
            flags |= LineFlags.BLOCK_PLAYERS
        if value & 0x8000:
            flags |= LineFlags.BLOCK_ALL

    if namespace == MapNamespace.ZDOOM or namespace == MapNamespace.ETERNITY:
        if value & 0x0200:
            flags |= LineFlags.PASS_USE

    return flags


def map_thing_flags(value: int, namespace: MapNamespace) -> ThingFlags:
    flags: ThingFlags = ThingFlags.NONE

    if value & 0x0001:
        flags |= ThingFlags.SKILL_1 | ThingFlags.SKILL_2
    if value & 0x0002:
        flags |= ThingFlags.SKILL_3
    if value & 0x0004:
        flags |= ThingFlags.SKILL_4 | ThingFlags.SKILL_5

    if namespace == MapNamespace.STRIFE:
        if value & 0x0008:
            flags |= ThingFlags.STANDING
        if value & 0x0010:
            flags |= ThingFlags.NOT_SP
        if value & 0x0020:
            flags |= ThingFlags.AMBUSH
        if value & 0x0040:
            flags |= ThingFlags.FRIEND

        if value & 0x0300:
            flags |= ThingFlags.INVISIBLE
        else:
            if value & 0x0100:
                flags |= ThingFlags.TRANSLUCENT25
            if value & 0x0200:
                flags |= ThingFlags.TRANSLUCENT75

    elif namespace == MapNamespace.HEXEN:
        if value & 0x0008:
            flags |= ThingFlags.AMBUSH
        if value & 0x0010:
            flags |= ThingFlags.DORMANT
        if value & 0x0020:
            flags |= ThingFlags.CLASS1
        if value & 0x0040:
            flags |= ThingFlags.CLASS2
        if value & 0x0080:
            flags |= ThingFlags.CLASS3
        if value & 0x0100:
            flags |= ThingFlags.SP
        if value & 0x0200:
            flags |= ThingFlags.COOP
        if value & 0x0400:
            flags |= ThingFlags.DM

    else:
        if value & 0x0008:
            flags |= ThingFlags.AMBUSH
        if value & 0x0010:
            flags |= ThingFlags.NOT_SP

        # Boom\MBF
        if value & 0x0020:
            flags |= ThingFlags.NOT_DM
        if value & 0x0040:
            flags |= ThingFlags.NOT_COOP
        if value & 0x0080:
            flags |= ThingFlags.FRIEND

    return flags


def unpack_vertex(values: Tuple, namespace: MapNamespace):
    return Vertex(float(values[0]), float(values[1]))


def unpack_line_doom(values: Tuple, namespace: MapNamespace):
    return Line(values[0], values[1], values[5], values[6], map_line_flags(values[2], namespace), values[3],
                [values[4]], 0, 0, 0, 0, 0, None)


def unpack_line_hexen(values: Tuple, namespace: MapNamespace):
    return Line(
        values[0], values[1], values[9], values[10], map_line_flags(values[2], namespace), values[3],
        [0], values[4], values[5], values[6], values[7], values[8], None,
    )


def unpack_side(values: Tuple, namespace: MapNamespace):
    return Side(values[5], values[2], values[4], values[3], values[0], values[1])


def unpack_sector(values: Tuple, namespace: MapNamespace):
    return Sector(values[0], values[1], values[2], values[3], values[6], values[5], values[4])


def unpack_thing_doom(values: Tuple, namespace: MapNamespace):
    return Thing(float(values[0]), float(values[1]), 0, values[2], values[3], map_thing_flags(values[4], namespace), 0, 0, 0, 0, 0, 0, 0, None)


def unpack_thing_hexen(values: Tuple, namespace: MapNamespace):
    return Thing(
        float(values[1]), float(values[2]), float(values[3]), values[4], values[5], map_thing_flags(values[4], namespace), values[0], values[7],
        values[8], values[9], values[10], values[11], values[12], None
    )


class BinaryMapReader(MapReaderBase):

    def read(self, map_data: MapData) -> Optional[Map]:
        map_name: str = map_data.name

        namespace: MapNamespace = MapNamespace.DOOM
        if self.game == Game.STRIFE:
            namespace = MapNamespace.STRIFE
        elif self.game == Game.HEXEN:
            namespace = MapNamespace.HEXEN
        # TODO: ZDoom, Eternity?

        vertices: List[Vertex] = BinaryMapReader._read_binary_data(map_data, 'VERTEXES', unpack_vertex, STRUCT_VERTEX)
        sides: List[Side] = BinaryMapReader._read_binary_data(map_data, 'SIDEDEFS', unpack_side, STRUCT_SIDE)
        sectors: List[Sector] = BinaryMapReader._read_binary_data(map_data, 'SECTORS', unpack_sector, STRUCT_SECTOR)

        if map_data.format == MapFormat.DOOM:
            lines: List[Line] = BinaryMapReader._read_binary_data(map_data, 'LINEDEFS', unpack_line_doom, STRUCT_LINE_DOOM)
            things: List[Thing] = BinaryMapReader._read_binary_data(map_data, 'THINGS', unpack_thing_doom, STRUCT_THING_DOOM)
        else:
            lines: List[Line] = BinaryMapReader._read_binary_data(map_data, 'LINEDEFS', unpack_line_hexen, STRUCT_LINE_HEXEN)
            things: List[Thing] = BinaryMapReader._read_binary_data(map_data, 'THINGS', unpack_thing_hexen, STRUCT_THING_HEXEN)

        for index, side in enumerate(sides):
            sides[index] = Side(
                side.sector,
                side.texture_upper.decode('latin1').partition('\x00')[0],
                side.texture_mid.decode('latin1').partition('\x00')[0],
                side.texture_lower.decode('latin1').partition('\x00')[0],
                side.texture_x,
                side.texture_y,
            )

        for index, sector in enumerate(sectors):
            sectors[index] = Sector(
                sector.z_floor,
                sector.z_ceiling,
                sector.texture_floor.decode('latin1').partition('\x00')[0],
                sector.texture_ceiling.decode('latin1').partition('\x00')[0],
                sector.ids,
                sector.type,
                sector.light,
            )

        return Map(map_name, namespace, map_data.format, vertices, lines, sides, sectors, things)

    @staticmethod
    def _read_binary_data(map_data: MapData, file_name: str, unpack_func, data_struct: Struct):
        file = map_data.files.get(file_name)
        if file is None:
            return []
        data = file.get_data()

        # Trim any extraneous data, iter_unpack will not accept it.
        if len(data) % data_struct.size != 0:
            aligned = data_struct.size * int(len(data) / data_struct.size)
            data = data[0:aligned]

        items = [None] * (len(data) // data_struct.size)
        for index, unpacked in enumerate(data_struct.iter_unpack(data)):
            items[index] = unpack_func(unpacked, map_data.namespace)

        return items
