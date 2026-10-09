# HUD panel refinement status

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
