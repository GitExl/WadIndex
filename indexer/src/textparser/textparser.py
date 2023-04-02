import re

from re import Pattern, RegexFlag
from typing import TextIO, Tuple, Optional, List

from indexer.engine import Engine
from indexer.game import Game
from textparser.textkeys import TextKeyStore, TEXT_KEYS, TEXT_BOOLEAN, TEXT_GAMES, TEXT_ENGINE, TEXT_DIFFICULTY, \
    TextKeyTransform, TextKeyType, TextKeyProcess
from utils.logger import Logger


KEY_VALUE_MIN_TRAILING_WHITESPACE = 3

RE_KEY_VALUE: Pattern = re.compile(r':(?!//)')
RE_HEADER: Pattern = re.compile(r'[+]?[=\-]{2,}')
RE_WHITESPACE_COLLAPSE: Pattern = re.compile(r'\s\s+')
RE_ORDERED_LIST: Pattern = re.compile(r'[0-9]\.\s')


class TextParser:

    def __init__(self, logger: Logger):
        self.logger: Logger = logger
        self.info: dict = {}
        self.pairs: List[Tuple[str, str]] = []

    def parse(self, file: TextIO):
        key = None
        values = []
        newline_count = 0

        for line in file:
            line = line.rstrip()

            # Skip blank lines, but track how many.
            is_blank = len(line.strip()) == 0
            if is_blank:
                newline_count += 1

            # After some newlines, assume a break in between key\values.
            elif newline_count > 2:
                self.add_pair(key, values)
                key = None
                values = []

            newline_count = 0

            # Headers are treated as the key of a new key\value pair.
            if not is_blank:
                header = self.detect_header(line)
                if header is not None:
                    self.add_pair(key, values)
                    key = header.lower()
                    values = []
                    continue

            # Detect key\value pairs or just values to append to the current pair.
            detect_key, detect_value = self.detect_key_value(line)
            if detect_key is not None:
                self.add_pair(key, values)
                key = detect_key
                values = [detect_value]

            elif detect_value is not None:
                values.append(detect_value)

        # Add the last key\value pair if any.
        self.add_pair(key, values)

        # Convert pairs into useful data.
        for key, value in self.pairs:
            if not self.parse_pair(key, value) and self.logger.verbosity == Logger.VERBOSITY_DEBUG:
                self.logger.stream('pairs', '{} :: {}'.format(key, value))
                self.logger.stream('keys', key)

        # Postprocess data
        for key, value in  self.info.items():
            type_info = TEXT_KEYS.get(key)

            process = type_info.get('process', None)
            if process == TextKeyProcess.TEXT_TO_MARKDOWN:
                self.info[key] = self.text_to_markdown(value)

    def add_pair(self, key: Optional[str], values: List[str]):
        if len(values) == 0 or key is None or len(key) == 0:
            return

        # Strip useless trailing characters from keys.
        if key[0] == '*':
            key = key.strip('* ')

        for value in values:
            self.pairs.append((key, value))

    @staticmethod
    def detect_key_value(text: str) -> Tuple[Optional[str], Optional[str]]:

        # Not long enough to contain anything useful.
        if len(text) < KEY_VALUE_MIN_TRAILING_WHITESPACE:
            return None, text.strip()

        # If it starts with enough trailing whitespace, it must just be another value part.
        start = text[0:KEY_VALUE_MIN_TRAILING_WHITESPACE]
        if start.isspace():
            return None, text.strip()

        # If there is at least one colon, this must be a new key\value pair.
        parts = RE_KEY_VALUE.split(text, 1)
        if len(parts) < 2:
            return None, text.strip()

        return parts[0].strip().lower(), parts[1].strip()

    @staticmethod
    def detect_header(text: str) -> Optional[str]:
        text = text.strip()

        # Starts with "5. "
        list_match = RE_ORDERED_LIST.match(text)
        if list_match is not None:
            text = text[list_match.end():]

        # * Detect this *
        if len(text) > 2 and text[0] == '*' and text[-1] == '*':
            return text.strip('*').strip()

        # Strip the initial character from the start and end of the string.
        initial = text[0]
        stripped_text = text.strip(initial).strip()
        if len(stripped_text) == 0:
            return ''

        startswith = RE_HEADER.match(text)
        if startswith is None:
            return None

        # Strip the initial character from the start and end of the string.
        initial = text[0]
        text = text.strip(initial).strip()

        # * Detect this *
        if len(text) > 2 and text[0] == '*' and text[-1] == '*':
            text = text.strip('*').strip()

        if len(text):
            return text.strip()

        return ''

    def parse_pair(self, key: str, value: str) -> bool:
        parser_key, parser_data = self.match_key(key, TEXT_KEYS)
        if not parser_key:
            return False

        # Skip single value keys if a value already exists.
        type = parser_data.get('type', TextKeyType.SINGLE)
        if type == TextKeyType.SINGLE and parser_key in self.info:
            return True

        transform = parser_data.get('transform', TextKeyTransform.TEXT)
        store = parser_data.get('store', TextKeyStore.STORE)

        # Transform value.
        if transform == TextKeyTransform.TEXT:
            value = str(value).strip()
            value = RE_WHITESPACE_COLLAPSE.sub(' ', value)
        elif transform == TextKeyTransform.BOOL:
            value = self.parse_bool(value)
        elif transform == TextKeyTransform.DIFFICULTY:
            value = self.parse_difficulty(value)
        elif transform == TextKeyTransform.GAME:
            value = self.parse_game(value)
        elif transform == TextKeyTransform.ENGINE:
            value = self.parse_engine(value)
        elif transform is not None:
            raise Exception('Unimplemented textparser key transform "{}".'.format(transform))

        # Store value with possible existing value.
        if store == TextKeyStore.STORE:
            pass
        elif store == TextKeyStore.BINARY_OR:
            if value is None:
                return True
            if parser_key in self.info:
                value = self.info[parser_key] | value
        else:
            raise Exception('Unimplemented textparser key store "{}".'.format(store))

        # Place into requested data structure.
        if type == TextKeyType.SINGLE:
            self.info[parser_key] = value
        elif type == TextKeyType.ARRAY:
            if parser_key not in self.info:
                self.info[parser_key] = []
            self.info[parser_key].append(value)
        elif type == TextKeyType.SET:
            if parser_key not in self.info:
                self.info[parser_key] = set()
            self.info[parser_key].add(value)
        else:
            raise Exception('Unimplemented textparser key type "{}".'.format(store))

        return True

    @staticmethod
    def match_key(value: str, parser_data: dict) -> Tuple[Optional[str], Optional[dict]]:
        if not len(value):
            return None, None

        for parser_key, data in parser_data.items():
            if 'keys' in data and value in data['keys']:
                return parser_key, data

            if 're' in data:
                for regexp in data['re']:
                    if re.search(regexp, value, RegexFlag.IGNORECASE):
                        return parser_key, data

        return None, None

    def parse_bool(self, value: str) -> bool:
        value = value.lower().strip()
        if not len(value):
            return False

        parser_key, data = self.match_key(value, TEXT_BOOLEAN)
        if parser_key == 'true':
            return True
        elif parser_key == 'false':
            return False

        if value.isnumeric() and int(value) > 0:
            return True

        if self.logger.verbosity == Logger.VERBOSITY_DEBUG:
            self.logger.stream('text_parser_value_bool', '{}'.format(value))

        return False

    def parse_game(self, value: str) -> Game:
        value = value.lower().strip()

        parser_key, data = self.match_key(value, TEXT_GAMES)
        if parser_key:
            return Game(parser_key)

        if self.logger.verbosity == Logger.VERBOSITY_DEBUG:
            self.logger.stream('text_parser_value_game', '{}'.format(value))

        return Game.UNKNOWN

    def parse_engine(self, value: str) -> Engine:
        value = value.lower().strip()

        # TODO: only allow one to match from all, otherwise many false positives
        parser_key, data = self.match_key(value, TEXT_ENGINE)
        if parser_key:
            return Engine(parser_key)

        if self.logger.verbosity == Logger.VERBOSITY_DEBUG:
            self.logger.stream('text_parser_value_engine', '{}'.format(value))

        return Engine.UNKNOWN

    def parse_difficulty(self, value: str) -> Optional[bool]:
        value = value.lower().strip()

        parser_key, data = self.match_key(value, TEXT_DIFFICULTY)
        if parser_key is not None:
            return parser_key == 'true'

        if self.logger.verbosity == Logger.VERBOSITY_DEBUG:
            self.logger.stream('text_parser_value_difficulty', '{}'.format(value))

        return None

    @staticmethod
    def text_to_markdown(data) -> str:
        if isinstance(data, str):
            data = [data]
        if isinstance(data, set):
            data = list(data)

        paragraphs = []

        lines = []
        for data_line in data:
            if len(data_line) == 0:
                paragraphs.append(' '.join(lines))
                lines.clear()
                continue

            lines.append(data_line)

        return '\n\n'.join(paragraphs).strip()
