from struct import Struct

from doom.map.map import Map
from doom.map.map_data_finder import MapData
from doom.nodes.nodes import Nodes


class NodesReaderBase:

    def __init__(self, map: Map, map_data: MapData):
        self.map: Map = map
        self.map_data: MapData = map_data

    def read(self) -> Nodes:
        return Nodes([], [], [], [])

    def read_binary_data_lump(self, file_name: str, unpack_func, data_struct: Struct):
        file = self.map_data.files.get(file_name)
        if file is None:
            return []

        return self.read_binary_data(file.get_data(), unpack_func, data_struct)

    def read_binary_data(self, data: bytes, unpack_func, data_struct: Struct):

        # Trim any extraneous data, iter_unpack will not accept it.
        if len(data) % data_struct.size != 0:
            aligned = data_struct.size * int(len(data) / data_struct.size)
            data = data[0:aligned]

        items = [None] * (len(data) // data_struct.size)
        for index, unpacked in enumerate(data_struct.iter_unpack(data)):
            items[index] = unpack_func(unpacked)

        return items

    def read_binary_data_memoryview(self, data: memoryview, unpack_func, data_struct: Struct):
        items = [None] * (len(data) // data_struct.size)
        for index, unpacked in enumerate(data_struct.iter_unpack(data)):
            items[index] = unpack_func(unpacked)

        return items
