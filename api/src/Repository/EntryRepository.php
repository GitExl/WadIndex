<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

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

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function getLatestTeasers(int $count=10): array {
    $stmt = $this->connection->prepare("
      SELECT
        e.id AS `id`,
        e.path AS `path`,
        e.collection AS `collection`,
        e.title AS `title`,
        e.file_modified AS `timestamp`,
        e.game AS `game`,
        e.description AS `description`,
        (SELECT COUNT(*) FROM entry_levels WHERE entry_id = e.id) AS `level_count`
      FROM entry e
      ORDER BY e.file_modified DESC
      LIMIT $count
    ");
    $entries = $stmt->executeQuery()->fetchAllAssociative();

    foreach ($entries as &$entry) {
      $entry['game'] = self::GAME_KEY[$entry['game']];
    }
    unset($entry);

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

  public function list(string $collection, ?string $path=NULL): ?array {
    if ($path) {
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
        'collection' => $collection,
        'path' => $path,
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
    $stmt = $this->connection->prepare('
      SELECT
        e.id AS `id`,
        e.path AS `path`,
        e.collection AS `collection`,
        e.title AS `title`,
        e.file_modified AS `timestamp`,
        e.game AS `game`,
        e.description AS `description`,
        (SELECT COUNT(*) FROM entry_levels WHERE entry_id = e.id) AS `level_count`
      FROM entry e
      WHERE
        e.collection = :collection AND
        e.directory_id = :directory_id
      ORDER BY e.path ASC
    ');
    $entries = $stmt->executeQuery([
      'collection' => $collection,
      'directory_id' => $directory_id,
    ])->fetchAllAssociative();

    foreach ($entries as &$entry) {
      $entry['game'] = self::GAME_KEY[$entry['game']];
    }
    unset($entry);

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
      'entries' => $entries,
    ];
  }

  public function getForMusic(int $music_id): array {
    $stmt = $this->connection->prepare('
      SELECT
          em.entry_id AS `id`,
          em.name AS `name`,
          e.collection AS `collection`,
          e.path AS `path`,
          e.title AS `title`
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
          ea.entry_id AS `id`,
          e.collection AS `collection`,
          e.path AS `path`,
          e.title AS `title`
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

}
