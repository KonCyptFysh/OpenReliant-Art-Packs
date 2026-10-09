# Expose HUD warning flash state and device charge bars

The new `hud.lights` list helps, but it only tells us which warnings/devices are active. I'm still keeping those native because I can't faithfully draw their flashing and charge indicators from that alone.

Could scripts read whether each active light is visible on this frame, plus its charge-bar value where it has one? I'm mainly looking at ECM, cloak and spectral shields. The flashing countermeasure icon/readout and the shield-hit quadrant flashes would be useful too.

For the light list, keeping an entry present while it flashes dark would let a custom HUD reserve the same space without the other icons jumping around. An active state, visible state and optional charge fraction would work, but I'm happy to follow whatever shape fits the API.

Attached: `03-warning-and-device-presentation.zip`. The observer leaves all native instruments active and prints `hud.lights`, the countermeasure count and shield/armour readings. The README has the controls and limits of the test.

This is a request based on the current API and native drawing code, not a claim that I've tested every device state. The simple mission validates that the observer runs. Use a ship/mission with the relevant device to compare its native flashing/bar with the logged readings.

Source: `src/scripting/instruments.zig` (`Lights`, `ShipStatus`, `countermeasures`) and `src/engine/game/hud.zig` (`lightsShown`, `lightsWith`, `drawLights`). Native drawing applies presentation state which isn't included in those script readings.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
