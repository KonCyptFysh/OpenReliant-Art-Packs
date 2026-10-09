# Beta testing and known work

Current compatibility target: official OpenReliant 0.8.1. See `compatibility-0.8.json` for this package-only update. All native models/missions and the PNG loadout-colour pipeline passed non-visual checks. No new 0.8.1 gameplay or GPU-rendering capture was performed. The earlier artwork and gameplay limitations below remain applicable.

- Player/AI asset identity is verified from official engine source and native mission records. Full mission 25 gameplay, AI combat, cloaking, damage, ejection and distance transitions have not been played through with this pack.
- Stowing, deploying and cycling with four carried torpedoes passed bounded runtime verification. Manual missile firing and the post-launch closing mode need user gameplay review.
- Cockpit interior assets are preserved unchanged. Custom emissive maps are deferred. Only Linux runtime has been tested.
- The original 256-square atlas was reconstructed at 1254-square, with 4096-square delivery maps; delivery size does not imply generated native 4K detail.
