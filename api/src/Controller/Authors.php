<?php

namespace App\Controller;

use App\Repository\AuthorRepository;
use App\Repository\EntryRepository;
use App\Repository\ImageRepository;
use App\Repository\MusicRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Attribute\Cache;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

class Authors extends AbstractController {

    private AuthorRepository $authors;

    private EntryRepository $entries;

    private MusicRepository $music;

    private ImageRepository $images;

    public function __construct(AuthorRepository $authors, EntryRepository $entries, MusicRepository $music, ImageRepository $images) {
        $this->authors = $authors;
        $this->entries = $entries;
        $this->music = $music;
        $this->images = $images;
    }

    #[Route('/author/{alias}', methods: ['GET'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function get(string $alias): Response {
        $author = $this->authors->get($alias);
        if (!$author) {
            throw new NotFoundHttpException();
        }

        $author['entries'] = $this->entries->getForAuthor($author['id']);
        $this->addEntryTeaserData($author['entries']);

        unset($author['id']);

        return $this->json($author);
    }

    private function addEntryTeaserData(array &$entries) {
        foreach ($entries as &$entry) {
            $entry['authors'] = $this->authors->getForEntry($entry['id']);
            $entry['image'] = $this->images->getPrimaryForEntry($entry['id'], $entry['alias']);
            unset($entry['id']);
        }
        unset($entry);
    }
}
