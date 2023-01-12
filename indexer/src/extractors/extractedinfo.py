from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from zipfile import ZipFile

from PIL.Image import Image

from archives.archivebase import ArchiveBase
from archives.archivelist import ArchiveList
from doom.map import Map
from indexer.engine import Engine
from indexer.entry import Entry
from indexer.game import Game


class MusicType(Enum):
    MIDI = 'mid'
    MUS = 'mus'


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
    entry: Optional[Entry] = None

    main_archive: Optional[ZipFile] = None
    archive: Optional[ArchiveBase] = None
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
    authors: List[str] = field(default_factory=lambda: [])
    graphics: Dict[str, GraphicInfo] = field(default_factory=lambda: {})
    maps: List[Map] = field(default_factory=lambda: [])
    music: Dict[str, MusicInfo] = field(default_factory=lambda: {})
