<?php

namespace App\Controller;

use App\Repository\AuthorRepository;
use App\Repository\MapRepository;
use App\Repository\MusicRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\Cache;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Symfony\Component\Routing\Exception\InvalidParameterException;

class Maps extends AbstractController {

    private MapRepository $maps;

    private MusicRepository $music;

    private AuthorRepository $authors;

    public function __construct(MapRepository $maps, MusicRepository $music, AuthorRepository $authors) {
        $this->maps = $maps;
        $this->music = $music;
        $this->authors = $authors;
    }

    #[Route('/maps/{collection}/{path}', methods: ['GET'], requirements: ['path' => '.+'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function get(string $collection, string $path): Response {
        $last_slash = mb_strrpos($path, '/');
        if ($last_slash === FALSE) {
            throw new InvalidParameterException('Path must end with a level name.');
        }

        $entry_path = mb_substr($path, 0, $last_slash);
        $name = mb_substr($path, $last_slash + 1);
        $map = $this->maps->get($collection, $entry_path, $name);
        if (!$map) {
            throw new NotFoundHttpException();
        }

        if ($map['music']) {
            $map['music'] = $this->music->getByNameForEntry($map['entry_id'], $map['music']);
        }
        if ($map['next']) {
            $map['next']['authors'] = $this->authors->getForMap($map['next']['id']);
            unset($map['next']['id']);
        }
        if ($map['next_secret']) {
            $map['next_secret']['authors'] = $this->authors->getForMap($map['next_secret']['id']);
            unset($map['next_secret']['id']);
        }
        $map['authors'] = $this->authors->getForMap($map['id']);

        unset($map['entry_id'], $map['id']);

        return $this->json($map);
    }
}
