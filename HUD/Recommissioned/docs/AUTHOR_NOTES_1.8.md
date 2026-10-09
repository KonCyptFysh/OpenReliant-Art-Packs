# Independent HUD text placement — draft, not posted

I've got the comms/portrait wireframes sharing the same placement now, with
one frame behind the portrait and the comms text. That's handled in the mod.

The next thing is moving the speaker's name to the bottom right of the
portrait, right-aligned. But that's probably not the only title I'll want to
move, so can we make the names, titles and labels across the native HUD
independently adjustable while we're doing it?

Being able to set each text item's position or anchor, left/centre/right
alignment and text size would cover it. Ideally I could anchor a name to the
bottom-right of its portrait or panel, so short and long names end in the
same place and it still behaves properly at different resolutions. It would
also help to hide/replace just that text without replacing its whole panel.
The text should stay above its panel wireframe/background.

That includes the portrait speaker name, target and pilot names, subtarget
labels, gun and firing-mode labels, missile names, comms titles/options,
objective headings/status/body, and the damage/power/wing panel headings and
labels. Where a panel changes its text, I'd want the actual text it's showing
exposed too, rather than trying to reconstruct it from unrelated game state.

A lot of those readings are already exposed, and our scripted panels already
move their own text. I'm not asking for those to be added again. The gap is
independent control over the text that remains inside a native instrument,
plus any displayed text that still has no reading — the active portrait
speaker is the concrete example I've hit.

Either native component layout controls, or separately replaceable text
components with their current text exposed, would work. For the radio it needs
to follow the line actually playing, including queued, interrupted and
mission-scripted lines. `radio_say` is the request/queue hook, so the last
requested film isn't a reliable substitute for the current speaker.

One related detail: `hud.measure` gives the legacy advance widths, while the
outline font's visible ink can start elsewhere. Actual ink bounds alongside
advance measurements would make precise left/right/bottom text alignment
much easier. I've corrected our comms columns in the mod, but that required
measuring the original bitmap layout against our outline font.

The fixed logical portrait rectangle from the earlier notes would still let
me remove the HD shader workaround. That's separate from these text controls.

## What is already available on the tested build

| Text or panel | Current reading / mod handling |
| --- | --- |
| Active portrait speaker name | No current-name reading; fixed native placement. |
| Target type, pilot and subtarget | `hud.target_display.name`, `.pilot`, `.subtarget`; our replacement draws them. |
| Gun name and firing mode | `hud.guns` gives gun/group/all/paired/synchronized; our replacement supplies labels. |
| Missile name and count | `hud.missiles` gives armed type/count; our replacement draws them. |
| Objectives and comms choices | `hud.objectives` and `hud.comms`; replacement headings and rows are already editable. |
| Damage, power and wing panel labels | `hud.damage`, `hud.power`, `hud.wingmen`; replacement labels/headings are editable. |
| Messages, subtitles, view/caption and prompts | Existing HUD readings; do not duplicate these as new requests. |

This is a request for consistent native text-component controls, not a claim
that all of the above are absent from the existing scripting API. Proposed
component-level controls here are suggestions, not names of shipped APIs.

## Checked source

Unmodified OpenReliant main 220affa78729a2ce7dcb49602e4f38a4a53d5dc1:

- `src/engine/game/hud/radio.zig`: `name_at = {1,2}` and
  `canvas.string(name, name_at, .left)`; portrait at `{13,19}`.
- `src/scripting/instruments.zig`: `HudLayout` exposes whole-instrument
  `offset` and `scale`; no active radio-name reading. The other HUD readings
  above are already exposed here.
- `src/engine/hooks.zig`: `radio_say` exposes speech, film and mode; the
  `_line` holding the actual name is private to the engine.
- `src/engine/game/radio.zig`: `sayNow` sets the active name, whereas queued
  requests may wait, expire or be interrupted before they are shown.
- `src/engine/game/hud/outline.zig`: outline glyphs are centred on bitmap ink;
  `src/scripting/drawing.zig` measures the bitmap advance layout.

No engine edit, guessed name, suppressed speaker label or upstream post is
included in HUD 1.8. The bottom-right speaker-name placement remains pending.
