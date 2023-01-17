from doom.language_parser import LanguageParser, LanguageParserError, LocaleStrings
from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase
from indexer.game import Game
from utils.lexer import LexerError


class LanguageExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if info.archive_list is None:
            return
        if info.game is None or info.game == Game.UNKNOWN:
            return

        archive_list = info.archive_list
        language_files = archive_list.file_find_all_regexp('language($|\\.)', False)
        if not len(language_files):
            return

        info.locale_strings = LocaleStrings()
        for language_file in language_files:
            text = language_file.get_data().decode('latin1')

            try:
                parser = LanguageParser(text)
                locale_strings = parser.parse_locale_strings(info.game)
            except LexerError as e:
                self.logger.stream('language_parser_lexer_error', info.path_idgames.as_posix())
                self.logger.stream('language_parser_lexer_error', str(e))
                continue
            except LanguageParserError as e:
                self.logger.stream('language_parser_error', info.path_idgames.as_posix())
                self.logger.stream('language_parser_error', str(e))
                continue

            info.locale_strings.add_from(locale_strings)
