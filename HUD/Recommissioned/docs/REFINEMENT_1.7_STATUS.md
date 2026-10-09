# HUD alignment and HD portraits

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

## Private manual review shell

`<OpenReliant-install>/launch-hud-review.sh` offers HD portrait inspection, sandbox flight, the game menu for Instant Action/campaign, and a native HUD comparison. Profiles and saves are isolated under `Games/OpenReliant/reviews/hud-1.7`. The HUD profile is extracted from the exact private review ZIP using its distributable folder name. The shell uses no screenshot exit in normal use. Editable test sources are under `source/test-fixtures/hud-1.7-review`; results are recorded in `tracking/review-shell-1.7.json`. This adds no runtime mod changes and does not lift the release hold.
