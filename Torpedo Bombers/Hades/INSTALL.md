# Installation and review

Copy `mods/114-hades-worn-v1` to OpenReliant's `game-data/mods`. Requires your own StarLancer data and official OpenReliant 0.8.1. The same runtime is installed in the local review setup.

Keep the four launcher scripts together beside `launch-openreliant.sh`, or set OPENRELIANT_HOME to your installation. `launch-hades-test.sh` defaults to the cycle mode; it also accepts `stowed`, `deployed`, `cycle` or `launch`, followed by optional engine arguments.

| Launcher | Scene |
| --- | --- |
| launch-hades-test.sh | Start stowed, then repeatedly deploy and retract the four arms |
| launch-hades-stowed-test.sh | Hold stowed with four carried torpedoes |
| launch-hades-deployed-test.sh | Deploy and hold; allow about four seconds |
| launch-hades-launch-test.sh | Deploy, release four torpedoes in sequence, then retract |

Missions 968, 967, 966 and 965 respectively use Hades type 26 and four Allied torpedoes of type 74. The launch mode uses native mission StartLaunch commands, not a new player control. Release begins at about nine seconds, with roughly seven seconds between torpedoes.

No enemies or objectives; the ship is stationary and invulnerable. Sound is off. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, and 0 for a screenshot. Close an existing game session before starting another. Remove or disable this mod to restore the original Hades.
