# Official 0.7.0 compatibility probes

These diagnostic mod scripts were exercised against the unmodified v0.7.0 Linux x86_64 release at commit `3b27f16779e53c03ccf177bfd2f9ec46a27bbfb7`. They do not replace the HUD pack and must not be shipped as part of its player download.

Use `python3 tools/prepare_stock_hud_probes.py /path/to/temporary-output` from the repository. The builder copies the listed PNG/font exports without changing them. Each case produces its own flat `hudprobe` mod folder. Enable only one case at a time in a separate game-data test directory, with your original StarLancer files available. Start any flight mission with the HUD visible and outline fonts enabled. The scripts use `pcall` to report expected failures without terminating the game. Look for `HUDPROBE` in the log.

- `overlay`: draws the authored radar image at a chosen 350x221 rectangle, larger text, and live fuel/countermeasures. The native radar stays visible. Named probes for additional instrument state fail; the complete API/source review, not these proposed field names alone, establishes which information is absent.
- `memory`: loads seventeen distinct 1024x1024 RGBA images across frames, drawing each at 1x1. Images 1–16 succeed; image 17 raises `BadSize` at the 64 MiB decoded-picture budget.
- `count`: loads 129 distinct filenames containing the same small sprite. Images 1–128 succeed; image 129 raises `TooManyAssets`. This is a file-cache test, not 129 simultaneous HUD widgets.
- `font`: measures the same TTF with different base fonts. The HUD/default bases raise `InvalidFont`; both menu bases and `font="hud"` succeed. The last option uses the native `BLUFONT.ttf` substitution.

The probes include no original game archives. Screenshot mode intentionally exits after capturing; a successful exit is not a crash. See `docs/STOCK_0.7_HUD_COMPATIBILITY.md` for the distinction between current support, mod export work and upstream requests.
