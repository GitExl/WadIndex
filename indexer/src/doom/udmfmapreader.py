from typing import Dict, Optional

from doom.mapfinder import MapData
from doom.mapreaderbase import MapReaderBase
from doom.map import Map, MapNamespace, MapFormat
from doom.udmfparser import UDMFParser, UDMFParserError
from utils.lexer import LexerError


UDMF_NAMESPACE_MAP: Dict[str, MapNamespace] = {
    'doom': MapNamespace.DOOM,
    'heretic': MapNamespace.HERETIC,
    'hexen': MapNamespace.HEXEN,
    'strife': MapNamespace.STRIFE,
    'zdoom': MapNamespace.ZDOOM,
    'eternity': MapNamespace.ETERNITY,
}


class UDMFMapReader(MapReaderBase):

    def read(self, map_data: MapData) -> Optional[Map]:
        map_lump = map_data.files.get('TEXTMAP')
        if map_lump is None:
            self.logger.error('Cannot load UDMF map that has no TEXTMAP lump.')
            return None

        map_name = map_data.name
        text = map_lump.get_data().decode('latin1')

        try:
            parser = UDMFParser()
            parser.parse(text)
            namespace = self.map_udmf_namespace(parser.namespace.lower())
            return Map(map_name, namespace, MapFormat.UDMF, parser.vertices, parser.lines, parser.sides, parser.sectors, parser.things)

        except LexerError as e:
            self.logger.error('Unable to lex "{}": {}'.format(map_name, e))
        except UDMFParserError as e:
            self.logger.error('Unable to parse "{}": {}'.format(map_name, e))

        return None

    def map_udmf_namespace(self, udmf_namespace: str) -> MapNamespace:
        if udmf_namespace in UDMF_NAMESPACE_MAP:
            return UDMF_NAMESPACE_MAP[udmf_namespace]

        self.logger.warn('Unknown UDMF namespace "{}", using Doom fallback.'.format(udmf_namespace))
        return MapNamespace.DOOM
