from enum import Enum

from indexer.engine import Engine
from indexer.game import Game


class TextKeyStore(Enum):
    STORE = 0
    BINARY_OR = 1


class TextKeyTransform(Enum):
    TEXT = 0
    BOOL = 1
    DIFFICULTY = 2
    ENGINE = 3
    GAME = 4


class TextKeyType(Enum):
    SINGLE = 0
    ARRAY = 1
    SET = 2


class TextKeyProcess(Enum):
    TEXT_TO_MARKDOWN = 0


TEXT_KEYS = {
    'authors': {
        'type': TextKeyType.SET,
        'keys': {'author', 'authors', 'author(s)', 'autor', 'original author'},
    },
    'title': {
        'keys': {'title', 'level name', 'name'},
    },
    'game_style_singleplayer': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'single player', 'singleplayer'},
    },
    'based_on': {
        'keys': {'base', 'idea base'},
    },
    'description': {
        'type': TextKeyType.ARRAY,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {'description', 'instructions', 'play information', 'wad description', 'log entry'},
    },
    'difficulty_levels': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.DIFFICULTY,
        'keys': {'difficulty settings', 'difficulty'},
    },
    'game_style_cooperative': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'cooperative 2-4 player', 'cooperative', 'cooperative 2-8 player', 'co-op', 'coop 2-4 player', 'coop'},
    },
    'game_style_deathmatch': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'deathmatch 2-4 player', 'deathmatch', 'deathmatch 2-8 player'},
    },
    'tools_used': {
        'type': TextKeyType.SET,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {
            'editor(s) used', 'editors used', 'editor used', 'tools used', 'editors', 'utilities used', 'editor',
            'main editor(s) used', 'tools(s) used',
        },
    },
    'known_bugs': {
        'keys': {'known bugs', 'bugs', 'unknown bugs'},
    },
    'copyright': {
        'type': TextKeyType.ARRAY,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {'copyright / permissions'},
    },
    'filename': {
        'keys': {'filename'},
    },
    'credits': {
        'type': TextKeyType.ARRAY,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {
            'additional credits to', 'additional credits', 'credits', 'credits to', 'special thanks to', 'thanks to',
            'big thanks to', 'special thanks', 'additional credit to',
        },
    },
    'build_time': {
        'keys': {'build time', 'time taken', 'construction time', 'time', 'building time'},
    },
    'author_info': {
        'keys': {'misc. author info', 'misc author info', 'author info', 'misc. developer info'},
    },
    'other': {
        'keys': {'other'},
    },
    'game': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.GAME,
        'keys': {'game', 'required game', 'game version required', 'iwad needed', 'doom version', 'game and version used'},
    },
    'content_graphics': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {
            'new graphics', 'graphics', 'graphic addon only', 'sprites', 'textures', 'sprite edit', 'new sprites',
            'new textures',
        },
    },
    'content_sounds': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'new sounds', 'sounds', 'sound pwad only'},
    },
    'music': {
        'keys': {'music', 'music track'},
    },
    'content_demos': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'demos replaced', 'demos', '.lmp only', 'new demos'},
    },
    'content_music': {
        'store': TextKeyStore.BINARY_OR,
        'keys': {'new music', 'music pwad only', 'midi', 'new musics'},
    },
    'date_released': {
        'keys': {'release date', 'date', 'date released', 'date of release'},
    },
    'content_dehacked': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'dehacked/bex patch', 'dehack patch only'},
    },
    'game_style_primary': {
        'keys': {'primary purpose'},
    },
    'game_style_other': {
        'keys': {'other game styles'},
    },
    'other_files_required': {
        'keys': {'other files required', 'required to have in dir'},
    },
    'author_other_files': {
        'keys': {'other files by author'},
    },
    'engine': {
        'transform': TextKeyTransform.ENGINE,
        'keys': {'advanced engine needed', 'source port', 'engine', 'port'},
    },
    'links': {
        'keys': {
            'the usual', 'ftp sites', 'web sites', 'bbs numbers', 'homepage', 'web page', 'ftp', 'website',
            'web site', 'home page', 'www', 'bbs', 'internet', 'web', 'www sites'
        },
    },
    'do_not_run_with': {
        'type': TextKeyType.ARRAY,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {'may not run with...', 'may not run with', 'will not run with...'},
    },
    'archive_maintainer': {
        'keys': {'archive maintainer'},
    },
    'tested_with': {
        'keys': {'tested with'},
    },
    'update_to': {
        'keys': {'update to'},
    },
    'where_to_get': {
        'keys': {'where to get this wad'},
    },
    'date_completed': {
        'keys': {'date finished', 'date completed', 'completion date'},
    },
    'content_levels': {
        'store': TextKeyStore.BINARY_OR,
        'transform': TextKeyTransform.BOOL,
        'keys': {'new level wad', 'new levels', 'levels', 'levels replaced', 'new levels'},
    },
    'review': {
        'keys': {'review'},
    },
    'story': {
        'type': TextKeyType.ARRAY,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {'story', 'the story', 'story line', 'the story so far'},
    },
    'theme': {
        'keys': {'theme', 'themes'},
    },
    'inspiration': {
        'keys': {'inspiration'},
    },
    'comments': {
        'type': TextKeyType.ARRAY,
        'process': TextKeyProcess.TEXT_TO_MARKDOWN,
        'keys': {
            'comments', 'author\'s comment', 'info', 'author\'s comments', 'note', 'notes', 'additional notes',
            'uploader\'s note', 'important notes', 'play notes', 'misc. info', 'things to look out for',
            'additional info', 'comment', 'misc game info', 'misc notes', 'author comments', 'authors comments',
            'important',
        },
    },
    'hints': {
        'keys': {'hints', 'tips', 'hint'},
    },
    'content_decorate': {
        'keys': {'decorate'},
    },
    'content_weapons': {
        'keys': {'weapons', 'new weapons'},
    },
}

TEXT_GAMES = {
    Game.DOOM2: {
        'keys': {
            'doom 2', 'doom2', 'doom ii', 'doomii', 'doom 2 ver 1.9', 'doom ][', 'doom / doom2', 'doom/doom2',
            'any doom', '- doom2', '2', 'any', 'both', 'freedoom',' freedm', 'ii', 'any iwad', 'freedoom: phase 2',
        },
        're': ['any doom.*', '^doom 2.*', '.*doom2.*', r'.*doom2\.wad.*', '.*doom ii.*', r'\bdoom\b', '^any game'],
    },
    Game.DOOM: {
        'keys': {'doom', 'doom1', '(ultimate) doom', 'the ultimate doom', 'freedoom1'},
        're': ['^doom.*', '.* ultimate .*', r'doom\.wad', '.*ultimate doom.*', '.*doom i.*'],
    },
    Game.PLUTONIA: {
        'keys': {'final doom', 'the plutonia experiment'},
        're': ['^final doom.*', '^plutonia.*'],
    },
    Game.TNT: {
        're': ['^tnt.*'],
    },
    Game.HERETIC: {
        're': ['.*heretic.*'],
    },
    Game.HEXEN: {
        're': ['.*hexen.*'],
    },
    Game.STRIFE: {
        're': ['.*strife.*'],
    },
    Game.CHEX: {
        'keys': {'chex', 'chex quest', 'chex quest 3'},
    },
    Game.HACX: {
        're': ['^hacx.*'],
    }
}

TEXT_DIFFICULTY = {
    'true': {
        'keys': {'yes', 'y', 'supported', 'possibly', 'of course', 'any', 'all', 'full implementation', 'fully functional.', 'fully supported', 'some'},
        're': ['^yes', '^yup', '^yep', '^yeah', r'^skills\s', r'^skill\s', '^only', '^implemented', r'^all\b', '^definitely', '^fully implemented', r'^some\b']
    },
    'false': {
        'keys': {'not implented', 'no', 'not implimented', '-', 'n\\a', 'unknown', 'n', 'not really', 'na', 'not applicable'},
        're': ['^not implemented', '^nope', '^none', r'^no\b', '^nah', '^n/a', r'^not\b']
    },
}

TEXT_BOOLEAN = {
    'true': {
        'keys': {'designed for', 'all', 'any', 'yeah!', 'yeah', 'affirmative', 'certainly', 'some', 'y', '- yes',
                 'one'},
        're': ['^yea.*', '^oh yeah.*', '^oh yes.*', '^supported.*', '^starts.*', '^yes.*', '^sure.*', '^probably.*',
               '^absolutely.*', '^definitely.*', '^some .*', '^duh.*', '^hell (yes|yeah).*', '^i guess.*',
               '^implemented.*', '^of course.*', '^yep.*', '^yup.*', '^a .*', '^all .*', '^designed.*', '^fully .*',
               '^full .*', '^you bet.*', r'.*\(yes\).*', '^aye.*'],
    },
    'false': {
        'keys': {'n/a', '-', '- no', '0', 'nah'},
        're': ['^no.*'],
    },
}

TEXT_ENGINE = {
    Engine.ZDOOM: {
        're': [r'zdoom'],
    },
    Engine.DOOM: {
        'keys': {
            'none', 'no', 'none.', 'doom2', 'vanilla', '-', 'doom 2', 'nope', 'any', 'n/a', 'vanilla compatible',
            'doom2.exe', 'vanilla-compatible', 'vanilla doom', 'none required',
        },
    },
    Engine.BOOM: {
        're': [r'boom', 'prboom+', 'prboom-plus -complevel 2'],
    },
    Engine.GZDOOM: {
        're': [r'gzdoom'],
    },
    Engine.SKULLTAG: {
        'keys': {'skulltag'},
    },
    Engine.NOLIMITS: {
        'keys': {'limit removing', 'limit-removing', 'limit removing port', 'yes', 'limit-removing port'},
    },
    Engine.MBF: {
        'keys': {'mbf', 'marine\'s best friend'},
    },
    Engine.LEGACY: {
        'keys': {'legacy', 'doom legacy'},
    },
    Engine.ZANDRONUM: {
        'keys': {'zandronum'},
    },
    Engine.ZDAEMON: {
        'keys': {'zdaemon'},
    },
    Engine.ETERNITY: {
        'keys': {'eternity'},
    },
    Engine.ODAMEX: {
        'keys': {'odamex'}
    }
}
