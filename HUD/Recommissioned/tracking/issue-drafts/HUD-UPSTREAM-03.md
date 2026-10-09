# Scripted custom TTF returns InvalidFont with HUD base but works with menu bases

Submission-ready wording: [GitHub issue draft](../github-issues/03-custom-font-hud-base.md). This file retains the fuller engineering notes.

Local draft; not posted. Type: reproducible bug. Related to the palette-font handling discussed in [#520](https://github.com/OpenReliant/openreliant/issues/520); that existing issue also covers remaining small HUD fonts.

Official v0.7.0 Linux x86_64, commit `3b27f16779e53c03ccf177bfd2f9ec46a27bbfb7`, outline fonts enabled, flight HUD visible.

## Reproduction

Use a flat mod containing the HUD pack's valid `BLUFONT.ttf` (Oxanium), `mod.ini` with `[Scripts] Player=probe.luau`, and this player script:

```lua
local hud = require("openreliant.hud")
local done = false
return { engine_handlers = { on_frame = function()
    if done or not hud.shown then return end
    done = true
    for _, base in {"default", "hud", "menu_small", "menu_large"} do
        local ok, result = pcall(hud.measure, "H", {font="BLUFONT.ttf", base_font=base})
        print(base, ok, result)
    end
    print(pcall(hud.measure, "H", {font="hud", scale=1.5}))
end } }
```

Observed: `default` and `hud` return `false, font BLUFONT.ttf: InvalidFont`; both menu bases succeed. `font="hud"` succeeds and native logging confirms `BLUFONT.FNT uses BLUFONT.ttf`. The same file therefore loads successfully through other supported paths. Calling `hud.text` with the filename and HUD base also failed in the initial probe.

Expected: a valid custom TTF should fit the HUD base, as documented, or report a more specific unsupported-base error.

## Possible cause and workaround

[`Assets.loadFont`](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L93-L141) constructs a ramp font and calls `Fit.of` with `level_cover` for every base. The [native attachment path](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/game/hud.zig#L354-L365) uses the palette-derived ink coverage for the HUD. This difference is a source-based diagnosis to investigate, not a verified fix.

Workaround for this pack: retain the native `BLUFONT.ttf` replacement and use `font="hud"` with script text scaling. This bug does not require shipping a companion engine.

Test font SHA-256: `6690376ac20ddf9ca4e2f01f0769c1ee2b275c05512c69a5de6f92b95d7be679`. Preserve the included Oxanium OFL notice if attaching the font.

## Suggested fixes

The preferred small upstream fix is to share the native font-fitting setup with scripted custom fonts. Preserve the selected base's palette/ramp interpretation and use its actual ink coverage when fitting; carry over the appropriate ink colour and special-colour glyph fallback. Do not pass the HUD's palette indices through `level_cover` unconditionally. A shared helper would keep the native and scripting paths consistent without embedding knowledge of this particular font.

The smaller interim option for this mod is already available: install `BLUFONT.ttf` normally, then request `font="hud"` from scripts and use the existing `scale` parameter. This preserves the selected HUD font but does not provide an independently chosen custom typeface for each instrument. Using a menu base is another workaround only where its different text metrics are acceptable.

Suggested regression case: use a real palette-based HUD bitmap font and a valid TTF; verify `measure` and drawing with the HUD/default bases, both menu bases, native substitution, a missing glyph and a special-colour glyph. Also preserve the existing outline-fonts-disabled behavior. The proposed coverage fix has not been built or tested locally; the successful workaround and failing cases have been tested on the official binary.
