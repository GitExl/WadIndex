<?php

namespace App\Controller;

use App\Repository\EntryRepository;
use App\Repository\MusicRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\Cache;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

class Music extends AbstractController {

    private MusicRepository $music;

    private EntryRepository $entries;

    public function __construct(MusicRepository $music, EntryRepository $entries) {
        $this->music = $music;
        $this->entries = $entries;
    }

    #[Route('/music/{hash}', methods: ['GET'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function get(string $hash): Response {
        $music = $this->music->get($hash);
        if (!$music) {
            throw new NotFoundHttpException();
        }

        $music['heard_in'] = $this->entries->getForMusic($music['id']);
        unset($music['id']);

        return $this->json($music);
    }
}
