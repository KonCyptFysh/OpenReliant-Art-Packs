# Local review installation

Requires OpenReliant 0.8.1. With the game closed, copy the flat `96-patriot-worn-v1` directory into `game-data/mods/`. Preserve both native variants and all supplied texture maps/aliases. Back up a previous local installation outside the mods directory before replacing it.

The authoring workflow deploys exactly this repository directory and verifies every file. Launch `tools/launch-patriot-test.sh`; it uses `OPENRELIANT_HOME` or `$HOME/Games/OpenReliant`. The quiet inspection scene contains one Patriot, no enemies or objectives. Press 7, then use arrows to orbit and Shift+Up/Down to zoom.

This is a held review candidate, not a published release.

For an upgrade, replace the old mod folder instead of merging into it. This removes obsolete `g`/`r` texture files. The engine generates loadout colours from the unprefixed PNG textures.
