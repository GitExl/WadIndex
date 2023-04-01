<?php

namespace App\Repository;

use Doctrine\DBAL\Connection;

class ImageRepository {

  private Connection $connection;

  public function __construct(Connection $connection)  {
      $this->connection = $connection;
  }

  public function getPrimaryForEntry(int $entry_id, string $entry_path): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        ei.name AS `name`,
        ei.width AS `width`,
        ei.height AS `height`,
        ei.aspect_ratio AS `aspect_ratio`
      FROM
        entry_images ei
      WHERE
        ei.name = "titlepic" AND
        entry_id = :entry_id
      LIMIT 1
    ');

    $image = $stmt->executeQuery([
      'entry_id' => $entry_id,
    ])->fetchAssociative();

    if (empty($image)) {
      return NULL;
    }

    $this->generateImagePaths($image, $entry_path);

    return $image;
  }

  public function getAllForEntry(int $entry_id, string $entry_path): ?array {
    $stmt = $this->connection->prepare('
      SELECT
        ei.name AS `name`,
        ei.width AS `width`,
        ei.height AS `height`,
        ei.aspect_ratio AS `aspect_ratio`
      FROM
        entry_images ei
      WHERE
        entry_id = :entry_id
      ORDER BY ei.index
    ');

    $images = $stmt->executeQuery([
      'entry_id' => $entry_id,
    ])->fetchAllAssociative();

    if (empty($images)) {
      return [];
    }

    foreach ($images as &$image) {
      $this->generateImagePaths($image, $entry_path);
    }
    unset($image);

    return $images;
  }

  public function getRandom(int $count=15): array {
    $images = [];

    for ($i = 0; $i < $count; $i++) {

      // Method to quickly get a random entry_id from the entry_images table, then
      // get the primary image for that entry.
      $stmt = $this->connection->prepare('
        SELECT
          ei.name AS `name`,
          ei.width AS `width`,
          ei.height AS `height`,
          ei.aspect_ratio AS `aspect_ratio`,
          e.path AS `entry_path`
        FROM entry_images ei
        INNER JOIN
          (SELECT CEIL(
            (SELECT MIN(entry_id) FROM entry_images) +
            (
              RAND() *
              (SELECT MAX(entry_id) FROM entry_images) - (SELECT MIN(entry_id) FROM entry_images)
            )
          ) AS entry_id)
        AS x
        LEFT JOIN entry e ON e.id = ei.entry_id
        WHERE
          ei.entry_id >= x.entry_id AND
          ei.is_primary = 1
        LIMIT 1
      ');
      $image = $stmt->executeQuery()->fetchAssociative();

      $this->generateImagePaths($image, $image['entry_path']);
      unset($image['entry_path']);

      $images[] = $image;
    }

    return $images;
  }

  private function generateImagePaths(array &$image, string $base_path) {
    $dirname = pathinfo($base_path, PATHINFO_DIRNAME);
    $filename = pathinfo($base_path, PATHINFO_FILENAME);

    $image['href'] = 'graphics/' . $dirname . '/' . $filename . '_' . $image['name'] . '.webp';
    $image['href_thumbnail'] = 'graphics/' . $dirname . '/' . $filename . '_' . $image['name'] . '_thumb.webp';
  }

}
