<?php

namespace App\Controller;

use App\Repository\LevelRepository;
use App\Repository\MusicRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\Cache;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Symfony\Component\Routing\Exception\InvalidParameterException;

class Levels extends AbstractController {

    private LevelRepository $levels;

    private MusicRepository $music;

    public function __construct(LevelRepository $levels, MusicRepository $music) {
        $this->levels = $levels;
        $this->music = $music;
    }

    #[Route('/levels/{collection}/{path}', methods: ['GET'], requirements: ['path' => '.+'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function get(string $collection, string $path): Response {
        $last_slash = mb_strrpos($path, '/');
        if ($last_slash === FALSE) {
            throw new InvalidParameterException('Path must end with a level name.');
        }

        $entry_path = mb_substr($path, 0, $last_slash);
        $name = mb_substr($path, $last_slash + 1);
        $level = $this->levels->get($collection, $entry_path, $name);
        if (!$level) {
            throw new NotFoundHttpException();
        }

        if ($level['music']) {
            $level['music'] = $this->music->getByNameForEntry($level['entry_id'], $level['music']);
        }
        unset($level['entry_id']);

        return $this->json($level);
    }
}
