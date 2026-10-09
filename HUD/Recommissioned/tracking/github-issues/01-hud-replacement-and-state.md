# Let HUD mods replace native instruments and read their live state

I'm trying to get a replacement HUD working as a simple drop-in package on 0.7, but I've hit a couple of gaps between drawing a custom overlay and replacing the existing instruments.

## What happens

Scripted HUD displays draw over the native HUD. That's fine for some assets, but our radar has transparent sections, so drawing the larger radar leaves the original radar and contacts underneath.

`hud.set_display_enabled` controls displays registered by scripts. I couldn't find a supported way to replace individual native instruments or change their component positions and text sizes, unless I've overlooked something.

Scripts expose useful ship information, but I also couldn't find all the live state needed to replace the instruments properly: selected gun group/firing mode, gun energy, selected missile and ammunition, HUD-selected target/subtarget, radar range/transition and the native kill count. `object.target` describes the current AI order's target, which isn't the same as a defined HUD-selection value.

## Reproducing the overlay problem

1. Extract the `mods` folder from `01-hud-replacement-repro.zip` into a test game-data directory. Enable just this diagnostic mod alongside the original game files.
2. Start a flight mission at 1920x1080 with the HUD visible and outline fonts enabled.
3. The script draws the custom radar, larger text and live fuel/countermeasures. The original radar remains visible underneath.

This was tested on the official, unmodified v0.7.0 Linux x86_64 release (`3b27f16`). The script uses the existing `hud.picture` and `hud.text` calls. The archive includes the tested script and relevant log output.

## Possible ways to support this

Could the existing instruments expose their layout through a mod file? Positions, sizes, text sizing and separate rectangles for the ship, label, ammo and other parts would let the mod change the appearance while keeping the existing behaviour. The radar would also need its contact area and animation frames to follow that layout.

Otherwise, being able to replace individual instruments through scripts and read the same live information they use would work too. Turning off the mod, or a replacement failing, should bring the native instrument back. The engine would still handle weapon selection, target filtering and instrument state.

We previously had the design working through a few local source changes to check dimensions and colours. I've kept that code as reference, but maintaining an engine fork just for a HUD mod doesn't make sense. Radar, gunnery and missiles would be a useful starting point for proper mod support.

I can adapt our layout/export format to whatever fits OpenReliant. This is a feature request for a normal modding route, not a request to adopt our private INI format or a report that basic script drawing is broken.

References: [current HUD API](https://github.com/OpenReliant/openreliant/blob/v0.7.0/docs/guide/reference.md#openrelianthud), [native/script drawing order](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/openreliant/main.zig#L2031-L2043), [existing object fields](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/objects.zig#L67-L308).
