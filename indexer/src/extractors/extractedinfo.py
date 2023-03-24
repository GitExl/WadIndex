from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from zipfile import ZipFile

from PIL.Image import Image

from archives.archivebase import ArchiveBase
from archives.archivelist import ArchiveList
from doom.language_parser import LocaleStrings
from doom.map.map import Map
from indexer.engine import Engine
from indexer.game import Game
from utils.author_parser import Author


class MusicType(Enum):
    UNKNOWN = 'unk'
    MIDI = 'midi'
    MUS = 'mus'
    TRACKER = 'tracker'
    MP3 = 'mp3'
    WAV = 'wav'
    VORBIS = 'vorbis'
    OPUS = 'opus'
    WMA = 'wma'
    VGM = 'vgm'
    SPC = 'spc'
    FLAC = 'flac'


@dataclass
class MusicInfo:
    name: str
    type: MusicType
    data: bytes
    hash: bytes
    duration: Optional[int] = None
    id: Optional[int] = None

    def to_row(self) -> Dict[str, any]:
        return {
            'type': self.type.value,
            'hash': self.hash,
            'duration': self.duration,
        }


@dataclass
class GraphicInfo:
    image: Image
    image_thumb: Image
    image_hash: bytes
    index: int
    is_primary: bool = False


@dataclass
class ExtractedInfo:
    path_local: Path
    path_local_base: Path
    path_idgames: Path
    path_idgames_base: Path
    filename_base: str
    file_size: int
    file_modified: int

    main_archive: Optional[ZipFile] = None
    archives: List[ArchiveBase] = field(default_factory=lambda: [])
    archive_list: Optional[ArchiveList] = None

    text_keys: Dict[str, any] = field(default_factory=lambda: {})
    text_contents: Optional[str] = None

    title: Optional[str] = None
    game: Game = Game.UNKNOWN
    engine: Engine = Engine.UNKNOWN
    is_singleplayer: Optional[bool] = None
    is_cooperative: Optional[bool] = None
    is_deathmatch: Optional[bool] = None
    description: Optional[str] = None
    tools_used: Optional[str] = None
    build_time: Optional[str] = None
    known_bugs: Optional[str] = None
    credits: Optional[str] = None
    comments: Optional[str] = None
    authors: List[Author] = field(default_factory=lambda: [])
    graphics: Dict[str, GraphicInfo] = field(default_factory=lambda: {})
    maps: List[Map] = field(default_factory=lambda: [])
    music: Dict[str, MusicInfo] = field(default_factory=lambda: {})
    locale_strings: Optional[LocaleStrings] = None
