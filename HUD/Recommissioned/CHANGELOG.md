# Changelog

## First public beta — 9 October 2026

HUD revision 1.8 is approved for this beta as-is. Artwork, script and shader
bytes match the tested candidate. Release metadata and licence notices were
added for publication. The earlier release hold below is historical; final
stable release and broader QA remain pending.

## HUD 1.8, 9 October 2026

- Comms and radio now share the same authored upper/side grids. The native
  radio owns the frame beneath the portrait and speaker name while visible;
  comms draws that exact geometry when the radio is shut. Its text stays above.
  The two new HUDHARD aliases are exact copies of existing approved grids.
- Both sides stay level: upper-grid centre y=47 and side-grid centre y=170
  at 1080p. Native SPR origins are included; the side grid shifts slightly to
  match the portrait frame. Existing panel text positions remain unchanged.
- Comms numbers, periods and labels now align by their visible ink, accounting
  for the native bitmap metrics and replacement outline-font bearings.
  The three observed rows align within one raster pixel; all periods match.
- Focused gameplay captures passed at 1080p/720p. Exposed shared-frame pixels
  match exactly, with no extra frame over the portrait. Native forced closing
  and return to the comms frame were also observed without script errors.
- Speaker-name bottom-right placement is still pending upstream support.
  The author request now covers independent position/anchor, alignment, size
  and selective replacement for all native HUD names, titles and labels,
  while identifying existing readings rather than asking for duplicates.

All prior 909 PNGs, 225 FM8 films, portrait sources and the HD shader are
unchanged. There are now 1,154 flat runtime files, including 911 PNGs.
Approved subtargets 393–409 are preserved; Ion Cannon remains frame 406.
The engine remains unmodified main 220affa / 0.8.1. The HD shader limitations
from 1.7 still apply. Public release, user playthrough and broader QA stay held.
See [current status](docs/REFINEMENT_1.8_STATUS.md) and
[author request](docs/AUTHOR_NOTES_1.8.md). Older sections below are historical.

## HUD 1.7, 9 October 2026

- Damage upper and side wireframes now align with the existing comms grids.
  At 1080p the upper grid moved up 21 pixels and the side grid/body 16 pixels;
  their centres are y=47 and y=161 respectively. The title centre is y=59.
  Comms placement and the approved artwork are unchanged.
- All 225 HD portrait sequences are ordinary flat native FM8 replacements:
  9,353 frames, matching the original names/counts and native 15 fps timing.
  Exact 480x400 editable PNG sources are preserved. FM8 conversion uses its
  native shared 256-colour palette. Runtime films total about 1.04 GB.
- A normal mod device.glsl draws the tagged films in the native 120x100
  logical picture area. The frame, speaker name, audio/queue/playback code,
  opening/closing emblems and input remain native. No engine modification or
  custom timed animation player is needed. Comms overlap remains intentional.
- Verified HD display with the full HUD at 1080p and 720p, linear/gamma-space
  colour, a native speaker label, extended playback and native hit shake.
  The original-film negative control is pixel-identical over the entire
  screenshot with and without this shader. All 9,353 exported frames decode,
  with matching dimensions/counts. A full-pack campaign launch also passed;
  that early launch capture contains no active radio portrait.
- Synthetic comms/pause input tests this pass were inconclusive. Forced-open
  comms overlap is visually correct; HUD 1.6 already tested actual C/number
  handling, and this pass changes no input behavior. Exhaustive queue,
  interruption and campaign review remain pending.

This is a working workaround on unmodified main 220affa / 0.8.1. It requires
MOD EFFECTS at startup and conflicts with another whole device.glsl override.
The renderer shader interface can change independently of the frozen mod API.
If the shader is disabled/rejected/overwritten, films draw oversized. Restore
the prior HUD backup, or remove the paired shader and all 225 replacement FM8
files together for native portraits. HUD radio bounds still describe the raw
quad. A native logical film rectangle would remove these workaround limits.

All 909 HUD PNGs and approved subtargets 393–409 (Ion Cannon 406) are unchanged.
The installed engine is unchanged. Public release remains held; unfinished
artwork, t_grendel ammunition, native power-ball reuse and wider QA stay open.

## HUD 1.6 panels, 9 October 2026

- Enlarged the objectives heading/status/body and moved their common left
  edge to x=1568 at 1080p. Body width is 260 pixels, with 20-pixel preferred
  capital height and 1.4-times line spacing. Wrapping preserves paragraph
  breaks and reduces size only when needed to fit the available area.
- Comms numbers, periods and option labels use separate columns. The first
  period is visible and labels align consistently, including two-digit rows.
- Retained the native comms-over-portrait behaviour by explicit maintainer
  choice after testing it with HUD disabled. C opens the menu during a
  transmission and 1 enters its submenu. The same interaction works with
  the finished HUD. No blocking, portrait hiding or side-by-side layout ships.
- Tested normal objectives at 1080p/720p, long objective text, comms at both
  sizes, ten synthetic options, native and modded input during playback,
  and HD whole-radio scaling. All listed runs exited normally without script
  errors. These focused checks do not replace campaign or release QA.
- Whole-radio scaling can resize an HD film, but shrinks its frame/emblem
  as well. Independent film sizing remains unresolved; a complete scripted
  replacement has not been ruled out or built. HD films remain test-only.

The engine remains unmodified main 220affa. Only the runtime player script,
layout INI and mod version change. All 909 PNGs and approved subtargets
393–409 (Ion Cannon 406) are unchanged. Sources and test fixtures are preserved.
Public release remains held. The prior t_grendel ammo, native power-ball,
unfinished artwork and broader rendering/release QA items remain open.

## HUD 1.5 refinement, 9 October 2026

- Fixed legacy HUD flashes at startup and during missile changes. Current images
  load in bounded callbacks before the same frame is presented; actual missing
  artwork still falls back to the complete native instrument. Radar warms only
  its current frame, not all 43 frames.
- Moved the missile name onto the upper wireframe, centered at y=35 at 1080p.
- Rebuilt all 90 missile poses with a continuous halo derived from the full-size
  silhouette. Preserved source renders, opaque foreground colours and geometry.
  Black, white and orange comparisons and a white-background gameplay capture
  no longer show the detached/stippled contour.
- Verified the ordinary Grendel counter decreases from 3000 to 2982. Verified
  solid/split pair indicators with Ctrl+G, gun-group cycling, and FULL GUNS.
  FULL GUNS hides the pair indicator by legacy design; changing gun type does
  not toggle the synchronized firing setting.
- Found an upstream gap: `t_grendel` in mission 29 exposes no `hud.guns.rounds`;
  the native panel also omits it. A standalone reproduction and proposed fix
  are preserved under `source/compatibility-probes/main-220affa/refinement-1.5`.
- Confirmed the installed portraits are legacy. Inventoried 9,353 updated
  480x400 frames in 225 sequences. A standard FM8 test encodes and plays them,
  but the native radio renders the higher-resolution film four times too large.
  Keep HD films out of the live pack until sizing can preserve the surrounding
  frame/text. Full original sequences remain at the inventoried authoring path.
- Tested 1,245 continuous HUD frames including 12 missile switches: no fallback
  frames or script diagnostics. Passed 1080p/720p layout and invalid-art fallback
  checks. Public release remains held; the engine stays unmodified main 220affa.

All 924 runtime files remain flat. The 90 missile PNGs, layout INI, player script
and version metadata changed; the other 819 PNGs and approved subtargets 393–409
(Ion Cannon 406) are unchanged. User gameplay review and prior art/QA work remain.

## HUD 1.4 integration, 9 October 2026

Updated the normal installation to unmodified current main `220affa`. The held
HUD now uses the stable 0.8 API, live gun rounds/pairing, approved component art,
warning flashes and device bars, hit overlays, radar/missile positions and window
progress. All 924 deployed files match; all 909 PNGs and approved 393–409 sources
are unchanged. See [integration status](docs/INTEGRATION_0.8_STATUS.md),
[author notes](docs/AUTHOR_NOTES_0.8.md), and `tracking/integration-0.8.json`.
Public release remains held. Older sections below are historical.

## Upstream 0.8.1 review, 9 October 2026

Six HUD issues are closed upstream; their fixes/readings are in official 0.8.1.
The old missing-sprite probe now looks complete, but #894 remains open pending
live review. The deployed HUD still needs the stable API naming migration and
new-field integration. Test-only copies were used; 924 runtime files and all
approved subtargets are unchanged. See `docs/UPSTREAM_0.8.1_REVIEW.md`.


## API-freeze feedback, 9 October 2026

Prepared seven individual issue drafts plus one comment for existing #509,
with tested, independently installable reproduction/observer attachments on
unmodified upstream main `57c394b5`. Font corruption, state-sweep sprite loss
and named-subtarget shutdown diagnostics reproduced; remaining API needs and
test limits are recorded in `tracking/api-freeze-feedback.json`.
Editable probes and source inventory updated. The 924-file runtime export,
deployed copies, launcher and approved subtargets 393–409 are unchanged.
Ion Cannon remains 406. Nothing posted or published; final release held.


## Unreleased

- HUD 1.3: adopt main 30163d9's expanded official HUD API for authored radar,
  gauges, player/target status, whole-ship target, damage, power, wing status,
  objectives and comms. Keep native fallback where art/state is incomplete.
- Add 45 mirrored export derivatives and 278 composed gauge states; only current
  gauge states are loaded. Stage up to one megapixel/twelve small files per frame
  and separate panel fonts. Preserve all 586 existing PNGs and approved subtargets.
- Export/deploy 924 files to the live HUD and isolated unmodified dev review.
  Normal 0.7.0 launcher and nested sources remain unchanged. Extend editable
  validation fixtures and inventory records. Keep public release held.
- Record unresolved missing sprite/text pieces in selected scenes separately
  from successful layout/control checks; do not classify it as a cache bug.

- Advance the test baseline again to main `240f075` after #866 merges during the
  same pass. Verify radar contacts and target-display fields in cockpit and chase
  view, repeat 1080p/720p and the font reproduction, and update both development
  launchers. Runtime is unchanged; the additional editable probe brings the
  source/tool inventory to 702. Other window/message readings remain #832 part 3.

- Establish unmodified upstream main `86aa967` as the local development baseline,
  including the first full-instrument API part (#864). Update the HUD test launcher
  and add a separate dev-menu launcher, with isolated saves/settings and rollback.
  Verify 1080p/720p, FULL GUNS, native-gunnery fallback, the installed launcher and
  readings with instruments hidden in chase view. Runtime remains 592 exact files.
- Reproduce the shared-font six-size corruption on current main. Preserve the
  editable font/API probes and licence, bringing the source/tool inventory to 699.
  Prepare unposted author notes on the font bug and gun/light presentation gaps.
  Preserve approved artwork, the normal 0.7.0 launcher and the release hold.

- Fix the gunnery floor grid's reversed perspective. Export the native renderer's
  vertical-mirror orientation as one additional PNG, preserving all 585 existing
  PNGs and every editable art master. The ordinary mod now contains 592 files.

- Correct gunnery to the legacy arrangement: smaller left-aligned weapon name
  above the panel, original solid/split pairing sprites underneath, and no extra
  mode caption. FULL GUNS and Nova Cannon omit the pairing bar as native code does.
  Keep the enlarged wireframe clear of the heading, including tall silhouettes.
  Preserve every PNG; only the generated script and layout change in the mod.

- HUD 1.2: implement ordinary player-script replacements for readouts, supported
  gunnery and missiles using merged upstream #833. Compile all layout rectangles
  from the preserved INI; all 90 match the previous layout helper.
- Stage image loading to avoid cold-load script timeouts. Keep separate font
  instances for native text, weapon labels and counters to avoid the four-size
  atlas collision. Preserve all 585 existing PNGs without changes.
- Verify 1080p/720p, FULL GUNS, native ammunition fallback, missing-art fallback,
  released 0.7.0 fallback and 1170 image-cache draws on unmodified upstream.
- Deploy 591 exact runtime files, preserve 775 nested authoring files and all 17
  approved subtargets, and add an isolated upstream review launcher. Keep the
  normal official 0.7.0 launcher unchanged and the public release on hold.
- Record the user's #793/#794 submissions and upstream merges #833/#831.
  Full instrument data remains #832; no new upstream issue or comment posted.

- Earlier: prepare three submission-ready GitHub issues in plain language, with solution options and exact-tested reproduction ZIPs. No submission or runtime/source change occurred during that preparation pass.

- Set community distribution to one ordinary mod folder on official OpenReliant; discontinue companion-engine distribution as a proposed path.
- Install and verify official v0.7.0 locally with rollback preserved. Keep all 589 HUD runtime files and approved subtargets unchanged; document current native-layout limitations.
- Verify official scripted image/text support and reproduce native replacement/state gaps, 128-file/64 MiB cache limits and a custom-font HUD-base bug. Preserve four editable diagnostic cases and update source inventory to 679 files.
- Prepare three local upstream drafts with concrete solution options grounded in the earlier working HUD. No upstream issue, repository upload or public release created.

- Complete HUD 1.1 sprite-edge cleanup, larger gunnery and instrument text, live solid/split gun-mode bars and captions, and 90 missile poses exported at 1024.
- Preserve 593 selected raster masters, 34 Blender scenes with packed resources, the current layout, portable export tools and the full HUD engine delta against upstream 4150676.
- Export and deploy 589 matching runtime files; back up and remove 38 confirmed redundant/source-only flat files. Preserve all 775 nested authoring files and all approved 393–409 subtarget hashes.
- Verify the deployed candidate through the unchanged launcher and an instrument scene at 1920x1080. At that earlier handoff, keep the final release on hold and leave engine upgrades to release preparation; the later user-authorized official upgrade is recorded above. No Git staging, commit or upload.

- Record all 17 subtargets (393–409) as finished and pixel-verified against their installed copies; close the historical frame 399 crop review.

- Correct subtarget identity: Ion Cannon is completed/deployed frame 406; frame 410 is the fuel pod.
- Document working-source snapshots, repository exports and exact local testing workflow.

- Prepare the separate Recommissioned HUD repository and first public beta plan.
- Track known artwork gaps and release validation work.
- Add bug and artwork report forms, issue drafts and a reproducible package builder.

No player release has been built or published from this repository. `0.1.0-beta.1` is reserved for the first tested package; existing individual asset-version numbers remain provenance.
