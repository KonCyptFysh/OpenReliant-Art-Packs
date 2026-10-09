# Review status

Current compatibility target: official OpenReliant 0.8.1. See `compatibility-0.8.json` for this package-only update. All native models/missions and the PNG loadout-colour pipeline passed non-visual checks. No new 0.8.1 gameplay or GPU-rendering capture was performed. The earlier artwork and gameplay limitations below remain applicable.

- Artwork 1.3 was approved by the user on 9 October 2026. Broader gameplay checks below remain open.
- Point-light hull occlusion is not supported by official OpenReliant 0.7.0. The local light range and brightness are reduced; no global renderer or game-setting change is included.
- Eighteen machinery UV repairs, six front-nose UV corrections and the eight-face gun material remap affect the finest detail level; lower-detail UVs remain original. All detail levels retain the previous shared-corner checks. Distance transitions still need review.
- Cloaking, cockpit ejection, firing, damage and loadout behavior remain untested; their native records are preserved.
- Custom emissive maps are deferred. Other platforms are untested.
