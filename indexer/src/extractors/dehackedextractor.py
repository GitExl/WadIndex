import re
from io import StringIO
from typing import Dict

from archives.archivelist import ArchiveList
from doom.dehacked_parser import DehackedParser, DehackedParserError
from doom.strings_map_titles import STRINGS_MAP_TITLES
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase


RE_DEHACKED_FILE = re.compile(r'(\.deh|\.bex)', re.IGNORECASE)


class DehackedExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if not len(info.maps):
            return

        archive_list: ArchiveList = info.archive_list
        if archive_list is None:
            self.logger.debug('Cannot extract Dehacked info without an archive list.')
            return

        file = archive_list.file_find_basename('dehacked', False)
        if file is None:

            # Find deh/bex files in main archive as fallback.
            for file_info in info.main_archive.infolist():
                if RE_DEHACKED_FILE.match(file_info.filename):
                    file = info.main_archive.open(file_info.filename)
                    break

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
        if info.game not in STRINGS_MAP_TITLES:
            return

        # Find map titles from original strings/keys.
        map_names: Dict[str, str] = {}
        for key, replacement in parser.strings.items():
            map_lump = STRINGS_MAP_TITLES[info.game].get(key)
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
            map.par_time = par.time
