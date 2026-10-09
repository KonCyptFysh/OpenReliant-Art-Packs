# Installation and inspection

Copy `mods/102-saber-worn-v1` into the OpenReliant `game-data/mods` directory and enable the mod. Keep the runtime files flat inside that folder. Requires your own StarLancer installation and official OpenReliant 0.8.1.

Place `tools/launch-saber-test.sh` alongside `launch-openreliant.sh`, or set OPENRELIANT_HOME to that installation. It opens mission 989 as Saber (ship type 43), with one ship, no enemies or objectives, and sound disabled. Press 7 for orbit view; use the arrow keys to rotate and Shift+Up/Down to zoom. Press 0 to save an in-game PNG screenshot.

Mission 989 does not replace another installed ship inspection. Remove or disable this mod to restore the original Saber.

For an upgrade, replace the old mod folder instead of merging into it. This removes obsolete `g`/`r` texture files. The engine generates loadout colours from the unprefixed PNG textures.
