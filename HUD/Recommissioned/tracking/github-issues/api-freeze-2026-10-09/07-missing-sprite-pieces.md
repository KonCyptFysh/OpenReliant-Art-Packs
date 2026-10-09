# Current retest status, 9 October 2026

See docs/AUTHOR_NOTES_0.8.md and tracking/integration-0.8.json. The 0.8.1/main
fixed-tick state sweep and bounded live samples look complete. Do not resubmit
the old reproduction as a current confirmed failure. #894 stays open pending
broader review; any recurrence needs the original live log, image/video, and
whether it flickers or persists until restart. The historical report follows.

# Scripted HUD loses parts of pictures during a state-change test

I'm getting whole sections of HUD pictures disappearing in some scenes. This is separate from the white edges we cleaned out of the artwork earlier.

I've attached a reduced version of the HUD and a scripted test scene. At tick 220, the afterburner and countermeasure pictures, damage icons and power/wing pictures lose substantial pieces. Those pictures should remain complete; this isn't the shield segments intentionally disappearing as shields drop.

Attach `07-missing-sprite-pieces.zip`, then extract its `mods` folder into a separate game-data folder with other mods disabled:

```sh
openreliant GAME_DATA --mission 991 --ship 4 --view 2 --size 1920x1080 --no-sound --screenshot-ticks 220 --screenshot hud-pieces.png
```

The test deliberately changes the player's shield/armour, speed, fuel and countermeasures. It is a synthetic diagnostic scene, not an ordinary mission. The ZIP includes the complete reduced mod, the state script, mission source, screenshot and log.

I also ran two comparisons at the same resolution and tick: removing the state script leaves the custom pictures complete; removing the custom HUD while keeping the state script leaves the native icons complete. All three runs exit normally without script warnings or error messages. Instructions and captures for both controls are included.

I haven't pinned this down to the engine or ruled out something in our drawing script. The native control uses a different layout and draw load, so it doesn't prove the cause by itself. Could you help establish whether we're using the drawing API incorrectly, or whether some picture/draw state is being reused between calls? If it's our usage, I'd be happy to change it to the supported approach.

This happens after the image-resource fix in #875. I'm not assuming it is the same issue or asking to reopen #794.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
