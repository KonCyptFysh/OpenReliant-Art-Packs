# Drawing one custom font at six sizes corrupts the first two text rows

I'm still getting corrupted text when I use one custom font at several sizes in the same HUD frame. I've reduced this to a small script with no HUD artwork involved.

The attached test draws the same line at six scales, 1.0 through 2.0. On the left, all six rows use one TTF filename. On the right, each row uses its own filename, but all seven files contain exactly the same font bytes.

Expected: both columns match. Actual: the first two rows on the left are scrambled; the right column is clear. The other four pairs match. There are no script warnings or error messages in this run.

Attach `04-shared-font-sizes.zip`. Extract its `mods` folder into a separate game-data folder with other mods disabled, then run:

```sh
openreliant GAME_DATA --mission 991 --ship 4 --view 2 --size 1920x1080 --no-sound --screenshot-ticks 180 --screenshot font-test.png
```

That command saves a screenshot and exits normally. The ZIP includes the script, font licence, screenshot and log.

I can work around it by using separate font filenames for different sizes, but I'd like to avoid duplicating the font throughout the pack. Could sizes already used by the current frame stay valid until that frame has finished drawing?

`src/engine/game/hud/outline.zig` currently keeps four size atlases and reuses the least recently used slot. That looks relevant, but I haven't proved the root cause or prepared an engine patch. This is separate from the old InvalidFont problem, which no longer reproduces on main.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
