# Local testing

Copy `mods/97-ordnance-worn-v1` into your OpenReliant installation's `game-data/mods` directory while the game is closed. Requires official OpenReliant 0.8.1 or later. Keep an existing version outside the mods directory as a backup before replacement.

To create the optional isolated review environment, run:

```sh
python3 tools/prepare-review.py "$HOME/Games/OpenReliant"
"$HOME/Games/OpenReliant/launch-ordnance-test.sh"
```

The launcher offers all 32 native variants. `--list` prints the menu; a number selects an item directly. Close the game before launching another item. Review settings, caches and saves stay inside `reviews/ordnance-v1`; the normal game launcher and settings are preserved. The test craft inherit Predator controls and cockpit only for inspection; their artwork uses the exact deployed weapon models and textures.

To remove this new pack, remove only `game-data/mods/97-ordnance-worn-v1`, its isolated `reviews/ordnance-v1` environment and `launch-ordnance-test.sh`. Other mods are unaffected.

For an upgrade, replace the old mod folder instead of merging into it. This removes obsolete `g`/`r` texture files. The engine generates loadout colours from the unprefixed PNG textures.
