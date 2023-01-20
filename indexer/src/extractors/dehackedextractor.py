from io import StringIO
from typing import Dict

from archives.archivebase import ArchiveBase
from doom.dehacked_parser import DehackedParser, DehackedParserError
from doom.strings_builtin import MAP_TITLE_STRINGS
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase


class DehackedExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if not len(info.maps):
            return

        archive: ArchiveBase = info.archive
        if archive is None:
            self.logger.debug('Cannot extract Dehacked info without an archive.')
            return

        # TODO: also find dehacked files in ZIP as fallback
        file = archive.file_find_basename('dehacked')
        if file is None:
            return

        parser = None
        try:
            parser = DehackedParser()
            parser.parse(StringIO(file.get_data().decode('latin1')))
        except DehackedParserError as e:
            self.logger.stream('dehacked_parser_error', 'Parser error for {}: {}'.format(info.path_idgames.as_posix(), str(e)))
        except Exception as e:
            self.logger.stream('dehacked_parser_error', 'Exception for {}: {}'.format(info.path_idgames.as_posix(), e))

        if parser is None:
            return
        self.assign_map_titles(info, parser)
        self.assign_par_times(info, parser)

        # TODO: music names can be changed in strings, track here

    @staticmethod
    def assign_map_titles(info: ExtractedInfo, parser: DehackedParser):
        if info.game not in MAP_TITLE_STRINGS:
            return

        # Find map titles from original strings/keys.
        map_names: Dict[str, str] = {}
        for key, replacement in parser.strings.items():
            map_lump = MAP_TITLE_STRINGS[info.game].get(key)
            if map_lump is None:
                continue
            map_names[map_lump] = replacement

        # Assign map titles to maps without any.
        for map in info.maps:
            if map.title is not None:
                continue

            map_title = map_names.get(map.name.upper())
            if map_title is None:
                continue
            map.title = map_title

    @staticmethod
    def assign_par_times(info: ExtractedInfo, parser: DehackedParser):
        for map in info.maps:
            if map.par_time is not None:
                continue

            par = parser.pars.get(map.name.upper())
            if par is None:
                continue
            map.par_time = par
