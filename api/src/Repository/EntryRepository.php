<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;
use InvalidArgumentException;

class EntryRepository {

  private const GAME_KEY = [
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

  private const ENGINE_KEY = [
    0 => NULL,
    1 => 'doom',
    2 => 'heretic',
    3 => 'hexen',
    4 => 'strife',
    5 => 'no_limits',
    6 => 'boom',
    7 => 'mbf',
    8 => 'zdoom',
    9 => 'gzdoom',
    10 => 'doom_legacy',
    11 => 'skulltag',
    12 => 'zdaemon',
    13 => 'doomsday',
    14 => 'edge',
    15 => 'eternity',
    16 => 'doom_retro',
    17 => 'zandronum',
  ];

  private const FIELDS_TEASER = '
    e.id,
    e.path AS `path`,
    e.collection AS `collection`,
    e.title AS `title`,
    e.file_modified AS `timestamp`,
    e.is_singleplayer AS `is_singleplayer`,
    e.is_cooperative AS `is_cooperative`,
    e.is_deathmatch AS `is_deathmatch`,
    e.description AS `description`,
    (SELECT COUNT(*) FROM maps WHERE entry_id = e.id) AS `map_count`
  ';

  private const FIELDS_MINIMAL = '
    e.entry_id AS `id`,
    e.collection AS `collection`,
    e.path AS `path`,
    e.title AS `title`
  ';

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function getLatestTeasers(int $count=15): array {
    $stmt = $this->connection->prepare("
      SELECT
        " . self::FIELDS_TEASER . "
      FROM entry e
      ORDER BY e.entry_created DESC, e.file_modified DESC
      LIMIT $count
    ");
    $entries = $stmt->executeQuery()->fetchAllAssociative();

    return $entries;
  }

  public function getUpdatedTeasers(int $count=15): array {
    $stmt = $this->connection->prepare("
      SELECT
        " . self::FIELDS_TEASER . "
      FROM entry e
      ORDER BY e.file_modified DESC
      LIMIT $count
    ");
    $entries = $stmt->executeQuery()->fetchAllAssociative();

    return $entries;
  }

  public function get(string $collection, string $path): ?array {
    $stmt = $this->connection->prepare("
      SELECT
        e.id AS `id`,
        e.path AS `path`,
        e.collection AS `collection`,
        e.title AS `title`,
        e.file_size AS `size`,
        e.file_modified AS `timestamp`,
        e.game AS `game`,
        e.engine AS `engine`,
        e.is_singleplayer AS `is_singleplayer`,
        e.is_cooperative AS `is_cooperative`,
        e.is_deathmatch AS `is_deathmatch`,
        e.description AS `description`,
        e.tools_used AS `tools_used`,
        e.build_time AS `build_time`,
        e.credits AS `credits`,
        e.known_bugs AS `known_bugs`,
        e.comments AS `comments`
      FROM entry e
      WHERE
        collection=:collection AND
        path=:path
      LIMIT 1
    ");
    $entry = $stmt->executeQuery([
      'collection' => $collection,
      'path' => $path,
    ])->fetchAssociative();

    if (empty($entry)) {
      return NULL;
    }

    $entry['game'] = self::GAME_KEY[$entry['game']];
    $entry['engine'] = self::ENGINE_KEY[$entry['engine']];

    return $entry;
  }

  public function list(ListParameters $params): ?array {
    if ($params->sortField === 'title') {
      $sort_field = 'e.title';
    }
    elseif ($params->sortField === 'date') {
      $sort_field = 'e.file_modified';
    }
    else {
      throw new InvalidArgumentException();
    }

    if ($params->sortOrder === 'asc') {
      $sort_order = 'ASC';
    }
    elseif ($params->sortOrder === 'desc') {
      $sort_order = 'DESC';
    }
    else {
      throw new InvalidArgumentException();
    }

    if ($params->path) {
      $stmt = $this->connection->prepare('
        SELECT
          d.id AS `id`
        FROM directories d
        WHERE
          d.collection = :collection AND
          d.path = :path
        LIMIT 1
      ');
      $directory_id = $stmt->executeQuery([
        'collection' => $params->collection,
        'path' => $params->path,
      ])->fetchFirstColumn();
      if ($directory_id == NULL) {
        return NULL;
      }

      $directory_id = $directory_id[0];
    }
    else {
      $directory_id = NULL;
    }

    // Get entries.
    $stmt = $this->connection->prepare("
      SELECT
        " . self::FIELDS_TEASER . "
      FROM entry e
      WHERE
        e.collection = :collection AND
        e.directory_id = :directory_id
      ORDER BY $sort_field $sort_order
      LIMIT $params->limit OFFSET $params->offset
    ");
    $entries = $stmt->executeQuery([
      'collection' => $params->collection,
      'directory_id' => $directory_id,
    ])->fetchAllAssociative();

    // Get total entry count.
    $stmt = $this->connection->prepare('
      SELECT
        COUNT(*)
      FROM entry e
      WHERE
        e.collection = :collection AND
        e.directory_id = :directory_id
    ');
    $entries_count = $stmt->executeQuery([
      'collection' => $params->collection,
      'directory_id' => $directory_id,
    ])->fetchFirstColumn()[0];


    // Get subdirectories.
    if ($directory_id) {
      $stmt = $this->connection->prepare('
        SELECT
          d.name AS `name`,
          d.path AS `path`
        FROM directories d
        WHERE
          d.parent_id = :parent_id
        ORDER BY d.name ASC
      ');
      $directories = $stmt->executeQuery([
        'parent_id' => $directory_id,
      ])->fetchAllAssociative();
    }
    else {
      $stmt = $this->connection->prepare('
        SELECT
          d.name AS `name`,
          d.path AS `path`
        FROM directories d
        WHERE
          d.parent_id IS NULL
        ORDER BY d.name ASC
      ');
      $directories = $stmt->executeQuery()->fetchAllAssociative();
    }

    return [
      'directories' => $directories,
      'entries_total' => $entries_count,
      'entries' => $entries,
    ];
  }

  public function getForMusic(int $music_id): array {
    $stmt = $this->connection->prepare('
      SELECT
        em.name AS `name`,
        ' . self::FIELDS_MINIMAL . '
      FROM
        entry_music em
      LEFT JOIN entry e ON e.id = em.entry_id
      WHERE
        em.music_id = :music_id
      ORDER BY e.file_modified ASC
    ');
    $entries = $stmt->executeQuery([
      'music_id' => $music_id,
    ])->fetchAllAssociative();

    return $entries;
  }

  public function getForAuthor(int $author_id): array {
    $stmt = $this->connection->prepare('
      SELECT
        ' . self::FIELDS_MINIMAL . '
      FROM
        entry_authors ea
      LEFT JOIN entry e ON e.id = ea.entry_id
      WHERE
        ea.author_id = :author_id
      ORDER BY e.file_modified ASC
    ');
    $entries = $stmt->executeQuery([
      'author_id' => $author_id,
    ])->fetchAllAssociative();

    return $entries;
  }

  public function search(SearchParameters $params): array {

    // Validate some input.
    if (empty($params->searchFields)) {
      $params->searchFields = ['title', 'filename'];
    }

    if ($params->sortField === 'relevance') {
      $sort_field = 'score';
    }
    elseif ($params->sortField === 'title') {
      $sort_field = 'title';
    }
    elseif ($params->sortField === 'date') {
      $sort_field = 'date';
    }

    if ($params->sortOrder === 'asc') {
      $sort_order = 'ASC';
    }
    elseif ($params->sortOrder === 'desc') {
      $sort_order = 'DESC';
    }

    // Build fulltext search statements for each column and table.
    $joins = [];
    $matches = [];
    foreach ($params->searchFields as $field) {
      if ($field == 'title') {
        $matches[] = 'MATCH(e.`title`) AGAINST(:search_key)';
      }
      elseif ($field == 'filename') {
        $matches[] = 'MATCH(e.`path`) AGAINST(:search_key)';
      }
      elseif ($field == 'description') {
        $matches[] = 'MATCH(e.`description`) AGAINST(:search_key)';
      }
      elseif ($field == 'textfile') {
        $matches[] = 'MATCH(et.`text`) AGAINST(:search_key)';
        $joins[] = 'LEFT JOIN entry_textfile et ON et.entry_id = e.id';
      }
    }

    $query = $this->buildSearchQuery(self::FIELDS_TEASER, $matches, $joins, $params->filterGame, $params->filterGameplay, $sort_field, $sort_order, $params->limit, $params->offset);
    $stmt = $this->connection->prepare($query);
    $stmt->bindValue('collection', $params->collection);
    $stmt->bindValue('search_key', $params->searchKey);
    $entries = $stmt->executeQuery()->fetchAllAssociative();

    $count_query = $this->buildSearchQuery('COUNT(*)', $matches, $joins, $params->filterGame, $params->filterGameplay);
    $stmt = $this->connection->prepare($count_query);
    $stmt->bindValue('collection', $params->collection);
    $stmt->bindValue('search_key', $params->searchKey);
    $entries_total = $stmt->executeQuery()->fetchFirstColumn()[0];

    return [
      'entries_total' => $entries_total,
      'entries' => $entries,
    ];
  }

  private function buildSearchQuery(
    string $fields,
    array $matches,
    array $joins,
    array $games,
    array $gameplay_types,
    ?string $sort_field=NULL,
    ?string $sort_order=NULL,
    ?int $limit=NULL,
    ?int $offset=NULL
  ): string {

    $query = [];

    // Select fields.
    $query[] = 'SELECT ' . $fields;

    if ($sort_field === 'score') {
      $query[] = ', (' . implode(' + ', $matches) . ') AS score';
    }
    $query[] = 'FROM entry e';

    // Join with other tables.
    if (!empty($joins)) {
      $query[] = implode(' ', $joins);
    }

    // Search query.
    $query[] = 'WHERE (' . implode(' OR ', $matches) . ')';

    // Filter by collection.
    $query[] = 'AND e.collection = :collection';

    // Filter by game.
    $game_ids = array_map(function ($game_str) {
      return array_search($game_str, self::GAME_KEY);
    }, $games);
    $game_ids = implode(', ', $game_ids);
    if (!empty($game_ids)) {
      $query[] = "AND e.game IN ($game_ids)";
    }

    // Filter by gameplay options.
    if (!empty($gameplay_types)) {
      $gameplay_cases = [];
      foreach ($gameplay_types as $gameplay_type) {
        $gameplay_cases[] = 'e.is_' . $gameplay_type . ' = 1';
      }
      $query[] = 'AND (' . implode(' OR ', $gameplay_cases) . ')';
    }

    // Sorting.
    if ($sort_field) {
      $query[] = "ORDER BY $sort_field";
      if ($sort_order) {
        $query[] = $sort_order;
      }
    }

    // Paging.
    if ($limit) {
      $query[] = "LIMIT $limit";
    }
    if ($offset) {
      $query[] = "OFFSET $offset";
    }

    return implode(' ', $query);
  }

}
