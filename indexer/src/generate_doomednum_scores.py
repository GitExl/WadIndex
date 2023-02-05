import json

from typing import Dict, Set, List
from indexer.engine import Engine
from utils.config import Config

engine_factors: Dict[Engine, float] = {
    Engine.DOOM: 1.5,
    Engine.HERETIC: 1.5,
    Engine.HEXEN: 1.5,
    Engine.STRIFE: 1.5,
    Engine.BOOM: 1.0,
    Engine.MBF: 1.0,
    Engine.ZDOOM: 1.0,
    Engine.GZDOOM: 1.0,
    Engine.LEGACY: 1.0,
    Engine.SKULLTAG: 1.0,
    Engine.ZDAEMON: 1.0,
    Engine.DOOMSDAY: 1.0,
    Engine.EDGE: 1.0,
    Engine.ETERNITY: 1.0,
    Engine.DOOMRETRO: 1.0,
    Engine.ZANDRONUM: 1.0,
}

config = Config()

with open(config.get('extractors.engine.doomednum_table'), 'r') as f:
    engine_data = json.load(f)

# Create sets of doomednums for each engine.
engine_doomednums: Dict[str, Set[int]] = {}
for engine_key, doomednums in engine_data.items():
    clean_doomednums: List[int] = []
    for doomednum in doomednums:
        if isinstance(doomednum, int):
            clean_doomednums.append(doomednum)
        elif isinstance(doomednum, str):
            a, b = doomednum.split('-')
            a = int(a)
            b = int(b)
            for num in range(a, b + 1):
                clean_doomednums.append(num)

    engine_doomednums[engine_key] = set(clean_doomednums)

# List which engines each doomednum appears in.
doomednum_engines: Dict[int, Set[str]] = {}
for engine_key, doomednums in engine_doomednums.items():
    engine = Engine[engine_key]
    engine_factor = engine_factors.get(engine, 1.0)

    for doomednum in doomednums:
        if doomednum not in doomednum_engines:
            doomednum_engines[doomednum] = set()
        doomednum_engines[doomednum].add(engine_key)

# Calculate score for each engine in each doomednum.
doomednum_scores: Dict[int, Dict[str, float]] = {}
for doomednum, engine_keys in doomednum_engines.items():
    if len(engine_keys) == len(engine_factors):
        continue

    average = 1 / len(engine_keys)
    presence_scores: Dict[str, float] = {}
    for engine_key in engine_keys:
        engine = Engine[engine_key]
        presence_scores[engine_key] = average * engine_factors[engine]

    doomednum_scores[doomednum] = presence_scores

with open(config.get('extractors.engine.doomednum_scores'), 'w') as f:
    json.dump(doomednum_scores, f, indent=4)
