import re
from typing import Iterable, Pattern, List

RE_AUTHOR_SPLIT: Pattern = re.compile(r'[;:,&]|(\sand\s)|(\s\|\s)')
RE_WHITESPACE_COLLAPSE: Pattern = re.compile(r'\s\s+')


AUTHOR_WORDS_EXCLUDE = {
    'and',
    'others',
}


def parse(text: Iterable) -> List[str]:
    authors: List[str] = []

    for line in text:
        for author in RE_AUTHOR_SPLIT.split(line):
            if author is None:
                continue

            author = author.strip()
            if len(author) and author not in AUTHOR_WORDS_EXCLUDE:
                authors.append(author)

    return authors
