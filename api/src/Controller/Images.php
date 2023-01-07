<?php

namespace App\Controller;

use App\Repository\ImageRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\Cache;

class Images extends AbstractController {

    private ImageRepository $images;

    public function __construct(ImageRepository $images) {
        $this->images = $images;
    }

    #[Route('/images/random', methods: ['GET'])]
    #[Cache(public: true, maxage: 21600, mustRevalidate: true)]
    public function get(): Response {
        return $this->json($this->images->getRandom());
    }
}

