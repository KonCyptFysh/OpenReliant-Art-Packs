# Saber editable source

Current scene: `saber_worn_pbr_v1.blend`. It contains both native parts, 612 stored triangles and 568 visible intact-ship triangles. Native hidden caps remain stored. Images are packed and also saved using relative `resources/` paths; the snapshot was reopened and checked for geometry, UV, normal, transform and material parity.

`Original_Saber_UV` and `Saber_Atlas_UV_v1` preserve the original mapping. `Saber_Delivery_UV_v1` repairs the 22 identified machinery faces. Native continuation splits are recorded in `authoring/native_preservation.json` and reproduced by `authoring/export_native.py`; they must be retained when exporting UV changes.

`originals/` contains immutable decoded sources. `maps/` preserves the restored base colour, normal, roughness, metallic, height and region masks. The source atlas is 256-square, built-in imagegen output is 1254-square and delivery maps are 4096-square; delivery resolution does not imply generated 4K detail. The exact prompt is in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains local Blender previews from both sides, rear and underside. They are not in-game screenshots. The user accepted the in-game appearance on 9 October 2026. See `../approval.json` and `../validation.json` for the scope of review.

`review/gallery_v1/` contains the actual OpenReliant 0.7.0 publication photographs. The web viewing copy uses the 568 visible intact-ship triangles and reduced textures; it omits loadout weapons and engine effects.
