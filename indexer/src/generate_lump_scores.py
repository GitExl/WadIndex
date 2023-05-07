import json

from typing import Dict, Set

from archives.wadarchive import WADArchive
from indexer.game import Game
from utils.config import Config
from utils.logger import Logger

iwads: Dict[Game, str] = {
    Game.DOOM2: 'DOOM2.WAD',
    Game.DOOM: 'DOOM.WAD',
    Game.HERETIC: 'HERETIC.WAD',
    Game.HEXEN: 'HEXEN.WAD',
    Game.TNT: 'TNT.WAD',
    Game.PLUTONIA: 'PLUTONIA.WAD',
    Game.STRIFE: 'STRIFE0.WAD',
    Game.HACX: 'HACX.WAD',
    Game.DOOM64: 'DOOM64.WAD',
}

iwad_factors: Dict[Game, float] = {
    Game.DOOM2: 1.05,
    Game.DOOM: 1.0,
    Game.HERETIC: 1.0,
    Game.HEXEN: 1.0,
    Game.TNT: 0.75,
    Game.PLUTONIA: 0.75,
    Game.STRIFE: 1.0,
    Game.HACX: 0.5,
    Game.DOOM64: 0.5,
}

ignore = {
    'THINGS', 'LINEDEFS', 'SIDEDEFS', 'VERTEXES', 'SEGS', 'SSECTORS', 'NODES', 'SECTORS', 'REJECT', 'BLOCKMAP',
    'SS_START', 'S_START', 'SS_END', 'S_END',
    'FF_START', 'F_START', 'FF_END', 'F_END',
    'PP_START', 'P_START', 'PP_END', 'P_END',
    'PLAYPAL', 'COLORMAP',

    # These are Hexen, but also ZDoom so not indicative
    'MAPINFO', 'SNDINFO', 'BEHAVIOR',
}

config = Config()
logger = Logger(config.get('paths.logs'))

lump_list: Dict[str, Set[Game]] = {}
for game, iwad_file in iwads.items():
    iwad_path = '{}/{}'.format(config.get('paths.iwads'), iwad_file)
    iwad_path = str(iwad_path).replace('\\', '/')

    with open(iwad_path, 'rb') as f:
        archive = WADArchive(iwad_path, f, logger)

    for file in archive.files:
        if file.name in ignore:
            continue

        if file.name in lump_list:
            lump_list[file.name].add(game)
        else:
            lump_list[file.name] = {game}

lump_scores: Dict[str, Dict[str, float]] = {}
for lump_name, lump_presence in lump_list.items():

    # Skip lumps that are present in every IWAD.
    if len(lump_presence) == len(iwads):
        continue

    # Score by how many IWADs a lump appears in and the factor per IWAD.
    average = 1 / len(lump_presence)
    presence_scores: Dict[str, float] = {}
    for game in lump_presence:
        presence_scores[game.name] = average * iwad_factors[game]

    lump_scores[lump_name] = presence_scores

with open(config.get('extractors.game.lump_score_table'), 'w') as f:
    json.dump(lump_scores, f, indent=4)
