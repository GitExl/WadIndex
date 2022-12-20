# Wad Index
A database, indexer and frontend for browsing Doom WADs.

## Usage
The project uses Docker Compose to build a production or development environment.

Copy .env.example to .env and configure it.

The following IWADs are required to be present in your configured IWADs directory:

* ``DOOM.WAD``: (Ultimate) Doom
* ``DOOM2.WAD``: Doom 2
* ``HACX.WAD``: Hacx
* ``HERETIC.WAD``: Heretic
* ``HEXEN.WAD``: Hexen
* ``PLUTONIA.WAD``: Plutonia
* ``STRIFE0.WAD``: Strife (Shareware)
* ``TNT.WAD``: TNT: Evilution

To start the production environment, run

```
docker compose build
docker compose
```

If you want to run the development environment that will serve the Vue application on port 3000 with hot reloading, run

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml build
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Limitations
* In some cases the indexer detects the wrong game type. As a result images with the wrong palette will be output.
* The Python standard library Zip functionality does not support the implode compression type used by some older
files present in the /idgames archive. These files will be skipped.
