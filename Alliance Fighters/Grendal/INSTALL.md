# Local review installation

Copy `mods/101-grendal-worn-v1` into your OpenReliant game-data/mods directory. Keep runtime files flat inside that folder and enable the mod. Requires your own StarLancer installation and OpenReliant 0.8.1.

Place `tools/launch-grendal-test.sh` alongside `launch-openreliant.sh`, or set OPENRELIANT_HOME to that installation. Run it to open mission 992 with Grendal (ship type 2), no enemies or objectives and sound disabled. Press 7 for orbit view, use the arrow keys to rotate, and Shift+Up/Down to zoom.

Mission 992 is separate from earlier ships' inspection missions. Remove or disable this mod folder to restore the original Grendal.

For an upgrade, replace the old mod folder instead of merging into it. This removes obsolete `g`/`r` texture files. The engine generates loadout colours from the unprefixed PNG textures.
