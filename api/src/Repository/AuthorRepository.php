<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;

class AuthorRepository {

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function get(string $path_alias): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        a.id AS `id`,
        a.name AS `name`,
        a.full_name AS `full_name`,
        a.nickname AS `nickname`
      FROM
        authors a
      WHERE
        path_alias = :path_alias
      LIMIT 1
    ');
    $author = $stmt->executeQuery([
      'path_alias' => $path_alias,
    ])->fetchAssociative();

    if (empty($author)) {
      return NULL;
    }

    return $author;
  }

  public function getForEntry(int $entry_id): array {
    $stmt = $this->connection->prepare('
      SELECT
        a.id AS `id`,
        a.name AS `name`,
        a.full_name AS `full_name`,
        a.nickname AS `nickname`,
        a.path_alias AS `path_alias`
      FROM
        entry_authors ea
      INNER JOIN authors a ON a.id = ea.author_id AND
        ea.entry_id = :entry_id
    ');
    $authors = $stmt->executeQuery([
      'entry_id' => $entry_id,
    ])->fetchAllAssociative();

    if (empty($authors)) {
      return [];
    }

    return $authors;
  }

  public function getForMap(int $map_id): array {
    $stmt = $this->connection->prepare('
      SELECT
        a.id AS `id`,
        a.name AS `name`,
        a.full_name AS `full_name`,
        a.nickname AS `nickname`,
        a.path_alias AS `path_alias`
      FROM
        map_authors ma
      INNER JOIN authors a ON a.id = ma.author_id AND
        ma.map_id = :map_id
    ');
    $authors = $stmt->executeQuery([
      'map_id' => $map_id,
    ])->fetchAllAssociative();

    if (empty($authors)) {
      return [];
    }

    return $authors;
  }

}
