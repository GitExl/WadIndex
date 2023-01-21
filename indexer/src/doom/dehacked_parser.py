import re
from dataclasses import dataclass
from enum import Enum
from io import StringIO
from typing import Dict, Optional


RE_SPLIT = re.compile(r'\s+')


class DehackedParserError(Exception):
    def __init__(self, message: str):
        super(Exception, self).__init__(message)


class ParseMode(Enum):
    NOTHING = 0
    THING = 1
    STATE = 2
    SOUND = 3
    WEAPON = 4
    AMMO = 5
    SPRITE = 6
    POINTER = 7
    STRING = 8
    MISC = 9
    CHEATS = 10
    PARS = 11
    STRINGS_EXT = 12
    POINTERS_EXT = 13


@dataclass
class DehackedThing:
    index: int
    spawn_id: int = -1
    name: Optional[str] = None


@dataclass
class DehackedState:
    index: int
    action: Optional[str] = None


@dataclass
class DehackedSound:
    index: int


@dataclass
class DehackedWeapon:
    index: int
    name: str = ''


@dataclass
class DehackedAmmo:
    index: int


@dataclass
class DehackedPar:
    episode: int
    map: int
    time: int


class DehackedParser:

    def __init__(self):
        self.things: Dict[int, DehackedThing] = {}
        self.states: Dict[int, DehackedState] = {}
        self.sounds: Dict[int, DehackedSound] = {}
        self.weapons: Dict[int, DehackedWeapon] = {}
        self.ammo: Dict[int, DehackedAmmo] = {}
        self.pars: Dict[str, DehackedPar] = {}

        self.strings: Dict[str, str] = {}
        self.cheats: Dict[str, str] = {}
        self.misc: Dict[str, str] = {}

    def parse(self, stream: StringIO):
        mode: ParseMode = ParseMode.NOTHING
        pointer_index: Optional[int] = None
        current_thing: Optional[DehackedThing] = None
        current_state: Optional[DehackedState] = None
        current_sound: Optional[DehackedSound] = None
        current_weapon: Optional[DehackedWeapon] = None
        current_ammo: Optional[DehackedAmmo] = None

        while True:
            line = stream.readline()
            if not line:
                break
            line = line[:-1].strip()

            # Skip comment lines and empty lines.
            if len(line) == 0 or line[0].startswith('#'):
                continue

            # Validate header line.
            if mode == ParseMode.NOTHING:
                if line == 'Patch File for DeHackEd v3.0':
                    continue

            line_normalized = line.upper()

            # Format version.
            if line_normalized.startswith('PATCH FORMAT = '):
                continue

            line_words = RE_SPLIT.split(line)

            # Entry headers.
            if line_normalized.startswith('THING ') and len(line_words) >= 3:
                mode = ParseMode.THING
                thing_index = int(line_words[1]) - 1
                current_thing = DehackedThing(thing_index)
                current_thing.name = ' '.join(line_words[2:])[1:-1]
                self.things[thing_index] = current_thing
                continue

            elif line_normalized.startswith('FRAME ') and len(line_words) >= 2 and '=' not in line:
                mode = ParseMode.STATE
                state_index = int(line_words[1])
                current_state = DehackedState(state_index)
                self.states[state_index] = current_state
                continue

            elif line_normalized.startswith('SOUND ') and len(line_words) >= 2:
                mode = ParseMode.SOUND
                sound_index = int(line_words[1])
                current_sound = DehackedSound(sound_index)
                self.sounds[sound_index] = current_sound
                continue

            elif line_normalized.startswith('WEAPON ') and len(line_words) >= 3:
                mode = ParseMode.WEAPON
                weapon_index = int(line_words[1])
                current_weapon = DehackedWeapon(weapon_index)
                current_weapon.name = ' '.join(line_words[2:])[1:-1]
                self.weapons[weapon_index] = current_weapon
                continue

            elif line_normalized.startswith('AMMO ') and len(line_words) >= 3 and line_words[2][0] == '(':
                mode = ParseMode.AMMO
                ammo_index = int(line_words[1])
                current_ammo = DehackedAmmo(ammo_index)
                current_ammo.name = ' '.join(line_words[2:])[1:-1]
                self.ammo[ammo_index] = current_ammo
                continue

            elif line_normalized.startswith('SPRITE ') and len(line_words) == 2:
                mode = ParseMode.SPRITE
                continue

            elif line_normalized.startswith('POINTER ') and len(line_words) >= 4:
                mode = ParseMode.POINTER
                pointer_index = int(line_words[3][:-1])
                continue

            elif line_normalized.startswith('CHEAT 0'):
                mode = ParseMode.CHEATS
                continue

            elif line_normalized.startswith('MISC 0'):
                mode = ParseMode.MISC
                continue

            elif line_normalized.startswith('[PARS]'):
                mode = ParseMode.PARS
                continue

            elif line_normalized.startswith('[CODEPTR]'):
                mode = ParseMode.POINTERS_EXT
                continue

            elif line_normalized.startswith('[STRINGS]'):
                mode = ParseMode.STRINGS_EXT
                continue

            # Text header.
            elif line_normalized.startswith('TEXT ') and len(line_words) == 3:
                mode = ParseMode.STRING

                entry_len1 = int(line_words[1])
                entry_len2 = int(line_words[2])

                original = stream.read(entry_len1)
                new = stream.read(entry_len2)
                self.strings[original] = new

                continue

            # Extended mode section contents.
            if mode == ParseMode.PARS:
                if line_words[0] == 'par':
                    if len(line_words) == 4:
                        par_episode = int(line_words[1])
                        par_map = int(line_words[2])
                        par_time = int(line_words[3])
                    elif len(line_words) == 3:
                        par_episode = 0
                        par_map = int(line_words[1])
                        par_time = int(line_words[2])
                    else:
                        continue

                    par = DehackedPar(par_episode, par_map, par_time)
                    if par.episode == 0:
                        lump_name = 'MAP{:02}'.format(par.map)
                    else:
                        lump_name = 'E{}M{}'.format(par.episode, par.map)
                    self.pars[lump_name] = par

                continue

            elif mode == ParseMode.STRINGS_EXT:
                pair = line.split(' = ')
                if len(pair) < 2:
                    continue

                key = pair[0]
                value = pair[1]

                # Read multiline strings.
                if line.endswith('\\'):

                    # Strip the trailing \
                    value = value[:-1]
                    while True:
                        line = stream.readline()
                        if line is None:
                            break

                        # Strip newline.
                        line = line[:-1]

                        # Lines that do not end with \ will terminate the string value.
                        # Lines that do are added without the \
                        if not line.endswith('\\'):
                            value += line.lstrip()
                            break
                        else:
                            value += line.lstrip()[:-1]

                self.strings[key] = self.string_unescape(value)
                continue

            elif mode == ParseMode.POINTERS_EXT:
                pair = line.split(' = ')
                if len(pair) < 2:
                    continue

                key = pair[0]
                value = pair[1]

                index_parts = RE_SPLIT.split(key)
                if len(index_parts) < 2:
                    continue
                index = int(index_parts[1])

                if index not in self.states:
                    continue
                self.states[index].action = value

                continue

            # Key\value pairs.
            pair = line.split(' = ', 1)
            if len(pair) != 2:
                continue
            key = pair[0]
            value = pair[1]

            if mode == ParseMode.THING and current_thing is not None:
                if key == 'ID #':
                    current_thing.spawn_id = int(value)

            elif mode == ParseMode.STATE and current_state is not None:
                pass
            elif mode == ParseMode.SOUND and current_sound is not None:
                pass
            elif mode == ParseMode.WEAPON and current_weapon is not None:
                pass
            elif mode == ParseMode.AMMO and current_ammo is not None:
                pass

            elif mode == ParseMode.POINTER and pointer_index is not None:
                if pointer_index not in self.states:
                    self.states[pointer_index] = DehackedState(pointer_index)
                self.states[pointer_index].action = value
            elif mode == ParseMode.CHEATS:
                self.cheats[key] = value
            elif mode == ParseMode.MISC:
                self.misc[key] = value

    @staticmethod
    def string_unescape(string: str):
        """
        Returns an escaped string for use in Dehacked patch reading.
        """

        string = string.replace('\\\\', '\\')
        string = string.replace('\\n', '\n')
        string = string.replace('\\r', '\r')
        string = string.replace('\\t', '\t')
        string = string.replace('\\"', '\"')

        return string
