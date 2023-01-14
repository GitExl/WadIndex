# Wad Index
A database, indexer and frontend for browsing Doom WADs.

## Usage

### Setup
The project uses Docker Compose to build a production or development environment.

Step 1: Make the source collection files available in a directory of choice. Currently supported collections are
configured in indexer/config.json.

Step 2: Ensure that the following IWADs are present in a directory of choice:

* `DOOM.WAD`: (Ultimate) Doom
* `DOOM2.WAD`: Doom 2
* `HACX.WAD`: Hacx
* `HERETIC.WAD`: Heretic
* `HEXEN.WAD`: Hexen
* `PLUTONIA.WAD`: Plutonia
* `STRIFE0.WAD`: Strife (Shareware)
* `TNT.WAD`: TNT: Evilution

Step 2: Copy `.env.example` to `.env` and set the paths in it to point to your IWADs and source collection files.

Step 3: Start the production Docker environment with:

```
docker compose build
docker compose up
```

If instead you want to run the development environment that will serve the Vue application on port 3000 with hot
reloading, include the dev Docker compose file by running:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml build
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Indexing
To generate the initial index, start a shell into the indexer Docker container with

```docker exec -it wadindex-indexer-1 /bin/bash```

Then run

```python src/index.py --index```

This will run for a while, possibly many hours if the environment is low on resources. Indexing performance is
largely dictated by CPU speed, with IO performance being secondary. As of january 2023 a modern system
with a fast SSD should be able to complete this in about 25 minutes for just the /idgames collection, using 12
processes.

Use the `--processes` argument to indicate how many processes to use. The default is 60% of available CPUs, minus 1.

Other indexing options are available using `--help`.

## Limitations
* In some cases the indexer detects the wrong game type. As a result images with the wrong palette will be output.
* The Python standard library Zip functionality does not support the implode compression type used by some older
files present in some collections. These files will be skipped.
