# Install Phoenix - Worn Paint

Use official OpenReliant 0.8.1 and your own StarLancer game data. Extract the player ZIP and copy `mods/98-phoenix-worn-v1` into the game's `mods/` directory. Keep its files together in that flat folder. Enable Phoenix - Worn Paint in the mod menu if it is disabled.

This pack replaces Phoenix's main, training and loadout artwork. Remove its mod folder to uninstall. Do not install a second Phoenix artwork pack at the same time.

## Optional quiet inspection scene on Linux

Copy `tools/launch-phoenix-test.sh` beside the existing `launch-openreliant.sh` and run `bash launch-phoenix-test.sh`. Alternatively, set `OPENRELIANT_HOME` to the existing launcher directory. The scene uses mission 990 and Phoenix ship 11, with one ship and no enemies or objectives. Press 7 for external orbit; arrow keys rotate and Shift+Up/Down zoom.

For an upgrade, replace the old mod folder instead of merging into it. This removes obsolete `g`/`r` texture files. The engine generates loadout colours from the unprefixed PNG textures.
