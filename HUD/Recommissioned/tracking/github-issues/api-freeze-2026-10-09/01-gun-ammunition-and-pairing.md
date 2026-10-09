# Expose live gun ammunition and selected-group pairing to HUD scripts

I'm getting the custom HUD running as a normal drop-in mod now. The replacement support and the new readings have got most of it working, but there are still two gunnery details I can't get from the script API.

`hud.guns` gives us the selected group, FULL GUNS, synchronised firing, gun type and charge. Could it also provide the live rounds remaining and whether the selected group contains a pair?

At the moment I'm keeping native gunnery on Grendel, Wolverine and Reaper so I don't hide their ammunition. The `rounds` value in `openreliant.records` is the ship's static definition, not its remaining rounds. The synchronised flag also doesn't tell us whether the selected group is paired and should show the solid/split indicator in the first place.

Something like nullable `rounds` and a `paired` flag would cover this. Those are suggested names, not fields that already exist. It would be good to use the same values the native gunnery display uses, so custom ship definitions work too.

Attached: `01-gun-ammunition-and-pairing.zip`. It contains a small observer mod and a test mission. Extract its `mods` folder into an isolated game-data folder, with other HUD mods disabled, then run:

```sh
openreliant GAME_DATA --mission 0 --ship 8 --view 2 --size 1920x1080
```

The native Wolverine display stays visible; the attached capture shows 3000 rounds while the observer has no rounds field. Mission 0 keeps the ordinary Wolverine instead of selecting its later-mission twin. Fire the guns with Space. Press G to select one group instead of FULL GUNS, then toggle synchronisation with Ctrl+G. Compare the native display with the fields printed above it and the `HUD_FREEZE` lines in the log. The probe prints the proposed fields as nil; it doesn't fake their values.

Source: `src/scripting/instruments.zig` (`Guns`) and `src/engine/game/hud/gunnery.zig` (`items`). The native renderer already checks `paired()` and reads the live object's rounds.

The attached capture verifies the exposed fields at startup. The firing/toggle steps are instructions for interactive follow-up, not a claim that this attachment includes a successful before/after ammunition capture.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
