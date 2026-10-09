# Upstream checks

These are test-only player scripts for unmodified upstream commit 410d0a6.
They are not exported with the player mod.

- `state.luau` logs the actual ship, gun mode, replaced instruments and native
  bounds on frame 30. It safely skips older engines. Put it in a separate test mod
  with `[Scripts] Player=state.luau` alongside the ordinary HUD mod.
- `cache-cycle.luau` draws all 585 exported PNGs twice, one new image a frame.
  Copy those PNGs unchanged into its own separate test mod and set
  `[Scripts] Player=cache-cycle.luau`. Run at least 1180 screenshot ticks. Both
  `HUD_CACHE_PASS 585 pictures` and `HUD_CACHE_PASS 1170 pictures` must appear,
  without a script warning. This exceeds both the 128-file cache and its 128 MiB
  memory budget over time, exercising eviction instead of loading them together.
- Missing artwork: copy the runtime HUD to a separate test installation, omit
  `rc_gunnery_ship_wireframes_coyote_wireframe.png`, and fly the Coyote panel
  fixture. The script reports the missing file once and keeps native gunnery.

Use the preserved `source/test-fixtures/mission991.dte` in an isolated game-data
directory for the instrument scene. The screenshot command exits after saving
its image. Never use the live player profile for destructive fault injection.
