# HUD 1.8 — shared frames and comms text

Working candidate for unmodified main 220affa78729a2ce7dcb49602e4f38a4a53d5dc1
(reported 0.8.1). Public release is held.

## Implemented

The radio and comms use the same HUDHARD 120/121 replacements and geometry.
Native radio draws its frame before its portrait/name; comms adds only text
while radio is visible. With radio shut, comms draws the same two shapes.
Both panels therefore avoid duplicate frames over the portrait. Damage grids
share their vertical placement: centres y=47/170 at 1080p.

Comms uses separate number, period and label columns. Per-glyph visible-ink
bearings correct the native bitmap/outline font layout difference, including
"1" and the first letters T/A/B. The metric recipe and font hashes are kept in
source; changing the comms font requires regenerating its metric table.

Native layout registrations cannot be edited or removed. A bounded cache
supports up to 24 distinct window/UI-scale combinations per session; beyond
that it retains the last layout, still shared by both frames. Normal 1080p
and 720p sessions were tested. Exhaustive resizing/UI-scale sweeps are pending.

## Evidence

- At tick 150, comms-only and comms-over-portrait exposed frame regions match
  exactly: 18,000 pixels at 1080p; 7,998 at 720p.
- A 15,252-pixel region below the comms rows is identical between portrait-only
  and overlap captures. Opening comms adds no grid strokes across the face.
- Observed comms ink left edges at 1080p: numbers 39/40/40; periods 62/62/62;
  label starts 78/78/77. One-pixel curves/rasterization are within tolerance.
- Opening emblem, portrait overlap, native forced closing and return to the
  standalone comms frame were inspected. The transition observer records
  opening/open/closing/shut, with comms still open. The native shrinking frame
  remains in charge during radio closing; the comms frame returns when shut.
- All focused captures exited normally without script diagnostics. Screenshot
  test runs intentionally exit after capture; this is not a game crash.
- Earlier late mission-991 captures still contained a portrait. They are
  explicitly marked as playback captures, not closing/recovery evidence.

Evidence: `.local/refinement-1.8/evidence`; portable test sources under
`source/compatibility-probes/main-220affa/refinement-1.8`. Tests force the native
comms menu open rather than synthesizing key input. The input code is unchanged.
Full speech/queue/interruption and user gameplay review remain pending.

## Preserved and pending

Only the script, placement INI and version metadata change, plus two aliases
of existing approved grids. All prior 909 PNGs, all 225 films, all 9,353 source
portrait frames, the HD shader and approved subtargets 393–409 are unchanged.
No engine patch or upstream post is included.

The requested bottom-right speaker name still needs native text controls or
an exposed active speaker reading plus selective replacement. The current
name remains at its native position. [The expanded author request](AUTHOR_NOTES_1.8.md)
covers other native names/titles/labels too and identifies readings that already
exist. The paired 1.7 shader requirements/conflicts and wider art/QA backlog
remain; this is not final release approval.
