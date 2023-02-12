import io
from hashlib import sha1
from pathlib import Path
from typing import Optional, Dict

from mido import MidiFile

from archives.archivefilebase import ArchiveFileBase
from doom.strings_music import MUSIC_STRINGS
from extractors.extractedinfo import ExtractedInfo, MusicType, MusicInfo
from extractors.extractorbase import ExtractorBase
from indexer.game import Game


class MusicExtractor(ExtractorBase):

    def extract(self, info: ExtractedInfo):
        if info.archive_list is None:
            self.logger.debug('Cannot extract music without an archive list.')
            return

        music_files: Dict[str, ArchiveFileBase] = {}

        # Collect all MIDI/MUS file types as they are always music.
        for archive in info.archive_list.archives:
            if archive.is_main:
                continue

            for file in archive.files:
                if file.type == 'midi' or file.type == 'mus':
                    music_files[file.name] = file

        source = self.get_music_source(info.game)
        if source in MUSIC_STRINGS[source]['maps']:

            # Set default music tracks for maps.
            self.assign_game_music_defaults(info, MUSIC_STRINGS[source]['maps'])

            # Add extra known music tracks.
            for music_name in MUSIC_STRINGS[source]['extra']:
                file = info.archive_list.file_find_basename(music_name, False)
                if file is None:
                    continue
                music_files[file.name] = file

        # Get music files assigned to maps.
        for map in info.maps:
            if map.music is None and map.music != '':
                continue
            file = info.archive_list.file_find_basename(map.music, False)
            if file is not None:
                music_files[file.name] = file

        # Process all found music files.
        for name, file in music_files.items():
            if file.type == 'midi':
                music_type = MusicType.MIDI
            elif file.type == 'mus':
                music_type = MusicType.MUS
            elif file.type == 'mp3':
                music_type = MusicType.MP3
            elif file.type == 'vorbis':
                music_type = MusicType.VORBIS
            elif file.type == 'opus':
                music_type = MusicType.OPUS
            elif file.type == 'wav':
                music_type = MusicType.WAV
            elif file.type == 's3m' or file.type == 'xm' or file.type == 'it' or file.type == 'mod':
                music_type = MusicType.TRACKER
            elif file.type == 'wma':
                music_type = MusicType.WMA
            elif file.type == 'vgm':
                music_type = MusicType.VGM
            elif file.type == 'spc':
                music_type = MusicType.SPC
            elif file.type == 'flac':
                music_type = MusicType.FLAC
            else:
                music_type = MusicType.UNKNOWN

            data = file.get_data()
            data_hash = sha1(data).digest()

            duration = self.get_music_duration(info, file)

            name_path = Path(file.name)
            name = name_path.stem
            info.music[name] = MusicInfo(name, music_type, data, data_hash, duration)

    @staticmethod
    def get_music_source(game: Game) -> Game:
        if game == Game.DOOM or game == Game.CHEX:
            return Game.DOOM
        elif game == Game.DOOM2 or game == Game.TNT or game == Game.PLUTONIA or game == Game.HACX:
            return Game.DOOM2

        return game

    @staticmethod
    def assign_game_music_defaults(info: ExtractedInfo, map_music: Dict[str, str]):
        if info.archive_list is None:
            return

        for map in info.maps:

            # Do not overwrite existing music name.
            if map.music is not None:
                continue

            # Assign default music, if the archive actually contains the music lump.
            default_music = map_music.get(map.name, None)
            if default_music is None:
                continue
            if info.archive_list.file_find_basename(default_music, False) is not None:
                map.music = default_music

    def get_music_duration(self, info: ExtractedInfo, file: ArchiveFileBase) -> Optional[int]:
        try:
            if file.type == 'midi':
                mid = MidiFile(file=io.BytesIO(file.get_data()))
                if mid.type < 2:
                    return mid.length
                else:
                    self.logger.debug(
                        'Cannot determine length of type 2 MIDI track {} in {}.'.format(file.name, info.path_idgames))

        except Exception as e:
            self.logger.error('Cannot determine length of music {} in {}: {}'.format(file.name, info.path_idgames, str(e)))

        return None
