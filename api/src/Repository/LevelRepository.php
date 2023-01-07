<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;

class LevelRepository {

  private const LEVEL_FORMAT_KEY = [
    'doom',
    'hexen',
    'udmf',
  ];

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function getAllTeasersForEntry(int $entry_id): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        e.path AS `path`,
        e.collection AS `collection`,
        el.name AS `name`,
        el.title AS `title`,
        el.music AS `music_name`,
        el.format AS `format`
      FROM
        entry_levels el
      LEFT JOIN entry e ON e.id = el.entry_id
      WHERE
        el.entry_id = :entry_id
      ORDER BY name ASC
    ');

    $levels = $stmt->executeQuery([
      'entry_id' => $entry_id,
    ])->fetchAllAssociative();

    if (empty($levels)) {
      return NULL;
    }

    foreach ($levels as &$level) {
      $level['format'] = self::LEVEL_FORMAT_KEY[$level['format']];
    }
    unset($level);

    return $levels;
  }

  public function getTeaser(string $collection, string $path, string $name): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        e.collection AS `collection`,
        e.path AS `path`,
        el.name AS `name`,
        el.title AS `title`,
        el.music AS `music_name`,
        el.format AS `format`
      FROM entry e
      LEFT JOIN entry_levels el ON el.entry_id = e.id
      WHERE
        e.collection=:collection AND
        e.path=:entry_path AND
        el.name=:name
      LIMIT 1
    ');

    $level = $stmt->executeQuery([
      'collection' => $collection,
      'entry_path' => $path,
      'name' => $name,
    ])->fetchAssociative();

    if (empty($level)) {
      return NULL;
    }

    $level['format'] = self::LEVEL_FORMAT_KEY[$level['format']];

    return $level;
  }

  public function get(string $collection, string $path, string $name): ?array {
    $stmt = $this->connection->prepare("
      SELECT
        e.id AS `entry_id`,
        e.collection AS `collection`,
        e.path AS `path`,
        el.name AS `name`,
        el.title AS `title`,
        el.par_time AS `par_time`,
        el.music AS `music`,
        el.next AS `next`,
        el.next_secret AS `next_secret`,
        el.cluster AS `cluster`,
        el.format AS `format`,
        el.allow_jump AS `allow_jump`,
        el.allow_crouch AS `allow_crouch`,
        el.line_count AS `line_count`,
        el.side_count AS `side_count`,
        el.sector_count AS `sector_count`,
        el.thing_count AS `thing_count`
      FROM entry e
      LEFT JOIN entry_levels el ON el.entry_id = e.id
      WHERE
        e.collection=:collection AND
        e.path=:entry_path AND
        el.name=:name
      LIMIT 1
    ");
    $level = $stmt->executeQuery([
      'collection' => $collection,
      'entry_path' => $path,
      'name' => $name,
    ])->fetchAssociative();

    if (empty($level)) {
      return NULL;
    }

    $level['format'] = self::LEVEL_FORMAT_KEY[$level['format']];
    $level['allow_jump'] = $level['allow_jump'] !== NULL ? (bool) $level['allow_jump'] : NULL;
    $level['allow_crouch'] = $level['allow_crouch'] !== NULL ? (bool) $level['allow_crouch'] : NULL;

    if ($level['next']) {
      $level['next'] = $this->getTeaser($collection, $path, $level['next']);
    }
    if ($level['next_secret']) {
      $level['next_secret'] = $this->getTeaser($collection, $path, $level['next_secret']);
    }

    return $level;
  }

}
