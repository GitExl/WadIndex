<?php

namespace App\Controller;

use App\Repository\AuthorRepository;
use App\Repository\EntryRepository;
use App\Repository\ImageRepository;
use App\Repository\MapRepository;
use App\Repository\ListParameters;
use App\Repository\MusicRepository;
use App\Repository\SearchParameters;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpKernel\Attribute\Cache;
use Symfony\Component\HttpKernel\Exception\BadRequestHttpException;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Symfony\Component\Validator\Validator\ValidatorInterface;

class Entries extends AbstractController {

    private EntryRepository $entries;

    private AuthorRepository $authors;

    private ImageRepository $images;

    private MusicRepository $music;

    private MapRepository $maps;

    private ValidatorInterface $validator;

    public function __construct(EntryRepository $entries, AuthorRepository $authors, ImageRepository $images, MusicRepository $music, MapRepository $maps, ValidatorInterface $validator)  {
        $this->entries = $entries;
        $this->authors = $authors;
        $this->images = $images;
        $this->music = $music;
        $this->maps = $maps;
        $this->validator = $validator;
    }

    #[Route('/entries/{collection}/{path}', methods: ['GET'], requirements: ['path' => '.+'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function get(string $collection, string $path): Response {
        $entry = $this->entries->get($collection, $path);
        if (!$entry) {
            throw new NotFoundHttpException();
        }

        $entry['authors'] = $this->authors->getForEntry($entry['id']);
        foreach ($entry['authors'] as &$author) {
            unset($author['id']);
        }
        unset($author);

        $entry['images'] = $this->images->getAllForEntry($entry['id'], $entry['path']);

        $entry['music'] = $this->music->getAllTeasersForEntry($entry['id']);
        unset($entry['music']['id']);

        $entry['maps'] = $this->maps->getAllTeasersForEntry($entry['id']);
        foreach ($entry['maps'] as &$map) {
            $map['authors'] = $this->authors->getForMap($map['id']);
            unset($map['id']);

            foreach ($map['authors'] as &$author) {
                unset($author['id']);
            }
            unset($author);
        }
        unset($map);

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

    #[Route('/entries/updated', methods: ['GET'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function updated(): Response {
        $entries = $this->entries->getUpdatedTeasers();
        $this->addEntryTeaserData($entries);
        return $this->json($entries);
    }

    #[Route('/list/{collection}/{path}', methods: ['GET'], requirements: ['path' => '.+'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function list(Request $request, string $collection, ?string $path=NULL): Response {
        $params = ListParameters::fromRequest($request, $collection, $path);
        $errors = $this->validator->validate($params);
        if (count($errors) > 0) {
            throw new BadRequestHttpException((string) $errors);
        }

        $listing = $this->entries->list($params);
        if ($listing == NULL) {
            throw new NotFoundHttpException();
        }

        $this->addEntryTeaserData($listing['entries']);

        $listing['offset'] = $params->offset;
        $listing['limit'] = $params->limit;

        return $this->json($listing);
    }

    #[Route('/search', methods: ['GET'])]
    #[Cache(public: true, maxage: 3600, mustRevalidate: true)]
    public function search(Request $request) {
        $params = SearchParameters::fromRequest($request);
        $errors = $this->validator->validate($params);
        if (count($errors) > 0) {
            throw new BadRequestHttpException((string) $errors);
        }

        $listing = $this->entries->search($params);
        $this->addEntryTeaserData($listing['entries']);

        $listing['offset'] = $params->offset;
        $listing['limit'] = $params->limit;

        return $this->json($listing);
    }

    private function addEntryTeaserData(array &$entries) {
        foreach ($entries as &$entry) {
            $entry['authors'] = $this->authors->getForEntry($entry['id']);
            foreach ($entry['authors'] as &$author) {
                unset($author['id']);
            }
            unset($author);

            $entry['image'] = $this->images->getPrimaryForEntry($entry['id'], $entry['path']);
            unset($entry['id']);
        }
        unset($entry);
    }
}
