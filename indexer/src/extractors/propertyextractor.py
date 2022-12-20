import re
from re import Pattern

from extractors.extractedinfo import ExtractedInfo
from extractors.extractorbase import ExtractorBase


RE_AUTHOR_SPLIT: Pattern = re.compile(r'[;:,&]|(\sand\s)|(\s\|\s)')
RE_WHITESPACE_COLLAPSE: Pattern = re.compile(r'\s\s+')

AUTHOR_WORDS_EXCLUDE = {
    'and',
    'others',
}


class PropertyExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        info.title = info.text_keys.get('title', None)
        if info.title is not None and len(info.title) > 255:
            info.title = '{}...'.format(info.title[:252])

        info.is_singleplayer = info.text_keys.get('game_style_singleplayer', None)
        info.is_cooperative = info.text_keys.get('game_style_cooperative', None)
        info.is_deathmatch = info.text_keys.get('game_style_deathmatch', None)
        info.description = info.text_keys.get('description', None)
        info.tools_used = info.text_keys.get('tools_used', None)
        info.build_time = info.text_keys.get('build_time', None)
        info.known_bugs = info.text_keys.get('known_bugs', None)
        info.credits = info.text_keys.get('credits', None)
        info.comments = info.text_keys.get('comments', None)

        parsed_authors = info.text_keys.get('authors', [])
        parsed_authors = list(set(parsed_authors))

        for author_list in parsed_authors:
            for author in RE_AUTHOR_SPLIT.split(author_list):
                if author is None:
                    continue
                author = author.strip()
                if len(author) and author not in AUTHOR_WORDS_EXCLUDE:
                    info.authors.append(author)
