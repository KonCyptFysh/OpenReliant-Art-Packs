# OpenReliant 0.8.1 package update

The current downloads for all 18 ship and ordnance packs now target official OpenReliant 0.8.1. The HUD already targets 0.8.1 and is unchanged.

Removed 81 byte-identical loadout-colour texture copies from 17 ship packs. Total player ZIP size fell from 2.20 GB to 1.19 GB: 46.2% smaller. The engine generates green/red colours from the unprefixed PNGs and inherits their normal and material maps. Ordnance already had no redundant copies.

All retained artwork and model/animation bytes were preserved. Sai's new download now includes its previously approved artwork revision 4.0, matching the gallery.

## Validation

Every native model and test mission passed the official 0.8.1 format checks. Every shipped material set passed a direct probe using the unchanged official 0.8.1 texture loader: generated green/red colours and normal/ORM inheritance were checked. ZIP contents, GitHub asset digests and public checksum files were verified. Individual folders contain `compatibility-0.8.json`, `validation.json` and `publication.json` evidence.

No new gameplay or GPU-rendering captures were performed for this compatibility update. Gallery photographs retain their original engine attribution. Broader gameplay and platform limitations remain in each pack’s notes.

## Upgrade

Close the game, back up the existing mod folder outside `mods`, and replace it completely. Merging files leaves obsolete texture copies behind. Historical releases remain available for rollback.

## Current downloads

| Pack | Release | ZIP size | Reduction |
| --- | --- | ---: | ---: |
| Coyote - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/coyote-v0.1.0-beta.2) | 114.7 MB | 114.4 MB |
| Predator - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/predator-v0.1.0-beta.2) | 129.8 MB | 128.9 MB |
| Reaper - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/reaper-v0.1.0-beta.2) | 60.8 MB | 59.7 MB |
| Wolverine - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/wolverine-v0.1.0-beta.2) | 32.3 MB | 30.8 MB |
| Tempest - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/tempest-v0.1.0-beta.2) | 32.3 MB | 31.9 MB |
| Shroud - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/shroud-v0.1.0-beta.2) | 39.4 MB | 38.9 MB |
| Mirage - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/mirage-v0.1.0-beta.2) | 30.8 MB | 30.1 MB |
| Naginata - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/naginata-v0.1.0-beta.2) | 94.8 MB | 94.5 MB |
| Patriot - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/patriot-v0.1.0-beta.2) | 147.4 MB | 147.0 MB |
| Phoenix - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/phoenix-v0.1.0-beta.2) | 117.7 MB | 116.3 MB |
| Crusader - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/crusader-v0.1.0-beta.2) | 92.6 MB | 91.5 MB |
| Sai - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/sai-v0.1.0-beta.2) | 70.8 MB | 2.3 MB |
| Grendal - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/grendal-v0.1.0-beta.2) | 28.3 MB | 27.2 MB |
| Saber - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/saber-v0.1.0-beta.2) | 28.8 MB | 27.9 MB |
| Basilisk - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/basilisk-v0.1.0-beta.2) | 26.9 MB | 25.9 MB |
| Kamov - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/kamov-v0.1.0-beta.2) | 27.7 MB | 26.4 MB |
| Missiles, Torpedoes and Fuel Pod - Worn Paint | [0.1.0-beta.4](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/ordnance-v0.1.0-beta.4) | 85.4 MB | No texture reduction |
| Loki - Worn Paint | [0.1.0-beta.2](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/loki-v0.1.0-beta.2) | 25.8 MB | 24.2 MB |
