import re


_RE_URL_CLEAN = re.compile(r'[^\w\-]')
_RE_URL_DEDUP = re.compile(r'[\-]{2,}')


def url_clean(url: str) -> str:
    url = url.replace(' ', '-').replace('_', '-').lower()
    url = _RE_URL_CLEAN.sub('', url)
    url = _RE_URL_DEDUP.sub('-', url)
    return url[:255].strip()
