from enum import Enum


class NodeTypes(Enum):
    NONE = 0
    VANILLA = 1
    DEEP = 2
    EXTENDED = 3
    EXTENDED_COMPRESSED = 4


class NodeTypesGL(Enum):
    NONE = 0
    ZDOOM_GL1 = 1
    ZDOOM_GL2 = 2
    ZDOOM_GL3 = 3
    ZDOOM_GL1_COMPRESSED = 4
    ZDOOM_GL2_COMPRESSED = 5
    ZDOOM_GL3_COMPRESSED = 6
    GLBSP1 = 7
    GLBSP2 = 8
    GLBSP3 = 9
    GLBSP4 = 10
    GLBSP5 = 11
