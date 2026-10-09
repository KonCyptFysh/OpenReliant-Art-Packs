# Run the OpenReliant HUD release checks

Tracking ID: `HUD-QA-01`

Label: `testing`  
Milestone: 0.1.0-beta.1

Test the final frozen package at 1920x1080 and additional resolutions, including missing-schematic fallback. Old DLL-specific HUD Edit and F11 tests must be translated to features that OpenReliant actually provides.

## Done when

- [ ] Fresh install, restart, disable and uninstall work.
- [ ] Test target/subtarget changes, dense radar, weapons and ammo, damage, communications, objectives, wing status and power.
- [ ] Test pause, mission relaunch, cinematic transitions and repeated alt-tab.
- [ ] Record platform, GPU, exact engine build, screenshots and unresolved gaps.

## 7 October working-candidate handoff

The HUD 1.1 repository handoff passed exact deployment hashes, the existing launcher and a 1920x1080 instrument scene. These are working-candidate checks; all final release checks above remain open. See `validation.json` for scope and evidence.

## Update, 8 October 2026 — main 30163d9

HUD 1.3 adopts #864/#866/#868 for radar, gauges, status/whole-target and the
damage, power, wing, objectives and comms panels. #832 is now closed. The current
924-file drop-in runtime is deployed for local review; no private engine patch.
Known rendering loss in selected scenes, native subtarget fallback, power-ball
fidelity and full gameplay/release QA remain open. See
`../hud-api-expansion.json` and `../../KNOWN_ISSUES.md` for current evidence.
Earlier baseline statements above are historical.
