# Missiles, Torpedoes and Fuel Pod

Current package: **0.1.0-beta.4**, artwork **1.2**, requiring **OpenReliant 0.8.1**. Redundant loadout colour variants have been removed; the engine generates green/red views from the original PNG material set.

**Artwork 1.2 / audit v3 — user approved and verified for Git upload.**

Seven families were revised following the second game review: Screamer pod, Raptor, Raptor pod, Jackhammer, Bandit, Imp and fuel pod. Matching loadout faces reuse the corrected flight UVs and textures. All 32 native variants and 100 part/LOD meshes remain present.

The pod mouth collars now continue over the upper corners and underneath. Raptor fin sides and closures have consistent mapping. Jackhammer has aligned cylinder markings and a bronze nose; Bandit has a coherent red fairing and silver bands; Imp's blue nose bands align. The fuel-pod top was an existing hidden cap: its visibility is restored and its UVs sample worn steel. The duplicate loadout cover triangles remain hidden.

The 18 variants of the nine approved families remain byte-identical to audit v2: Screamer, Havoc, Vagabond, Solomon missile/pod, Hawk missile/pod, Alliance torpedo and Coalition torpedo. All previous shared maps and the aligned nozzle UVs are unchanged. Two dedicated 4K pod material sets are baked from the existing worn artwork, with corresponding tangent normals and ORM maps.

[Review the 18 original in-game screenshots](review/game_audit_v3/index.html). Both sides, pod undersides and pod loadout copies were inspected in official OpenReliant 0.7.0. All models, including the seven new revisions, were approved after this review. Firing, mounted animation and actual distance transitions still require gameplay review.

Current editable source: `source/ordnance_worn_audit_v3.blend`. Packed resources and editable collar bake graphs are included. Original geometry, native/custom normals, attachment records, animation and LOD structure are preserved. All 32 native round trips pass; the portable source reproduces every delivered SHP exactly. Coarse spanning triangles retain established UVs where a new cylinder projection would collapse them.

Use the existing `launch-ordnance-test.sh` in the OpenReliant installation to select any of the 32 models. Press 7 for external orbit, arrows to rotate, Shift+Up/Down to zoom. The engine handles loadout tint. Emissives remain deferred.
