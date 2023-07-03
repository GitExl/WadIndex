import re
from dataclasses import dataclass
from typing import Iterable, Pattern, List, Optional, Tuple

from utils.url_clean import url_clean

RE_AUTHOR_SPLIT: Pattern = re.compile(r'[;:,&\+]|(\sand\s)|(\s\|\s)', re.IGNORECASE)
RE_WHITESPACE_COLLAPSE: Pattern = re.compile(r'\s\s+')
RE_USELESS: Pattern = re.compile(r'\s(et al)\s?|\-\-|\=\=')

RE_AUTHOR_NICKNAME = re.compile(r'(.*?)\s[\"\'\(](.*?)[\"\'\)]\s(.*)')
RE_AUTHOR_NICKNAME_AKA = re.compile(r'(.*?)\s(?:aka|a\.k\.a|a\.k\.a\.)\s(.*)', re.IGNORECASE)
RE_AUTHOR_NICKNAME_LAST = re.compile(r'(.*?)\s[\(\[](.*)[\)\]]')

AUTHOR_WORDS_EXCLUDE = {
    'By',
    'and',
    'others',
}


@dataclass(frozen=True)
class Author:
    name: str
    alias: str
    full_name: Optional[str]
    nickname: Optional[str]


def parse(text: Iterable) -> List[Author]:
    authors: List[Author] = []

    for line in text:
        for name in RE_AUTHOR_SPLIT.split(line):
            if name is None:
                continue

            name = RE_USELESS.sub(' ', name)
            name = RE_WHITESPACE_COLLAPSE.sub(' ', name)
            name = name.strip()
            if not len(name) or name in AUTHOR_WORDS_EXCLUDE:
                continue

            # Attempt to get full name and nickname.
            full_name, nickname = get_parts(name)
            alias = url_clean(name)

            if nickname is not None:
                nickname = nickname.strip('"\'')

            if full_name is not None:
                full_name = full_name.strip()
                if full_name.count(' ') > 3:
                    full_name = None
            elif 4 > name.count(' ') > 1:
                full_name = name

            if nickname is not None:
                nickname = nickname.strip()
                # @TODO: strip "aka" or "a.k.a." from start

            author = Author(name, alias, full_name, nickname)
            authors.append(author)

    return authors


def get_parts(name: str) -> Tuple[Optional[str], Optional[str]]:

    # Chris Kendell aka "VisionThing" - after aka, inside quotes
    # Matt Bollier a.k.a. Fogey - after a.k.a(.), inside quotes
    nickname_match = RE_AUTHOR_NICKNAME_AKA.match(name)
    if nickname_match is not None and nickname_match[1] and nickname_match[2]:
        return nickname_match[1], nickname_match[2]

    # Someone "Nickname" Lastname - in quotes is nickname
    # Ivar 'jallamann' Remøy - in single quotes is nickname
    # James (Jay) Cook - in brackets is nickname
    nickname_match = RE_AUTHOR_NICKNAME.match(name)
    if nickname_match is not None and nickname_match[1] and nickname_match[2] and nickname_match[3]:
        return nickname_match[1] + ' ' + nickname_match[3], nickname_match[2]

    # Mike Teske (Komet302) - if second part is one word, assume nickname
    # Ninja_of_DooM (Andrew Fernie) - if first part is one word, assume nickname
    nickname_match = RE_AUTHOR_NICKNAME_LAST.match(name)
    if nickname_match is not None and nickname_match[1] and nickname_match[2]:
        if ' ' not in nickname_match[1]:
            return nickname_match[2], nickname_match[1]
        return nickname_match[1], nickname_match[2]

    # ZeDude70 - single word is just a nickname
    if not ' ' in name:
        return None, name

    return None, None
