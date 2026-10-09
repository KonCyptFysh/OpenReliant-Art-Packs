# HUD 1.4 integration — 9 October 2026

The installed normal launcher now uses unmodified upstream main
`220affa78729a2ce7dcb49602e4f38a4a53d5dc1`, built with Zig 0.17.0 in ReleaseSafe.
The HUD is an ordinary flat folder mod, requires OpenReliant 0.8.1, and contains
no engine patch or replacement executable. The last upstream review established
that this commit's HUD implementation matches official 0.8.1.

## Implemented and deployed

- Stable API names: `color`, `center`, `synchronized`, `power.weapons`, and `objectives.showing`.
- All twelve authored fighter gun panels, including Grendel, Wolverine and Reaper ammunition. `guns.paired` governs the native solid/split shapes; FULL GUNS and Nova retain their actual native rules.
- `subtarget_class` selects approved component frames 393–409. Ion Cannon stays 406. Unknown/missing artwork keeps the complete native target panel.
- Warning light visibility, countermeasure flashing, and cloak/ECM/spectral charge bars use the actual native readings at the authored fixed positions.
- The four armour-hit overlays use `ship_status.hits` and `target_display.hits`. All four are prepared in advance so a one-frame flash does not wait for image decoding.
- Authored radar transition frames follow `radar.rings`; missile poses use each entry's `place`.
- Instrument rectangles follow `window_state.opened` with the native `2 - opened` scale/offset rule. The clock uses `hud.clock` at its authored rectangle, independent of native UI scale.

All 924 runtime files match the deployed copies. Only `mod.ini` and
`recommissioned.luau` changed in the runtime export; all 909 PNGs are byte-identical
to the previous pass. Approved component sources and runtime pixels remain unchanged.

## Checks

The final 1080p HUD capture is byte-identical on official 0.8.1 and current main.
Five protected Mirage live samples through mission time 1:23 show complete
panels; the longer controller stopped on lost focus, so its planned two-minute
run is not claimed complete.

The evidence catalog and exact hashes are in `tracking/integration-0.8.json`.
Checks cover 1080p and 720p, fighter/capital/component targets, communications,
objectives, Grendel/Wolverine/Reaper ammunition, Phoenix, changing shields/damage,
mod-disabled rendering, and native fallback after a deliberately broken image in
an isolated test copy. The broken file was never deployed.

Live keyboard checks verified Wolverine rounds decreasing 3000 → 2976,
FULL GUNS/synchronized/separate modes, missile cycling, radar intermediate positions,
power presets, cloak consumption and ECM recharge. Presentation readings are one
native frame behind, as documented upstream. Screenshot mode saves and exits
normally; this is not a crash. The test ship's destruction in an initial long run
was a mission event; the repeat uses an invulnerable synthetic test ship.

## Remaining work and limits

- The custom power panel still uses a temporary allocation triangle. A native-ball draw helper or documented reconstruction is the remaining upstream presentation request; see `AUTHOR_NOTES_0.8.md` and the small reproduction.
- #894 remains open upstream. Current captures and live samples must be described as a bounded retest, not proof that every GPU, mission or frame is fixed. If it returns, keep the original session log and a screenshot/video and record flicker versus persistence until restart.
- Full campaign, localization, dense combat, repeated alt-tab/relaunch and final user artwork/layout approval remain release QA. The new armour-hit overlays and spectral-shield charge wiring still need dedicated combat/device coverage.
- Seventeen large-schematic artwork jobs remain in the inventory. Fuel-pod component frame 410 has no approved replacement. These are mod artwork tasks, not upstream API blockers; native panels remain available. Do not rework completed 393–409.
- Messages, prompts and radio portraits remain native. Fine detail in the 1024-pixel missile poses is limited by the existing neutral artwork.

Public release and migration into the public art collection remain **on hold**.
No issue comment, release or package has been posted online. The local review ZIP
is for private testing and author feedback only. Editable scripts, layout and
approved artwork are preserved in this repository.
