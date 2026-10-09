# Portrait completion capture fixture

Use a separate profile with the complete HUD 1.9 runtime and this fixture as
a later test-only mod. Copy the selected runtime film to Rel_Brdge_Off.fm8
inside this fixture (never the normal HUD) to display it using mission 990.
The native label remains Bridge Officer because this is only a film-fit test.
Use unmodified 220affa / 0.8.1, ship 2, view 2, sound enabled (silent fixture),
MOD EFFECTS enabled, and --screenshot-ticks 150. capture.py accepts --binary,
--game, --mission, --ship, --size and --sound. Create its evidence/ folder first.

Recorded samples: MCGANNNO.FM8 at 1920x1080, STINGWL.FM8 at 1280x720,
PUMATANG.FM8 at 1920x1080. These are bounded fit checks, not a campaign or
current-main compatibility playthrough. The fixture is never a runtime export.
