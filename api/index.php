<?php

error_reporting(E_ALL);

$db = new mysqli('db', getenv('MARIADB_USER'), getenv('MARIADB_PASSWORD'), getenv('MARIADB_DATABASE'), 3306);

$action = $_GET['action'];

const GAME_TO_STRING = [
  0 => NULL,
  1 => 'doom',
  2 => 'doom2',
  3 => 'tnt',
  4 => 'plutonia',
  5 => 'heretic',
  6 => 'hexen',
  7 => 'strife',
  8 => 'chex_quest',
  9 => 'hacx',
];

const ENGINE_TO_STRING = [
  0 => NULL,
  1 => 'Doom',
  2 => 'Heretic',
  3 => 'Hexen',
  4 => 'Strige',
  5 => 'No limits',
  6 => 'Boom',
  7 => 'Marine\'s Best Friend',
  8 => 'ZDoom',
  9 => 'GZDoom',
  10 => 'Doom Legacy',
  11 => 'Skulltag',
  12 => 'ZDaemon',
  13 => 'Doomsday',
  14 => 'EDGE',
  15 => 'Eternity',
  16 => 'Doom Retro',
  17 => 'Zandronum',
];

const LEVEL_FORMAT_TO_STRING = [
  0 => 'doom',
  1 => 'hexen',
  2 => 'udmf',
];

header('Access-Control-Allow-Origin: *');

if ($action === 'entry_view') {
  $collection = $_GET['collection'];
  $path = $_GET['path'];

  $st = $db->prepare('SELECT e.id, e.title, e.collection, e.path, e.file_modified, e.game, e.description FROM entry e WHERE collection=? AND path=? LIMIT 1');
  $st->bind_param('ss', $collection, $path);
  $st->execute();
  $result = $st->get_result();
  $entry = $result->fetch_assoc();
  $st->close();

  if (empty($entry)) {
    http_response_code(404);
    exit();
  }

  $st = $db->prepare('SELECT name FROM author WHERE id IN (SELECT author_id FROM entry_authors WHERE entry_id = ?)');
  $st->bind_param('i', $entry['id']);
  $st->execute();
  $result = $st->get_result();
  $authors = $result->fetch_all();
  $st->close();

  $st = $db->prepare('SELECT name, title, par_time, music, next, next_secret, cluster, format, allow_jump, allow_crouch, line_count, thing_count, sector_count, side_count FROM entry_levels WHERE entry_id = ?');
  $st->bind_param('i', $entry['id']);
  $st->execute();
  $result = $st->get_result();
  $levels = $result->fetch_all(MYSQLI_ASSOC);
  $st->close();

  $st = $db->prepare('SELECT em.name, m.type, m.hash FROM entry_music em JOIN music m ON m.id = em.music_id WHERE em.entry_id = ?');
  $st->bind_param('i', $entry['id']);
  $st->execute();
  $result = $st->get_result();
  $music = $result->fetch_all(MYSQLI_ASSOC);
  $st->close();

  $data = [
    'title' => $entry['title'] ?? $entry['path'],
    'collection' => $entry['collection'],
    'path' => $entry['path'],
    'timestamp' => $entry['file_modified'],
    'game' => GAME_TO_STRING[$entry['game']],
    'engine' => ENGINE_TO_STRING[$entry['engine']],
    'description' => $entry['description'],

    'authors' => array_map(static function($author) {
      return $author[0];
    }, $authors),

    'levels' => array_map(static function($level) {
      return [
        'name' => $level['name'],
        'title' => $level['title'],
        'par_time' => $level['par_time'],
        'music' => $level['music'],
        'next' => $level['next'],
        'next_secret' => $level['next_secret'],
        'cluster' => $level['cluster'],
        'format' => LEVEL_FORMAT_TO_STRING[$level['format']],
        'allow_jump' => $level['allow_jump'],
        'allow_crouch' => $level['allow_crouch'],
        'stats' => [
          'things' => $level['thing_count'],
          'lines' => $level['line_count'],
          'sectors' => $level['sector_count'],
          'sides' => $level['side_count'],
        ],
      ];
    }, $levels),

    'music' => array_map(static function($music) {
      return [
        'name' => $music['name'],
        'type' => $music['type'],
        'url' => 'music/' . bin2hex($music['hash']) . '.' . $music['type'] . '.gz',
      ];
    }, $music),
  ];

  header('Content-Type: application/json; charset=utf-8');
  print(json_encode($data));

}

elseif ($action === 'entry_search') {
  $collection = $_GET['collection'];
  $key = $_GET['key'];

  $st = $db->prepare('SELECT e.id, e.title, e.collection, e.path, e.file_modified, e.game, e.engine, e.description FROM entry e WHERE collection=? AND MATCH(e.title, e.path) AGAINST (?) LIMIT 20');
  $st->bind_param('ss', $collection, $key);
  $st->execute();
  $result = $st->get_result();
  $entries = $result->fetch_all(MYSQLI_ASSOC);
  $st->close();

  $data = [];
  foreach ($entries as $entry) {
    $st = $db->prepare('SELECT name FROM author WHERE id IN (SELECT author_id FROM entry_authors WHERE entry_id = ?)');
    $st->bind_param('i', $entry['id']);
    $st->execute();
    $result = $st->get_result();
    $authors = $result->fetch_all();
    $st->close();

    $data[] = [
      'title' => $entry['title'] ?? $entry['path'],
      'authors' => array_map(static function($author) {
        return $author[0];
      }, $authors),
      'collection' => $entry['collection'],
      'path' => $entry['path'],
      'timestamp' => $entry['file_modified'],
      'game' => GAME_TO_STRING[$entry['game']],
      'engine' => ENGINE_TO_STRING[$entry['engine']],
      'description' => $entry['description'],
    ];
  }

  header('Content-Type: application/json; charset=utf-8');
  print(json_encode($data));

}

else {
  http_response_code(404);
  exit();

}
