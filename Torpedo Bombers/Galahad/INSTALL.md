# Installation and inspection

Copy `mods/113-galahad-worn-v1` into OpenReliant's `game-data/mods` directory and enable it. Runtime files stay flat. Requires your own StarLancer installation and official OpenReliant 0.8.1.

Copy all four `tools/launch-galahad-*.sh` scripts together alongside `launch-openreliant.sh`, or set OPENRELIANT_HOME to the installation. The main script accepts a mode followed by optional engine options:

| Launcher or mode | Review |
| --- | --- |
| launch-galahad-test.sh (default cycle) | Start stowed, repeatedly deploy and reverse the four native feet |
| launch-galahad-stowed-test.sh | Hold original stowed pose with two carried torpedoes |
| launch-galahad-deployed-test.sh | Deploy and hold; allow about four seconds for the native animation |
| launch-galahad-launch-test.sh | Deploy, release torpedo 1 after about nine seconds and torpedo 2 about seven seconds later, then stow |

The launch sequence uses native mission StartLaunch commands. Galahad does not share Kamov's player carried-torpedo Launch Missile shortcut. Torpedoes use the existing Allied torpedo asset and launch mounts. The review does not add new gameplay controls.

These are missions 973, 972, 971 and 970 respectively, with Galahad ship type 25 and two torpedoes of type 74. There are no enemies or objectives; engines, guns and ejection are disabled and the three objects are invulnerable. Launchers use official 0.8.1 directly, sound disabled, 1920x1080, 60 FPS. Close an existing session before launching a new one.

Press 7 for orbit, arrow keys to rotate, Shift+Up/Down to zoom and 0 for screenshots. Remove or disable the mod to restore the original Galahad. OpenReliant generates green/red loadout textures; duplicated colour files are unnecessary.
