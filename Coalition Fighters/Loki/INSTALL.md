# Installation

Requires your own StarLancer files and official OpenReliant 0.7.0. Extract the release ZIP. Copy the flat `mods/105-loki-worn-v1` folder into `game-data/mods` and enable it.

Place the three `tools/launch-loki*.sh` scripts alongside the installation's `game-data` and `releases` folders, or set OPENRELIANT_HOME to that installation. The launcher explicitly selects official OpenReliant 0.7.0.

- `launch-loki-test.sh`: starts in the initial folded pose and repeatedly moves to fighting position and back, with pauses to inspect each state.
- `launch-loki-folded-test.sh`: holds the initial folded pose.
- `launch-loki-fighting-test.sh`: plays the native four-second animation, then holds the fighting pose.

Press 7 for orbit view, arrow keys to rotate, Shift+Up/Down to zoom, and 0 for a screenshot. Missions 981–983 contain one Loki (type 65), no enemies or objectives. Engines and weapons are disabled only in these inspection scenes. Native mission script disassembly verifies the full `fighting position` track name and forward/reverse commands.

The shared game launcher and other inspection missions are unchanged. Remove or disable this mod to restore the original exterior.
