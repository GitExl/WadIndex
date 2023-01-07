<?php

namespace App\Controller;

use App\Repository\AuthorRepository;
use App\Repository\EntryRepository;
use App\Repository\ImageRepository;
use App\Repository\LevelRepository;
use App\Repository\MusicRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\Cache;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

class Entries extends AbstractController {

    private EntryRepository $entries;

    private AuthorRepository $authors;

    private ImageRepository $images;

    private MusicRepository $music;

    private LevelRepository $levels;

    public function __construct(EntryRepository $entries, AuthorRepository $authors, ImageRepository $images, MusicRepository $music, LevelRepository $levels)  {
        $this->entries = $entries;
        $this->authors = $authors;
        $this->images = $images;
        $this->music = $music;
        $this->levels = $levels;
    }

    #[Route('/entries/{collection}/{path}', methods: ['GET'], requirements: ['path' => '.+'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function get(string $collection, string $path): Response {
        $entry = $this->entries->get($collection, $path);
        if (!$entry) {
            throw new NotFoundHttpException();
        }

        $entry['authors'] = $this->authors->getForEntry($entry['id']);
        $entry['images'] = $this->images->getAllForEntry($entry['id'], $entry['path']);
        $entry['music'] = $this->music->getAllForEntry($entry['id']);
        $entry['levels'] = $this->levels->getAllTeasersForEntry($entry['id']);
        unset($entry['id']);

        return $this->json($entry);
    }

    #[Route('/entries/latest', methods: ['GET'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function latest(): Response {
        $entries = $this->entries->getLatestTeasers();
        $this->addEntryTeaserData($entries);
        return $this->json($entries);
    }

    #[Route('/list/{collection}/{path}', methods: ['GET'], requirements: ['path' => '.+'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function list(string $collection, string $path): Response {
        if (str_ends_with($path, '/')) {
            $path = mb_substr($path, 0, -1);
        }

        $listing = $this->entries->list($collection, $path);
        if ($listing == NULL) {
            throw new NotFoundHttpException();
        }

        $this->addEntryTeaserData($listing['entries']);
        return $this->json($listing);
    }

    #[Route('/list/{collection}', methods: ['GET'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function listRoot(string $collection): Response {
        $listing = $this->entries->list($collection);
        if ($listing == NULL) {
            throw new NotFoundHttpException();
        }

        $this->addEntryTeaserData($listing['entries']);
        return $this->json($listing);
    }

    private function addEntryTeaserData(array &$entries) {
        foreach ($entries as &$entry) {
            $entry['authors'] = $this->authors->getForEntry($entry['id']);
            $entry['image'] = $this->images->getPrimaryForEntry($entry['id'], $entry['path']);
            unset($entry['id']);
        }
        unset($entry);
    }
}
