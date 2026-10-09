# Shared-frame and comms-column reproduction

Use the complete HUD 1.8 mod on unmodified main 220affa / 0.8.1. Copy this
fixture's mod.ini, observer.luau, mission990–993.dte and rc_review.ut into a
separate flat fixture mod inside an isolated game profile. Do not install
these mission overrides into the normal game. Run ship 2, view 2 with sound
on; the fixture speech is silent.

- Mission 990: native Bridge Officer portrait, no forced comms menu.
- Mission 991: same scene with native comms held open. Tick 150 shows overlap.
- Mission 992: comms only. Compare frames against 991 at tick 150, at 1080p/720p.
- Tick 80 in mission 991 shows the opening emblem.
- Mission 993: same overlap, then native CloseInstrument(0) after Wait(3).
  Tick 450 shows closing; tick 600 shows radio shut and comms frame restored.
  The observer records opening/open/closing/shut with comms still open.

Capture ticks are simulation steps, not movie frames or seconds. Earlier
2120/2200 captures of mission 991 still showed a portrait and are not evidence
of closing. Native speech completion and all queue/interruption paths have
not been exhaustively tested in this pass.

The mission sources use the native assembler. capture.py has a local default
engine path; pass --binary and --game for another installation. The fixtures
are source/QA material only and are absent from the distributable runtime.
No synthetic input, speaker-name substitution or engine changes are used.
The native name stays at its original position pending text-component controls.
