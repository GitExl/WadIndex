<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;

class MusicRepository {

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function getAllForEntry(int $entry_id): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        em.name AS `name`,
        m.hash AS `hash`,
        m.duration AS `duration`,
        m.type AS `type`
      FROM
        entry_music em
      LEFT JOIN music m ON m.id = em.music_id
      WHERE
        em.entry_id = :entry_id
    ');

    $musics = $stmt->executeQuery([
      'entry_id' => $entry_id,
    ])->fetchAllAssociative();

    if (empty($musics)) {
      return NULL;
    }

    foreach ($musics as &$music) {
      $this->extend($music);
    }

    return $musics;
  }

  public function getByNameForEntry(int $entry_id, string $name): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        em.name AS `name`,
        m.hash AS `hash`,
        m.duration AS `duration`,
        m.type AS `type`
      FROM
        entry_music em
      LEFT JOIN music m ON m.id = em.music_id
      WHERE
        em.entry_id = :entry_id AND
        em.name = :name
      LIMIT 1
    ');

    $music = $stmt->executeQuery([
      'entry_id' => $entry_id,
      'name' => $name,
    ])->fetchAssociative();

    if (empty($music)) {
      return NULL;
    }

    $this->extend($music);

    return $music;
  }

  public function get(string $hash): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        m.id AS `id`,
        m.hash AS `hash`,
        m.duration AS `duration`,
        m.type AS `type`
      FROM
        music m
      WHERE
        m.hash = :hash
      LIMIT 1
    ');
    $music = $stmt->executeQuery([
      'hash' => hex2bin($hash),
    ])->fetchAssociative();

    if (empty($music)) {
      return NULL;
    }

    $this->extend($music);

    return $music;
  }

  private function extend(array &$music) {
    $music['hash'] = bin2hex($music['hash']);
    $music['href'] = '/music/' . $music['hash'] . '.' . $music['type'] . '.gz';
  }

}
