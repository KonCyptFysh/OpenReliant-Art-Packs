# Power-ball reuse, current main 220affa / 0.8.1

This is a small feature-request demonstration, not an engine crash report.
Copy this folder into an isolated game-data/mods directory and enable it. Disable
other HUD replacement mods. Start a mission and press P to open the power window.

With `replace = true`, the native power window is hidden; the probe can display
its live power shares, but cannot request just its animated ball. Set `replace =
false` and restart the mission for the native panel comparison. U/I/O change
power presets. The requested addition is a supported way to draw the native ball
at a script-chosen rectangle, or documented geometry/texture/state sufficient to
recreate it. This is separate from #509's high-resolution texture request.

No engine changes or external artwork are required. For a deterministic capture,
put the provided mission991.dte fixture in this folder and run:

    openreliant /path/to/game-data --mission 991 --ship 4 --view 2 --size 1920x1080 --no-sound --screenshot-ticks 80 --screenshot power-probe.png

Screenshot mode saves its image and exits normally. The optional fixture is
OpenReliant-derived MPL code; its source and license accompany the review bundle.
