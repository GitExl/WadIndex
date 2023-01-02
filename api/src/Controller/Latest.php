<?php

namespace App\Controller;

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;

class Latest extends AbstractController {

    #[Route('/latest')]
    public function get(): Response {
        return $this->json(['hi' => TRUE]);
    }
}
