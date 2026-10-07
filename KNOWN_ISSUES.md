# Known issues and tracked work

Individual beta packs include artwork with further refinements planned. Planned emissives and accepted gaps are tracked separately from new runtime defects. Report problems through the repository's bug or artwork issue forms.

| ID | Work | Type | Milestone |
|---|---|---|---|
| [#1 — FIGHTERS-ART-01](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/1) | Review and finish the initial eight fighters | unfinished-art | Fighter texture refinement |
| [#2 — FIGHTERS-FIX-01](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/2) | Review Naginata v4 edge UVs and exhaust reconstruction | needs-review | Fighter texture refinement |
| [#3 — FIGHTERS-EMISSIVE-01](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/3) | Design emissive treatment after textures are finished | planned | Emissive update |
| [#4 — FIGHTERS-EMISSIVE-02](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/4) | Implement and test the approved emissive maps | planned | Emissive update |
| [#5 — FIGHTERS-LOD-01](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/5) | Track lower-detail models and later-campaign liveries | planned | Later artwork |
| [#6 — FIGHTERS-QA-01](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/6) | Expand gameplay and platform validation after the first beta | testing | Gameplay and platform testing |

## Beta limits

Naginata's wing-edge and exhaust interpretation still needs detailed visual acceptance. Lower-detail models, mounted weapons and some later-campaign liveries retain original treatment. Custom emissives are not included.

Format checks and bounded rendering checks cover official OpenReliant 0.7.0 on Linux, including a fresh installation without the HUD. Full campaign play, damage, ejection, loadout, Shroud cloak, distance transitions and other platforms remain unvalidated. Each published asset folder contains its own `validation.json` describing exactly what passed.

Mirage and Naginata include optional inspection missions 993 and 994, respectively. They can conflict with other mods using those same numbers.

## Patriot

Coming soon. Current glass, UV joins, gun muzzles and radiator relief are under review. It is not part of the initial eight-ship release set.
