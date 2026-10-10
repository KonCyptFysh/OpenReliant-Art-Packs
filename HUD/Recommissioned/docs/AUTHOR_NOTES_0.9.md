# Notes for the author: HUD on 0.9.0

Your four HUD changes and the mod PR are working in the 1.10 source/runtime update.
All 257 films are now straight 480x400, with no padding or device.glsl. Portraits
fit at 1080p, 720p and 16:10, including with mod effects off. The name is down
at the right of the portrait, the native power ball is back, and the comms
columns use ink bounds. The top-edge anchoring fix looks right too.

One thing still worth keeping open is #894. The existing synthetic state sweep
on official 0.9.0, ship 5, tick 220 still cuts chunks out of the fuel/countermeasure,
damage, power and wing icons. A normal panel capture is clean. All the PNGs are
unchanged, and there are no script warnings. This is a fixed-tick reproduction;
I haven't established whether it persists or recovers during ordinary flight,
so I'm not calling it the same cause as the GPU-upload fix.

Reproduction: use the current HUD export and mission991.dte in an isolated
profile, plus the preserved state-sweep global script, then run
`--mission 991 --ship 5 --view 2 --size 1920x1080 --no-sound --screenshot-ticks 220 --screenshot state-sweep.png`.
The exact capture, log and source fixture are retained in local integration evidence.
The test script changes shields, armour, velocity, fuel and countermeasures;
it is never included in the normal runtime mod.

#1028 is the remaining layout API request. The current bounded registration
cache stays in place until layouts can be changed after registration.
No new engine fork or shader change is needed for the four completed requests.

These notes accompany the Git snapshot; no issue comment was posted by this update.
