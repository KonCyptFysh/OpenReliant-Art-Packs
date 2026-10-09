# Verify the current sprite and instrument refinement

Tracking ID: `HUD-FIX-01`  
Status: closed — completed and locally verified 7 October 2026  
Label: `bug`  
Milestone: 0.1.0-beta.1

HUD 1.1 is installed from the repository. Sprite cleanup covers every exported PNG;
gunnery/readouts are enlarged; full/synchronised guns show a solid bar and
individual firing shows a split bar, with live captions. All 90 missile poses
are now 1024 exports from the neutral masters and authored black halos.

## Verification

- [x] Complete installation and checks: 589 runtime hashes match the repository.
- [x] Check reticles, targeting/edge sprites, gun modes and readouts: current launcher/instrument captures and prior full/sync/interactive-individual captures use the same engine and retained asset bytes.
- [x] Record final export hashes and limitations in asset-manifest.json, validation.json and tracking/working-candidate.json.

Fine missile texture detail remains constrained by the neutral renders; this
pass removes the unnecessary 512 export reduction. This closes the local
implementation pass, not HUD-QA-01 or HUD-COMPAT-01. Final release stays on hold.
