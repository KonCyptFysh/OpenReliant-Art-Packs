# Hades editable source

`hades_worn_pbr_v1.blend` is the approved artwork 1.0 scene. Six parts, 368 stored finest-detail triangles (364 visible), original geometry, normals and UVs. Packed images also have verified relative paths under `resources/`; the saved scene was reopened and checked.

`originals/` preserves the native model, extracted atlas and decoded part/animation data. `maps/` contains generated artwork, final 4K maps and semantic masks. `authoring/` holds recipes, prompts and validation. `review/` contains Blender authoring views, not game photography.

Native animation is preserved in the SHP export; Blender shows the static source pose. Retain the native continuation corrections during later export. Start future work from the current scene, not by rerunning old recipes over manual changes.
