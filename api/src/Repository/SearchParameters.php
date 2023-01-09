<?php

namespace App\Repository;

use Symfony\Component\Validator\Constraints as Assert;
use Symfony\Component\HttpFoundation\Request;

class SearchParameters {

  private const FILTER_GAMEPLAY = [
    'singleplayer',
    'deathmatch',
    'cooperative',
  ];

  private const FILTER_GAME = [
    'doom',
    'doom2',
    'tnt',
    'plutonia',
    'heretic',
    'hexen',
  ];

  private const SEARCH_FIELDS = [
    'title',
    'description',
    'filename',
    'textfile',
  ];

  private const SORT_FIELD = [
    'relevance',
    'title',
    'date',
  ];

  private const SORT_ORDER = [
    'asc',
    'desc',
  ];

  #[Assert\NotBlank]
  public string $collection = 'idgames';

  #[Assert\NotBlank]
  public string $searchKey = '';

  #[Assert\Choice(choices: self::SEARCH_FIELDS, multiple: TRUE)]
  public ?array $searchFields;

  #[Assert\Choice(choices: self::FILTER_GAMEPLAY, multiple: TRUE)]
  public ?array $filterGameplay;

  #[Assert\Choice(choices: self::FILTER_GAME, multiple: TRUE)]
  public ?array $filterGame;

  #[Assert\Choice(choices: self::SORT_FIELD)]
  public ?string $sortField;

  #[Assert\Choice(choices: self::SORT_ORDER)]
  public ?string $sortOrder;

  #[Assert\Positive]
  #[Assert\LessThanOrEqual(200)]
  public ?int $limit;

  #[Assert\PositiveOrZero]
  public ?int $offset;

  public static function fromRequest(Request $request): SearchParameters {
    $params = new SearchParameters();
    $params->collection = $request->query->get('collection', 'idgames');
    $params->searchKey = $request->query->get('search_key', '');
    $params->searchFields = self::parseArrayQueryParam($request->query->get('search_fields', ''));
    $params->filterGameplay = self::parseArrayQueryParam($request->query->get('filter_gameplay', ''));
    $params->filterGame = self::parseArrayQueryParam($request->query->get('filter_game', ''));
    $params->sortField = $request->query->get('sort_field', 'relevance');
    $params->sortOrder = $request->query->get('sort_order', 'desc');
    $params->limit = (int) $request->query->get('limit', '50');
    $params->offset = (int) $request->query->get('offset', '0');
    return $params;
  }

  private static function parseArrayQueryParam(string $param): array {
    if (empty($param)) {
      return [];
    }

    return explode(',', $param);
  }

}
