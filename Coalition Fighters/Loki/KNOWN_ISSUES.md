# Beta coverage and remaining work

Current compatibility target: official OpenReliant 0.8.1. See `compatibility-0.8.json` for this package-only update. All native models/missions and the PNG loadout-colour pipeline passed non-visual checks. No new 0.8.1 gameplay or GPU-rendering capture was performed. The earlier artwork and gameplay limitations below remain applicable.

- Artwork 1.1 is user-approved, including the recessed-window revision. Fixed folded and fighting positions were visually checked in official OpenReliant 0.7.0 on Linux.
- Native geometry, hierarchy, attachments and animation bytes are preserved. The three inspection missions pass format and script checks; the complete repeating forward/reverse cycle has not been separately verified in this release pass.
- AI combat, firing, damage, distance transitions and other platforms remain untested. Cockpit interiors and custom emissive maps are outside this pass.
- Native mirrored markings and original UV repeats are retained. No lettering redesign or geometry remodel was requested.
- Original atlas: 256 square. Restored master: 1254 square. Delivery maps: 4096 square; this does not imply native generated 4K detail.
