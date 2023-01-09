<?php

namespace App\Repository;

use Symfony\Component\Validator\Constraints as Assert;
use Symfony\Component\HttpFoundation\Request;

class ListParameters {

  private const SORT_FIELD = [
    'title',
    'date',
  ];

  private const SORT_ORDER = [
    'asc',
    'desc',
  ];

  #[Assert\NotBlank]
  public string $collection = '';

  public ?string $path = '';

  #[Assert\Choice(choices: self::SORT_FIELD)]
  public ?string $sortField;

  #[Assert\Choice(choices: self::SORT_ORDER)]
  public ?string $sortOrder;

  #[Assert\Positive]
  #[Assert\LessThanOrEqual(200)]
  public ?int $limit;

  #[Assert\PositiveOrZero]
  public ?int $offset;

  public static function fromRequest(Request $request, string $collection, ?string $path=NULL): ListParameters {
    $params = new ListParameters();

    $params->sortOrder = $request->query->get('sort_order', 'asc');
    $params->sortField = $request->query->get('sort_field', 'title');
    $params->limit = (int) $request->query->get('limit', '50');
    $params->offset = (int) $request->query->get('offset', '0');

    $params->collection = $collection;
    if ($path && str_ends_with($path, '/')) {
        $params->path = mb_substr($path, 0, -1);
    }
    else {
        $params->path = $path;
    }

    return $params;
  }

}
