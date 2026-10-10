# HUD 1.10 on official OpenReliant 0.9.0

The local working installation uses the official Linux x86_64 release at
`fa1c0982879fecef5dcfad03d35e9a04ca4cfae3`, without source changes or a companion engine.
The normal, development and HUD-review launchers point to it. Revision 1.10
requires 0.9.0. The author supplied the source changes in
[PR #7](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/pull/7); these were
applied to the editable templates and regenerated through the export tools.
The patch is included in this source/runtime update; this publication does not itself merge the public PR.

All four requests in [engine PR #1027](https://github.com/OpenReliant/openreliant/pull/1027)
are now used: native 120x100 logical face sizing for arbitrary film resolution,
`parts.radio_speaker`, `hud.power_ball` and `hud.measure(...).ink`. Source films
encode at 480x400, without a marker or padding. The shader and two runtime notices
are retired; historical source and licence remain under source/compatibility/hud-1.9.
The name ends inside the portrait's lower-right corner. Comms remains usable over it.

## Evidence

257 films / 10,909 frames decoded at 480x400 with opaque content. The native
FM8 palette quantizes colours; conversion is not described as lossless RGB.
Every editable art file and all 911 runtime PNGs remain unchanged. Approved
subtargets 393–409 retain their source/export hashes; Ion Cannon is 406.
All 1,184 deployed runtime files match the export manifest, and 775 nested HUD
source files were preserved. Exact engine and manifest pins are in
tracking/integration-0.9.json and tracking/integration-0.9-deployment.json.

Portrait captures pass at 1920x1080, 1280x720 and 1920x1200. The first uses
`--no-mod-effects`. Reported face bounds are 240x200 at both 1920-wide sizes
and 160x133.33 at 720p: source video resolution no longer controls HUD size.
The top grids/icons stay at the same top-edge positions on 16:10. Comms number,
period and label columns line up; native power-ball rendering is visible.
These are fixed-tick captures, not a full interactive campaign review.

The preserved state sweep at tick 220, ship 5, still shows missing portions of
several icons on official 0.9.0. Normal captures are clean, and all runs exit
normally without script warnings. #894 remains open; neither cause nor live
persistence has been established. The original artwork is intact. #1028 also
remains open for updating layouts after registration; the 24-entry cache remains.

Local logs, captures, validation inputs and rollback files live in
`.local/integration-0.9`, outside publication content. A setup attempt failed
before launching because the isolated profile lacked a game-data link; the
link was corrected before the successful captures. No engine crash occurred.

This Git snapshot contains HUD 1.10, accepted by the maintainer with extensive
playtesting still needed. Public beta.1 remains HUD 1.8. No new beta/stable release
or player ZIP is published; unfinished artwork and full release review remain.

The normal launcher also passed a 1080p screenshot check with all 23 installed mods. It loaded HUD 1.10 on the official 0.9.0 binary and exited normally without script warnings.
