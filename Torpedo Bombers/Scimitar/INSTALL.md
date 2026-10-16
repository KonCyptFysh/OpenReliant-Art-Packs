# Installation and review

Copy `mods/115-scimitar-worn-v1` into OpenReliant's `game-data/mods`. Requires your own StarLancer data. The native pack supports 0.8.1; these local review launchers use the newly installed official 0.18.0.

Keep both launcher scripts beside `launch-openreliant.sh`, or set OPENRELIANT_HOME to the installation.

- `launch-scimitar-test.sh`: quiet stationary ship with two carried Coalition torpedoes, mission 964.
- `launch-scimitar-launch-test.sh`: timed release, mission 963; first torpedo after about nine seconds, second roughly seven seconds later.

No moving deploy/stow geometry exists on this model. The two native launch points are preserved. The review uses native StartLaunch commands rather than new player controls. Ship type 48, torpedo type 92.

Press 7 for orbit; arrows rotate; Shift+Up/Down zoom; 0 saves a screenshot. No enemies, invulnerable ship, sound off. Close any running game before starting another. Disable or remove this mod to restore the original Scimitar.
