# HUD capture missions

The three synthetic DTE missions preserve the current pass's test scenarios.
Use a separate game-data test directory with the real game archives linked in,
a copied configuration, the selected mod and these missions in a separate
`mods/zz-hud-validation` folder. Do not install them in the player's live HUD.

Mission 991 opens instrument windows and supplies a fighter target; 992 supplies
a capital target and edge indicator; 993 opens the communications scene. These fixtures
are test inputs, not exhaustive campaign validation. The current checked engine
supports `--mission 991 --ship 4 --view 2 --size 1920x1080 --no-sound
--screenshot-ticks 80 --screenshot capture.png`. Screenshot mode exits normally
after capture. Interactive gun-mode testing must use an ordinary running session,
since fixed-tick screenshot mode does not process gameplay input in the same way.

The matching editable generators are `panels.zig`, `objectives.zig` and
`comms.zig`, derived from OpenReliant's sandbox and covered by its MPL license
in `source/engine-patch/LICENSE`. With Zig 0.16.0 and the pinned engine checkout:

```sh
zig run --dep openreliant -Mroot=source/test-fixtures/panels.zig \
  -Mopenreliant="$ENGINE_SOURCE/src/root.zig" -- mission991.dte
```

Use `objectives.zig` for mission992 and `comms.zig` for mission993.

Mission 994 (flash-scene.zig, current main 220affa / Zig 0.17.0) adds mission-driven flashes for enemy lock, incoming missile, ECM, countermeasures and smart targeting. It is an isolated validation fixture; never deploy it to the normal HUD.
