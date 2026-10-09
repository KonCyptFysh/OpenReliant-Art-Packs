# Valid custom TTF gives InvalidFont with the HUD base font

## What happened

The same `BLUFONT.ttf` works as the normal HUD font replacement, but a script requesting that file with the HUD base font gets `InvalidFont`.

The font is Oxanium. It works with either menu base, and `font="hud"` also works, so it doesn't look like a broken font file.

## Steps to reproduce

1. Copy the `mods` folder from `03-custom-font-hud-base-repro.zip` into a test game-data directory and enable the diagnostic mod.
2. Turn on outline fonts and start a flight mission with the HUD visible.
3. Check the `HUDPROBE` log lines. The script measures `"H"` using the same TTF with each base font.

The failing call is:

```lua
hud.measure("H", {font="BLUFONT.ttf", base_font="hud"})
```

Results from the official binary:

| Font choice | Result |
|---|---|
| `BLUFONT.ttf`, flight default base | `InvalidFont` |
| `BLUFONT.ttf`, `hud` base | `InvalidFont` |
| `BLUFONT.ttf`, `menu_small` base | Works |
| `BLUFONT.ttf`, `menu_large` base | Works |
| `font="hud"`, using the native TTF replacement | Works |

The native log also confirms `BLUFONT.FNT uses BLUFONT.ttf`. Calling `hud.text` with the filename and HUD base failed in the initial test too. The reproduction catches the errors so the game keeps running.

## What should happen

A valid custom font should work with the documented HUD base, as it does with the menu bases.

## Possible cause and workaround

The scripted font-loading path appears to fit every custom font using ramp coverage, while the native HUD path uses palette-derived coverage. Could the scripted path reuse the native fitting logic and preserve the selected base's palette/ramp handling? That's a possible cause from reading the source, not a tested fix.

For now, installing `BLUFONT.ttf` normally and using `font="hud"` with script text scaling works around it. That doesn't let each instrument choose its own independent font, but it gets this HUD's text drawing.

## Version and system

Official OpenReliant v0.7.0, Linux x86_64, commit `3b27f16`. Fedora Linux 42 KDE, X11 via SDL. The machine has Intel Iris Xe and NVIDIA GeForce RTX 3070 Mobile graphics; the active GPU was not separately recorded for this test.

The reproduction uses only the diagnostic mod and original game data in a flight mission. The original automated run also used a local mission fixture. `--no-mods` removes the script needed to exercise the problem. For the original-game comparison field: **I don't know**; this concerns OpenReliant's added scripting API rather than equivalent original-game behaviour.

The ZIP includes the exact tested font, its OFL licence, script and relevant log output.

References: [scripted font fitting](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L93-L141), [native font fitting](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/game/hud.zig#L354-L365). Related to the palette-font work in [#520](https://github.com/OpenReliant/openreliant/issues/520).
