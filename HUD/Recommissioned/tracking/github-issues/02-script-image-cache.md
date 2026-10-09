# Scripted HUD image limits need a way to release unused images

I'm working on a replacement HUD and hitting the script image-cache limits as different artwork loads. The problem isn't just how much is visible at once: images stay cached after they stop being drawn, so changing instruments or cycling through animation poses keeps filling it.

## What happens

Two small tests on official v0.7.0 Linux x86_64 (`3b27f16`) reproduced the limits:

- Sixteen separate 1024x1024 RGBA PNGs load. The seventeenth fails with `BadSize`, after reaching 64 MiB of decoded image data.
- 128 separately named copies of a small PNG load. The 129th fails with `TooManyAssets`.

Each image is requested at a 1x1 screen size, and they're loaded across frames. This isn't the per-frame drawing limit. The script catches the errors, so the game itself keeps running.

This is the scripting picture/font cache. I'm not suggesting ordinary native PNG replacement mods have a 128-file limit.

## Steps to reproduce

1. Extract `02-script-image-cache-repro.zip` outside the game directory.
2. Copy the `mods` folder from its `memory` case into a test game-data directory. Run that case alone and start a flight mission with the HUD visible.
3. Check the `HUDPROBE` log lines. Images 1–16 succeed; image 17 returns `BadSize`.
4. Close the game and remove that diagnostic mod. Repeat with the `count` case instead. Images 1–128 succeed; image 129 returns `TooManyAssets`.

The archive includes both tested scripts, their images and the observed log output. Test one case per fresh game process.

## Possible solutions

Could unused pictures be evicted safely, or could scripts preload and release the image sets they need? Either would let the HUD keep the current ship/instruments loaded without accumulating everything it has ever displayed. Images still referenced by the renderer would need to stay alive until it finishes with them.

A configurable memory budget would also help where the currently visible artwork genuinely needs more than 64 MiB. Alternatively, could scripts use an appropriate native asset path for these images?

I can optimize the exports and trim transparent margins while preserving placement. Atlas support could reduce file count, although it wouldn't by itself solve the decoded-memory limit. For context, the current 90 missile poses would total 360 MiB if all remained cached; they don't need to be resident together.

It would also help if hitting the memory budget reported that directly. `BadSize` makes a valid PNG look as though it has the wrong dimensions.

This is a request to extend the existing resource handling, rather than remove all limits. The desired result is to cycle through more assets than the cache can hold while keeping only the active set resident.

References: [cache limits and lifetime](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L30-L33), [image loading](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L69-L91). Related: [#590](https://github.com/OpenReliant/openreliant/issues/590).
