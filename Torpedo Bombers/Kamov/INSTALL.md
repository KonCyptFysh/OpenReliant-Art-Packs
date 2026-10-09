# Installation

Requires your own StarLancer files and official OpenReliant 0.8.1. Copy the flat `mods/104-kamov-worn-v1` folder into `game-data/mods` and enable it. This replaces the shared player/AI exterior.

On Linux, mark the downloaded scripts executable with `chmod +x tools/launch-kamov*.sh`.

Place all four `tools/launch-kamov*.sh` scripts in your OpenReliant installation, alongside its `releases` and `game-data` directories. Or set OPENRELIANT_HOME to that installation and run the scripts from their tools directory. The inspection launcher explicitly uses `releases/openreliant-v0.8.1-linux-x86_64/openreliant`.

- `launch-kamov-test.sh`: starts stowed for eight seconds, then repeatedly opens for four seconds, holds open for roughly eight, closes for four and holds closed for roughly eight.
- `launch-kamov-stowed-test.sh`: holds the bays closed.
- `launch-kamov-deployed-test.sh`: opens the bays over four seconds and holds them open.
- `launch-kamov-launch-test.sh`: use the game's Launch Missile control to release the torpedoes. After all four finish launching, the bays close. Manual firing remains for user review.

Press 7 for orbit view, arrow keys to rotate, Shift+Up/Down to zoom, and 0 to capture a screenshot. Missions 984–987 contain one Kamov and four carried torpedoes, no enemies or objectives. Engines are disabled for inspection. The first three modes disable firing to preserve all four torpedoes for viewing.

The torpedoes use the existing Coalition torpedo asset. If the approved ordnance pack is installed, its art is reused automatically; the Kamov pack does not duplicate it. Remove or disable this mod to restore the original exterior. Other ship inspection missions are unaffected.

For an upgrade, replace the old mod folder instead of merging into it. This removes obsolete `g`/`r` texture files. The engine generates loadout colours from the unprefixed PNG textures.
