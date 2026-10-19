> Player downloads contain only the asset runtime mod. Test scenes and diagnostic controls are development-only; see `dev/` where present.

# Basilisk - Worn Paint

Current package: **0.1.0-beta.2**, artwork **1.3**, requiring **OpenReliant 0.8.1**. Redundant loadout colour variants have been removed; the engine generates green/red views from the original PNG material set.

User-approved artwork 1.3 for OpenReliant 0.8.1, packaged as an individual beta under Coalition Fighters.

Restores the worn dark-grey and red Coalition livery, original stars and markings, smooth amber glazing and structural surface detail. The nose and forward red gun housing share a smoother reflective finish with legible panel gaps. Glass reflection masks follow the original pane contours. Machinery UV repairs, the corrected nose seam and a restrained red hull light are included.

The user approved this revision on 9 October 2026. Native model and mission checks, all 1,661 shared-corner/material checks, material-map validation, portable-source reopening and exact installed-file verification passed. The gallery now uses fresh official OpenReliant 0.8.1 captures of the current artwork, with the shared elevated three-quarter camera and consistent framing. Its optional 3D viewing copy uses reduced textures and browser lighting.

Cloaking, firing, damage, ejection and distance transitions still need broader gameplay testing. Custom emissive maps are deferred. See `KNOWN_ISSUES.md` for the beta limits.

Install the flat `mods/103-basilisk-worn-v1` folder into `game-data/mods`. The quiet mission 988 launcher is in `dev/tools/launch-basilisk-test.sh`. Current editable source: `source/basilisk_worn_pbr_v4.blend`, with packed and relative image resources. Earlier passes and original sources are preserved.
