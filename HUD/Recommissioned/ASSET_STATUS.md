# HUD asset status

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


## Current pass, 8 October 2026

HUD 1.3 uses unmodified upstream main `30163d9` (#833/#864/#866/#868).
The expanded radar, gauges, ship/target status, damage, power, wing, objectives
and communications panels are implemented as ordinary mod script replacements.
Current checks and exact pins are in `tracking/hud-api-expansion.json`.

The export contains 924 runtime files, including 909 PNGs. All 586 previous PNGs
remain byte-identical; 45 horizontal mirror variants and 278 complete gauge-fill
states were added from preserved sources. Existing transparent-matte cleanup,
1024-pixel missile poses and legacy gunnery alignment are retained. Nine extra
font resource instances keep panel fonts within the known atlas limit.

All 17 approved subtargets 393–409, including Ion Cannon 406, retain their exact
source/export hashes and pixels. The 775 nested live authoring files are intact.
Runtime copies in the live HUD and isolated dev review match the prepared
repository. The normal launcher remains on published 0.7.0.

1080p/720p layouts, named objectives, comms, radar ranges, power changes, missile
cycling and normal Coyote flight have focused checks. FULL GUNS works, but a
Mirage scene and a synthetic state sweep show missing pieces of images/text.
The cause is unresolved, and release QA remains pending. A key-driven subtarget
attempt did not select a component; that behavior is not claimed verified.
Subtarget rendering keeps the native panel until a reliable art-class mapping
is available. Power uses a temporary allocation triangle; lights/messages and
radio portraits remain native. See [known issues](KNOWN_ISSUES.md).

Source and tool counts are recorded in the regenerated source manifest and
working-candidate record. Public release and migration to the public collection
remain held; no package or upstream message was published.

## Historical artwork audit

Checked 7 October 2026 against the installed flat HUD directory. The 21 September release checklist and large-target index agree on 17 unresolved jobs representing 19 runtime names; all 19 are still absent as custom replacements. This file records presence, not a new visual approval.

The prior custom renderer has native fallback for large schematics and subtarget icons. The active official 0.7.0 engine currently uses its native instruments; the final stock-compatible implementation must be tested for missing-art fallback. All of these artwork gaps remain visible to testers.

| Job | Runtime images | Remaining work |
|---|---|---|
| BERISCEM | beriscem | Create and promote a compound extraction map before alignment and rendering. |
| COMMSCEM | commscem | Author bespoke equipment/icon artwork rather than a ship projection. |
| CYCLSCEM | cyclscem | Refine the camera so both solar wings, central bus and dish match the reference. |
| CZADSCEM | czadscem | Restore the docked Czar missing rails and panels. |
| DREISCEM | dreiscem | Recover or identify the Dark Hat parent geometry needed for four of the eight mounts. |
| FUELSCEM | fuelscem | Author bespoke equipment/icon artwork rather than a ship projection. |
| KRESSCEM | ufelscem, yevsscem, zakoscem | Resolve shared legacy pod/rail geometry for ufelscem, yevsscem and zakoscem. The unused runtime kresscem must not ship. |
| NANNSCEM | nannscem | Create and promote a compound extraction map before alignment and rendering. |
| PACKSCEM | packscem | Author bespoke equipment/icon artwork rather than a ship projection. |
| PCORSCEM | pcorscem | Author bespoke equipment/icon artwork rather than a ship projection. |
| RESBSCEM | resbscem | Redo the rejected projection angle; recentering alone reproduced the rejected view. |
| SDROSCEM | sdroscem | Assemble a coherent arm and gripper and resolve the alternate pieces. |
| SHAVSCEM | shavscem | Compare pods and layout with the real in-game configuration before resuming this shelved image. |
| SHERSCEM | sherscem | Select the correct opposing textured face. |
| SSATSCEM | ssatscem | Reconstruct the four-part gun-satellite assembly. |
| STALSCEM | stalscem | Align the internal doors, duct, cavity and girders with the exterior shell. |
| ULYSSCEM | ulysscem | Check whether visible ULY_1 texture damage belongs to the intact in-game appearance; wreck geometry was already excluded. |

The approved index contains 49 jobs and 57 runtime names. Those approvals are historical; verify their current exported files at the release freeze. The unused runtime `kresscem` must never be added.

## Subtargets

- Frames 393–409: all 17 are finished per the maintainer. Every installed replacement matches its approved TGA source pixel-for-pixel at 528x416 RGBA, including alpha. Preserve this completed set. See the [audit](tracking/finished-subtargets.json). This is file verification; release gameplay testing remains pending.
- Frame 406 (Ion Cannon): completed and already deployed. The installed `rc_target_subtargets_frame_406.png` matches the maintainer-supplied TGA pixel-for-pixel at 528x416 RGBA. The Blender source and wireframe setup are located. This is not an open artwork or deployment task.
- Frame 410 (fuel pod): no replacement present in the inspected HUD. The engine explicitly maps this frame to `fuel_pod`; the old checklist's Ion Cannon label was wrong. Review the fuel-pod source/desired treatment separately and validate native fallback. Never rename frame 406 to 410.
- Frame 399 (satellite dish): finished, included in the confirmed set. The historical crop concern is closed following the maintainer’s confirmation and installed-pixel verification.

## Current editing and historical review

HUD 1.1 is implemented and locally verified. The repository now holds 593 selected raster masters, 34 portable Blender scenes, the current edited layout, complete engine patch and export tools. The 589 runtime files (585 PNGs, layout, mod manifest, font and notice) were rebuilt and deployed with matching SHA-256 hashes. All 17 approved subtargets retain their exact source/export hashes.

The broad transparency sweep preserves alpha and visible colours; 90 missile poses now export at 1024. Gunnery is larger, the full/synchronised bar is solid and individual firing is split, with readable labels and counts. The existing launcher and instrument-scene captures passed at 1920x1080. Those captures used the prior companion engine. The normal launcher has since switched to official 0.7.0; they do not establish full stock compatibility. See `validation.json` and `tracking/working-candidate.json` for exact hashes, prior firing-mode evidence and remaining coverage.

Fine missile detail is still limited by its neutral render/texture inputs. The final release stays on hold; engine compatibility and final gameplay QA remain open. Git LFS was unavailable at this earlier handoff; it is now installed. This editing pass has not pushed anything.

Mission-date text, prompts, notifications, world-range text and multiplayer text/scoreboard came from the old DLL project. They need OpenReliant-specific review. Old HUD Edit and F11 expectations are not assumed to apply.

## Official 0.7.0 audit and release direction

The normal launcher now runs the unmodified official release. All 589 runtime files and the original 665 source/tool files remain unchanged. Four editable compatibility probes and their preparation tool were added; the source manifest now records 679 files. All approved subtargets 393–409 retain their exact hashes/pixels. No runtime re-export or art redeployment was needed in this audit.

Stock loading and the normal launcher passed; most authored instruments remain at native geometry because this pack still needs a supported stock implementation. Script drawing/text and live fuel/countermeasures work. Native replacement/state gaps and the 128-file/64 MiB script cache limits were identified, with a separate font-base bug and tested workaround. See [findings and proposed solutions](docs/STOCK_0.7_HUD_COMPATIBILITY.md). The final package must be a drop-in mod, not an engine fork; issue drafts are local and release remains on hold.

## GitHub submission wording

Three self-contained issue drafts and reproduction attachments are ready for manual submission; see `tracking/github-issues/README.md`. This pass changes documentation/status only. Runtime and source inventories remain unchanged, and the final release remains on hold.
