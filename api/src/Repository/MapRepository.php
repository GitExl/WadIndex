<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;

class MapRepository {

  private const MAP_FORMAT_KEY = [
    'doom',
    'hexen',
    'udmf',
  ];

  private const FIELDS_ENTRY_TEASER = '
    e.collection AS `collection`,
    e.path AS `path`,
    m.id AS `id`,
    m.name AS `name`,
    m.title AS `title`,
    m.music AS `music_name`,
    m.format AS `format`,
    m.next AS `next`,
    m.next_secret AS `next_secret`
  ';

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function getAllTeasersForEntry(int $entry_id): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        ' . self::FIELDS_ENTRY_TEASER . '
      FROM entry e
      INNER JOIN maps m ON m.entry_id = e.id
      WHERE
        e.id=:entry_id
      ORDER BY name ASC
    ');

    $maps = $stmt->executeQuery([
      'entry_id' => $entry_id,
    ])->fetchAllAssociative();

    if (empty($maps)) {
      return [];
    }

    foreach ($maps as &$map) {
      $map['format'] = self::MAP_FORMAT_KEY[$map['format']];
    }
    unset($map);

    return $maps;
  }

  public function getTeaser(string $collection, string $path, string $name): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        ' . self::FIELDS_ENTRY_TEASER . '
      FROM entry e
      LEFT JOIN maps m ON m.entry_id = e.id
      WHERE
        e.collection=:collection AND
        e.path=:entry_path AND
        m.name=:name
      LIMIT 1
    ');

    $map = $stmt->executeQuery([
      'collection' => $collection,
      'entry_path' => $path,
      'name' => $name,
    ])->fetchAssociative();

    if (empty($map)) {
      return NULL;
    }

    $map['format'] = self::MAP_FORMAT_KEY[$map['format']];

    return $map;
  }

  public function get(string $collection, string $path, string $name): ?array {
    $stmt = $this->connection->prepare("
      SELECT
        e.id AS `entry_id`,
        e.collection AS `collection`,
        e.path AS `path`,
        m.id AS `id`,
        m.name AS `name`,
        m.title AS `title`,
        m.par_time AS `par_time`,
        m.music AS `music`,
        m.next AS `next`,
        m.next_secret AS `next_secret`,
        m.cluster AS `cluster`,
        m.format AS `format`,
        m.allow_jump AS `allow_jump`,
        m.allow_crouch AS `allow_crouch`,
        m.line_count AS `line_count`,
        m.side_count AS `side_count`,
        m.sector_count AS `sector_count`,
        m.thing_count AS `thing_count`
      FROM entry e
      LEFT JOIN maps m ON e.id = m.entry_id
      WHERE
        e.collection=:collection AND
        e.path=:entry_path AND
        m.name=:name
      LIMIT 1
    ");
    $map = $stmt->executeQuery([
      'collection' => $collection,
      'entry_path' => $path,
      'name' => $name,
    ])->fetchAssociative();

    if (empty($map)) {
      return NULL;
    }

    $map['format'] = self::MAP_FORMAT_KEY[$map['format']];
    $map['allow_jump'] = $map['allow_jump'] !== NULL ? (bool) $map['allow_jump'] : NULL;
    $map['allow_crouch'] = $map['allow_crouch'] !== NULL ? (bool) $map['allow_crouch'] : NULL;

    if ($map['next']) {
      $map['next'] = $this->getTeaser($collection, $path, $map['next']);
    }
    if ($map['next_secret']) {
      $map['next_secret'] = $this->getTeaser($collection, $path, $map['next_secret']);
    }

    return $map;
  }

}
