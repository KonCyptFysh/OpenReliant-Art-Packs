# Deliver the authored HUD as a drop-in mod on official OpenReliant

Tracking ID: `HUD-COMPAT-01` — open. Public release remains on hold.

The community package must work on the official executable by installing one ordinary mod folder. Companion-engine distribution is not an accepted release path. The normal local launcher now uses verified official v0.7.0; all current art, sources and prior engine work are preserved.

Read [the compatibility audit](../../docs/STOCK_0.7_HUD_COMPATIBILITY.md) for current support, confirmed blockers, mod-side work and proposed solutions. Official 0.7.0 already supports arbitrary script pictures and scaled text; missing support is narrower than a general inability to draw custom HUDs. The old claim that a companion was the necessary distribution path is superseded.

## Local upstream drafts

- [HUD-UPSTREAM-01](HUD-UPSTREAM-01.md): configurable native instruments or script replacements with live state; includes implementation options derived from the working HUD.
- [HUD-UPSTREAM-02](HUD-UPSTREAM-02.md): renderer-safe image lifecycle/budgets and mod-side export optimizations.
- [HUD-UPSTREAM-03](HUD-UPSTREAM-03.md): custom font/HUD-base bug, likely fix and tested workaround.

No issue has been posted. Source/cache/font tests ran on the unmodified official binary. Suggested engine changes are not implemented. The prior companion patch is reference material, not the shipping solution.

## Done when

- [ ] An upstream-supported implementation preserves the intended layout and live behavior.
- [ ] Our export/script implementation produces a single ordinary mod folder.
- [ ] Official-release gameplay, alternate-resolution, fresh-install and disable/fallback checks pass.
- [ ] Final hashes and release status are approved through release preparation.

## Update, 8 October 2026 — main 30163d9

HUD 1.3 adopts #864/#866/#868 for radar, gauges, status/whole-target and the
damage, power, wing, objectives and comms panels. #832 is now closed. The current
924-file drop-in runtime is deployed for local review; no private engine patch.
Known rendering loss in selected scenes, native subtarget fallback, power-ball
fidelity and full gameplay/release QA remain open. See
`../hud-api-expansion.json` and `../../KNOWN_ISSUES.md` for current evidence.
Earlier baseline statements above are historical.
