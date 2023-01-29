import zlib
from typing import Optional

from doom.map.map import Map
from doom.map.map_data_finder import MapData
from doom.nodes.node_types import NodeTypes, NodeTypesGL
from doom.nodes.nodes_reader_base import NodesReaderBase
from doom.nodes.nodes_reader_extended import NodesReaderExtended
from doom.nodes.nodes_reader_vanilla import NodesReaderVanilla
from doom.nodes.nodes_reader_zdoomgl import NodesReaderZDoomGL
from utils.logger import Logger


class NodesFinder:

    def __init__(self, map: Map, map_data: MapData, logger: Logger, path: str):
        self.map: Map = map
        self.map_data: MapData = map_data
        self.logger: Logger = logger
        self.path: str = path

        self.nodes_type: NodeTypes = NodeTypes.NONE
        self.nodes_data: Optional[bytes] = None

        self.nodes_gl_type: NodeTypesGL = NodeTypesGL.NONE
        self.nodes_gl_data: Optional[bytes] = None

        self._find()

    def get_reader(self) -> Optional[NodesReaderBase]:

        # Prefer ZDoom GL nodes.
        if self.nodes_gl_type == NodeTypesGL.ZDOOM_GL1:
            return NodesReaderZDoomGL(self.map, self.map_data, self.nodes_gl_data[4:], 1)
        elif self.nodes_gl_type == NodeTypesGL.ZDOOM_GL2:
            return NodesReaderZDoomGL(self.map, self.map_data, self.nodes_gl_data[4:], 2)
        elif self.nodes_gl_type == NodeTypesGL.ZDOOM_GL3:
            return NodesReaderZDoomGL(self.map, self.map_data, self.nodes_gl_data[4:], 3)

        elif self.nodes_gl_type == NodeTypesGL.ZDOOM_GL1_COMPRESSED:
            return NodesReaderZDoomGL(self.map, self.map_data, zlib.decompress(self.nodes_gl_data[4:]), 1)
        elif self.nodes_gl_type == NodeTypesGL.ZDOOM_GL2_COMPRESSED:
            return NodesReaderZDoomGL(self.map, self.map_data, zlib.decompress(self.nodes_gl_data[4:]), 2)
        elif self.nodes_gl_type == NodeTypesGL.ZDOOM_GL3_COMPRESSED:
            return NodesReaderZDoomGL(self.map, self.map_data, zlib.decompress(self.nodes_gl_data[4:]), 3)

        # # Use GLBSP nodes if available.
        # elif self.nodes_gl_type == NodeTypesGL.GLBSP1:
        #     return self._load_nodes_glbsp(1, self.map_data)
        # elif self.nodes_gl_type == NodeTypesGL.GLBSP2:
        #     return self._load_nodes_glbsp(2, self.map_data)
        # elif self.nodes_gl_type == NodeTypesGL.GLBSP3:
        #     return self._load_nodes_glbsp(3, self.map_data)
        # elif self.nodes_gl_type == NodeTypesGL.GLBSP4:
        #     return self._load_nodes_glbsp(4, self.map_data)
        # elif self.nodes_gl_type == NodeTypesGL.GLBSP5:
        #     return self._load_nodes_glbsp(5, self.map_data)

        # Fallback to extended nodes.
        elif self.nodes_type == NodeTypes.EXTENDED:
            return NodesReaderExtended(self.map, self.map_data, self.nodes_data[4:])
        elif self.nodes_type == NodeTypes.EXTENDED_COMPRESSED:
            return NodesReaderExtended(self.map, self.map_data, zlib.decompress(self.nodes_data[4:]))

        # Fallback to Deep nodes.
        elif self.nodes_type == NodeTypes.DEEP:
            return NodesReaderVanilla(self.map, self.map_data, deep=True)

        # Use vanilla if nothing else is available.
        elif self.nodes_type == NodeTypes.VANILLA:
            return NodesReaderVanilla(self.map, self.map_data)

        return None

    def _find(self):

        # ZNODES lump
        znodes_file = self.map_data.files.get('ZNODES')
        if znodes_file is not None:
            znodes_data = znodes_file.get_data()
            gl_type = self.detect_gl_nodes_type(znodes_data)
            if gl_type != NodeTypesGL.NONE:
                self.nodes_gl_type = gl_type
                self.nodes_gl_data = znodes_data

        # NODES lump
        nodes_file = self.map_data.files.get('NODES')
        if nodes_file is not None:
            nodes_data = nodes_file.get_data()

            # DeepBSP NODES
            if len(nodes_data) >= 8 and nodes_data[:8] == b'xNd4\0\0\0\0':
                self.nodes_type = NodeTypes.DEEP

            # Extended NODES
            elif len(nodes_data) >= 4 and nodes_data[:4] == b'XNOD':
                self.nodes_type = NodeTypes.EXTENDED
            elif len(nodes_data) >= 4 and nodes_data[:4] == b'ZNOD':
                self.nodes_type = NodeTypes.EXTENDED_COMPRESSED

            # Assume vanilla nodes if data is present.
            elif len(nodes_data):
                self.nodes_type = NodeTypes.VANILLA

            self.nodes_data = nodes_data

        # ZGL nodes in SSECTORS lump
        subsectors_file = self.map_data.files.get('SSECTORS')
        if subsectors_file is not None:
            subsectors_data = subsectors_file.get_data()
            gl_type = self.detect_gl_nodes_type(subsectors_data)
            if gl_type != NodeTypesGL.NONE:
                self.nodes_gl_type = gl_type
                self.nodes_gl_data = subsectors_data

        # GL nodes in GL_* lumps
        if len(self.map_data.name) > 5:
            glbsp_marker_name = 'GL_LEVEL'
        else:
            glbsp_marker_name = 'GL_{}'.format(self.map_data.name)
        glnodes_marker = self.map_data.files.get(glbsp_marker_name)
        if glnodes_marker is not None:
            glnodes_vert_file = self.map_data.files.get('GL_VERT')
            glnodes_segs_file = self.map_data.files.get('GL_SEGS')
            glnodes_ssect_file = self.map_data.files.get('GL_SSECT')
            glnodes_nodes_file = self.map_data.files.get('GL_NODES')
            if glnodes_vert_file is not None and glnodes_segs_file is not None or glnodes_ssect_file is not None and glnodes_nodes_file is not None:
                gl_vert_data = glnodes_vert_file.get_data()
                if len(gl_vert_data):
                    self.nodes_gl_type = NodeTypesGL.GLBSP1
                    if gl_vert_data[:4] == b'gNd2':
                        self.nodes_gl_type = NodeTypesGL.GLBSP2
                    elif gl_vert_data[:4] == b'gNd3':
                        self.nodes_gl_type = NodeTypesGL.GLBSP3
                    elif gl_vert_data[:4] == b'gNd4':
                        self.nodes_gl_type = NodeTypesGL.GLBSP4
                    elif gl_vert_data[:4] == b'gNd5':
                        self.nodes_gl_type = NodeTypesGL.GLBSP5

    @staticmethod
    def detect_gl_nodes_type(data: bytes) -> NodeTypesGL:
        if len(data) < 4:
            return NodeTypesGL.NONE

        if data[:4] == b'XGLN':
            return NodeTypesGL.ZDOOM_GL1
        elif data[:4] == b'ZGLN':
            return NodeTypesGL.ZDOOM_GL1_COMPRESSED

        elif data[:4] == b'XGL2':
            return NodeTypesGL.ZDOOM_GL2
        elif data[:4] == b'ZGL2':
            return NodeTypesGL.ZDOOM_GL2_COMPRESSED

        elif data[:4] == b'XGL3':
            return NodeTypesGL.ZDOOM_GL3
        elif data[:4] == b'ZGL3':
            return NodeTypesGL.ZDOOM_GL3_COMPRESSED

        return NodeTypesGL.NONE
