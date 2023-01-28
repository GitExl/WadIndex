from typing import Optional

from doom.map.map_data_finder import MapData
from doom.map.nodes import NodeTypes, NodeTypesGL
from utils.logger import Logger


class NodesReader:

    def __init__(self, map_data: MapData, logger: Logger, path: str):
        self.map_data: MapData = map_data
        self.logger: Logger = logger
        self.path: str = path

        self.nodes_type: NodeTypes = NodeTypes.NONE
        self.nodes_data: Optional[bytes] = None

        self.nodes_gl_type: NodeTypesGL = NodeTypesGL.NONE
        self.nodes_gl_data: Optional[bytes] = None

    def detect(self):
        # https://zdoom.org/wiki/Node
        # https://zdoom.org/wiki/ZNODES
        # https://glbsp.sourceforge.net/specs.php
        # Also see https://github.com/ZDoom/gzdoom/blob/master/src/maploader/maploader.cpp#L3049

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
            glbsp_name = 'GL_LEVEL'
        else:
            glbsp_name = 'GL_{}'.format(self.map_data.name)
        glnodes_marker = self.map_data.files.get(glbsp_name)
        if glnodes_marker is not None:
            glnodes_vert_file = self.map_data.files.get('GL_VERT')
            if glnodes_vert_file is not None:
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

        self.logger.stream('map_nodes', '{}, {}, {}, {}'.format(self.path, self.map_data.name, self.nodes_type.name, self.nodes_gl_type.name))

    @staticmethod
    def detect_gl_nodes_type(data: bytes) -> NodeTypesGL:
        if len(data) < 4:
            return NodeTypesGL.NONE

        if data[:4] == b'XGLN':
            return NodeTypesGL.ZDOOM_GL
        elif data[:4] == b'ZGLN':
            return NodeTypesGL.ZDOOM_GL_COMPRESSED

        elif data[:4] == b'XGL2':
            return NodeTypesGL.ZDOOM_GL2
        elif data[:4] == b'ZGL2':
            return NodeTypesGL.ZDOOM_GL2_COMPRESSED

        elif data[:4] == b'XGL3':
            return NodeTypesGL.ZDOOM_GL3
        elif data[:4] == b'ZGL3':
            return NodeTypesGL.ZDOOM_GL3_COMPRESSED

        return NodeTypesGL.NONE
