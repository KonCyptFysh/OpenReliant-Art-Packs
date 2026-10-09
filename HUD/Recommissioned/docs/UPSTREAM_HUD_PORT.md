# Current upstream HUD mod port, 8 October 2026

The current working candidate is HUD 1.3 on unmodified upstream
`30163d955177a4a13e5815985c84f3b9ae3748a6`, including
[#868](https://github.com/OpenReliant/openreliant/pull/868). The engine source
matches the downloaded main archive, with zero private engine edits. #832 is
now closed. The earlier progress narrative below is retained as dated history.

The ordinary mod replaces radar (settled ranges with authored projection),
player status, small target status, whole-ship large targets, speed/energy
curves, damage, power, wing status, objectives and comms, alongside the prior
gunnery, missile and readout panels. Windows follow official visibility state;
chase hides the instruments. Fuel and countermeasures now use HUD readings.
Objective/comms labels wrap or fit their authored bounds, with separate font
resources avoiding the previously reproduced four-size atlas collision.

`source/scripts/hud.luau` and `instruments.luau` are editable templates.
`ship-art.json` records vanilla art mappings against this source revision.
`tools/build_script.py` compiles the preserved layout into the runtime script;
the engine still does not parse the private placement INI. `build_mod.py`
exports 924 flat runtime files. All 586 prior PNGs and approved subtargets are
unchanged. The new derivatives are 45 horizontal mirrors and 278 complete
left/right gauge states. Only the current fills are prepared. Cold decoding
is budgeted by pixel count (one megapixel, at most twelve files each frame),
with native instruments retained while required art is loading.

Native fallback remains for selected subtargets, unavailable art, unknown ship
or missile types, ammunition-bearing gun groups and radar range transitions.
Lights, messages, prompts and radio portraits stay native. The temporary power
allocation triangle follows the exact percentages but is not the animated ball.
Shield hit flashing and complete native window animations are not reproduced.

Focused tests cover 1080p/720p, objectives/comms, radar range transitions, power
allocation, missile cycling, gun charge, synchronised/separate and FULL GUNS
state, ordinary Coyote flight, chase hiding, and released 0.7.0 fallback.
The attempted subtarget key test did not produce a selected component and is
explicitly unverified. Some Mirage/stress-scene sprites and text lose pieces
without errors. That rendering issue remains open; decoding/gauge controls
have not explained it. Do not treat all captures as visual passes.

Exact results, limits and hashes are in `tracking/hud-api-expansion.json`.
`.local/api-expansion/` holds local evidence and deployment/backup records.
Both dev launchers use the installed 30163d9 review profile. The normal launcher
remains on official 0.7.0; the dev binary is not part of the player package.
Public release, user visual approval and final gameplay QA remain pending.

---

# Historical port notes (through 240f075)

The maintainer merged [PR 833](https://github.com/OpenReliant/openreliant/pull/833),
closing [issue 793](https://github.com/OpenReliant/openreliant/issues/793), and
[PR 831](https://github.com/OpenReliant/openreliant/pull/831), closing
[issue 794](https://github.com/OpenReliant/openreliant/issues/794).
The latest published release checked for this pass is still **v0.7.0**. These
changes are in newer upstream source, not that release.

The development test uses unmodified upstream commit
`240f075183abc20bb3fafe91ae30c1b0aad7ca57`, verified as main at 07:51 UTC on
8 October 2026. No private engine patch is applied.
This build is a local test dependency, not part of the player mod or a proposed
companion distribution. The normal game launcher stays on official 0.7.0.

This revision includes [PR 864](https://github.com/OpenReliant/openreliant/pull/864),
the first part of #832, and [PR 866](https://github.com/OpenReliant/openreliant/pull/866),
the second part with radar contacts and target display. The new gauges, fuel, countermeasures, ship-status arcs,
lights, clock, text, radar contacts and target-display fields are accessible in the probe. An explicit switch
to the separate chase camera confirms readings remain available with native
instruments hidden and the clock advancing. This is a focused baseline, not
coverage of every warning/device/damage state. Our remaining custom panels
still need to adopt the newly available fields.

Both `launch-hud-upstream-test.sh` and `launch-openreliant-dev.sh` use this
installed development build and isolated profile. The first opens the HUD test
mission; the second opens the menu. The prior 410d0a6 and 86aa967 reviews remain available.
Current records and author feedback are in `tracking/main-dev-baseline.json`
and `tracking/github-issues/main-240f075-author-note.txt`.

## What the new mod script does

- Replaces the native afterburner, kill and countermeasure readouts with the
  authored icons and larger numbers, using live game values.
- Replaces gunnery on supported ships with the authored wireframe and lit gun
  groups and a smaller, left-aligned weapon name above the panel. Original native
  sprites 240/241 show synchronised/individual pairing underneath the heading;
  FULL GUNS and Nova Cannon omit that bar. The extra mode caption is removed.
  FULL GUNS leaves the Phoenix's charging Nova group unlit, as the game does.
- Replaces the missile window with the authored grids and 1024-pixel carousel
  images, plus larger selection and ammunition text. Ring positions follow the
  native ten-position ordering. Window keys and timeouts still belong to the game.
- Enlarges and moves the complete native radar and repositions its clock, using
  the new native-instrument layout API. The radar keeps its contacts, navigation
  information and range transitions.
- Detects engines without the new API and retains their native HUD. Unknown ship
  or missile types retain the corresponding native weapon display. An error in a
  registered replacement lets upstream restore its native instrument.
- Loads one new image per frame before enabling a replacement, so cold missile
  images do not exceed the script's 100 ms execution budget. During preparation
  the native instrument remains visible. Separate font instances keep native
  text, weapon labels and counters within the four-size atlas limit per font.

The exporter reads `source/hud/hud_layout.ini` and the portable layout descriptors,
then generates `recommissioned.luau`. The engine does not parse this private INI.
Edit `source/scripts/hud.luau` and the layout, then rebuild. Do not hand-edit the
generated runtime script. All PNGs and completed subtargets 393-409 are preserved.

## Remaining work

[Issue 832](https://github.com/OpenReliant/openreliant/issues/832) is still open.
It tracks the remaining instrument readings needed for full replacements.

- **Custom radar:** our 350x221 artwork has a different projection from the native
  134x65 rings. Stretching it over the native rings would misalign the contacts.
  Contact positions, heights and looks are now exposed in #866. The custom
  projection/layout port is ours to implement; current native ring-animation
  progress remains an optional API request. The current radar is the enlarged
  native one, not yet our authored replacement.
- **Gun ammunition:** `hud.guns` exposes charge, groups and firing mode, but no live
  expendable-round count. Grendel, Wolverine and Reaper retain native gunnery so
  their ammunition is never hidden. This also avoids guessing a count from the
  ship's static ammunition capacity.
- **Other panels:** damage, power, wing status, objectives, communications,
  ship/target status, status lights and gauges keep their native drawing for now.
  Ship status, gauges and the active light list are now available to port;
  target-display values and radar contacts are also available in #866. Other
  window/message readings remain planned in #832 part 3.
  Completed subtarget artwork is preserved but full custom target presentation
  is not active in this script pass.
- **Presentation:** the new light list reports active names, but not their
  visible flash phase or device-charge bars. Those and window opening/closing
  animation details are not exposed yet. The custom countermeasure count remains steady;
  scripted weapon panels follow the window's open state without its slide/zoom.
  The gunnery floor now uses a losslessly mirrored export to reproduce native
  orientation with the picture API. Further aspect-ratio/layout refinement and
  gameplay review remain open.
- **Image cache:** upstream now has a 128 MiB budget and evicts older images. The
  90 full missile canvases exceed that budget as a complete set. Cycling works
  through eviction; transparent-margin export optimisation remains an option
  if gameplay testing reveals decode stutter.

## Initial port and artwork checks on 410d0a6

The initial pass's 29 roots and 61 child rectangles matched the previous
renderer's layout helper exactly. The subsequent legacy-gunnery correction
changes two children and adds a pairing-bar child (91 rectangles total); the
other 88 are preserved. It keeps the heading and original pairing sprites at
the legacy offsets relative to the side grid, at twice native art size for
1080p. Tall wireframes move down as needed to clear the heading, with all their
gun layers kept together. All 585 existing PNGs remain byte-identical to the deployed
art. Screenshot checks cover Coyote at 1920x1080 and 1280x720, Mirage FULL GUNS,
Wolverine native gunnery fallback, missing-art fallback, and released 0.7.0 fallback.
The cache probe completed 1170 image draws, visiting all 585 PNGs twice, without
script errors. These checks do not replace interactive gameplay review.

The initial combined font instance produced garbled text when more than four
sizes were drawn. The isolated font instances pass the same scene without that
corruption. This is a mod workaround for the current atlas constraint. Custom
TTF with the HUD base now loads successfully on this upstream revision; the
older 0.7.0 `InvalidFont` reproduction remains historical evidence.

Evidence and inventories are recorded in `tracking/upstream-port.json` and the
ignored `.local/upstream-port/` evidence folder. Final community release remains
on hold until an official release contains the APIs and the remaining HUD work
and gameplay checks are complete.

## Legacy gunnery refinement

Editable placement is in `source/hud/hud_layout.ini`, drawing logic in
`source/scripts/hud.luau`, and silhouette clearance is generated from the
preserved alpha bounds by `tools/build_script.py`. No raster source is edited.
The reference is upstream `src/engine/game/hud/gunnery.zig`: name `(1,-157)`,
pairing `(1,-139)`, shapes `0xF0`/`0xF1`, against the side-grid anchor `(1,-147)`
in `windows.zig`. The 1080p heading has 16-pixel requested cap height. Shape size
compensates for the engine's native HUD scale; text is left-aligned and fitted
to the existing 230-pixel heading width.

This pass verifies solid and split pairing, FULL GUNS and 1080p/720p placement.
Nova's no-bar rule matches inspected native code; its interactive capture was
inconclusive because the test window paused, so it is not a recorded runtime
pass. Some interactive test exits also logged upstream SafeAllocator leaks;
those diagnostics are preserved rather than counted as clean engine shutdowns.
No script callback errors occurred in the accepted captures. The focused
layout results do not certify final HUD release readiness.

## Floor-grid orientation correction

The previous script missed the legacy gunnery floor's `.down = true` draw flag.
The floor therefore sloped in the opposite direction. `tools/build_mod.py` now
exports `rc_wireframes_gunnery_floor.png` from the same preserved frame 120
master by reversing its rows, and the script preloads/draws that variant. This
retains each pixel's RGBA exactly; it does not redraw or resample the artwork.
The original export remains available for other panels. All 585 prior PNGs and
the complete ship-wireframe art set are byte-identical. Placement is unchanged
from the preceding gunnery alignment pass. Current inventory: 592 runtime files,
586 PNGs, 686 source/tool files. The 1080p and 720p checks pass; final release
remains held. See `tracking/gunnery-grid-orientation.json`.

## Earlier development baseline on 86aa967

The runtime package is unchanged: 592 files, including 586 PNGs. The new editable
diagnostic mods bring the source/tool inventory to 699. Coyote at 1080p and 720p
produces byte-identical screenshots to the preceding build. Mirage FULL GUNS,
Wolverine native-gunnery fallback and the installed review launcher pass without
script errors. The installed scene also matches the isolated 1080p capture.
Five existing nested-folder warnings come from the separate Mirage art mod;
this pass does not change that pack. The historical 1170-picture cache check
belongs to 410d0a6, and was not repeated here.

The separate font probe confirms a current upstream bug: with six sizes of one
font drawn in a frame, the first two rows are corrupted. Matching rows using
independent copies of the font are clean, and the final four rows match exactly.
The four-size atlas cache appears to overwrite resources still referenced by
earlier text. This is a source-based explanation, not an engine fix verified in
this pass. Keep the existing mod workaround. The portable reproduction, font
licence and API probe are under `source/compatibility-probes/main-86aa967`.

Further author feedback concerns gun rounds/pairing and light presentation
state; optional animation progress is listed separately from blockers. Radar
and target state are already planned upstream. No upstream message or issue
was posted, and public release is still on hold.

## Current-main baseline on 240f075

Main advanced during the first build/test pass, adding #866. The final installed
development build includes both #864 and #866, with zero local source changes.
The new probe reports nine radar contacts: four hostile, four other, and the
selected target. SABER/JACKALS shows range 70, speed 0 and shield/armour arcs in
both cockpit and separate chase view. The clock advances while native
instruments are hidden. Dense radar, range changes, large targets/subtargets
and cloaked targets still need gameplay coverage.

The 1080p and 720p HUD captures remain byte-identical to 86aa967. The installed
launcher passes too. The six-size font reproduction is unchanged, including
1474 and 2342 differing pixels in its first two rows; the other four rows match
the independent-font controls. Keep the mod workaround. The previous FULL GUNS
and Wolverine fallback checks belong to 86aa967 and were not rerun here.

All 592 runtime files, 586 PNGs and 17 approved subtargets remain unchanged. The
additional editable radar/target probe brings the source/tool inventory to 702.
The current source manifest, installed binary and screenshots are pinned in
`tracking/main-dev-baseline.json`. Earlier records remain preserved in
`tracking/main-dev-baseline-86aa967.json`. Author notes and the diagnostic bundle
are prepared locally; nothing has been posted and the public release is held.
