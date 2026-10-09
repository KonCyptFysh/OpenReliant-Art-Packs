# Expose a stable subtarget class or HUD icon identifier

I'm trying to connect our finished subtarget artwork to the scripted target display. We have `hud.target.component`, plus the translated part name and health in `hud.target_display`, but I can't find a stable identifier for which kind of part it is.

The component number tells me which part of that particular ship is selected. It doesn't tell me whether the part is an engine, turret, shield generator, Ion Cannon, etc. Matching the translated display name would break with language changes and would be a fragile way to choose the artwork.

Could the target reading include the part's class as a named value, or the native HUD icon identifier? Ideally nil when there isn't a displayed subtarget. The existing translated name and health can stay as they are.

Attached: `02-stable-subtarget-identity.zip`. This is an API observer, not a crashing reproduction. It leaves the native target display visible and prints the selected component plus every simple field exposed by `hud.target_display`.

Extract its `mods` folder into an isolated game-data folder with other HUD mods disabled. The included mission selects the Reliant engine (component 4):

```sh
openreliant GAME_DATA --mission 991 --ship 4 --view 2 --size 1920x1080
```

The native panel names the ENGINE and shows its icon. The observer reports `component=4`, `subtarget=Engine` and `subtarget_armor=1`, but no stable class or icon identifier. You can also use it in a campaign mission and cycle named subtargets with S. The tested component number is specific to the Reliant, which is why it cannot stand in for a part-type identifier.

The native mapping already exists in `src/engine/game/hud/target_display.zig`, `named(class)`. For example, `ion_cannon` maps to icon `0x196` (frame 406). The script reading currently carries the translated name and armour, but not that class or icon.

The capture exits with code 0, but there are allocator warnings at shutdown. They also occur with the observer removed and are documented in the separate shutdown report.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
