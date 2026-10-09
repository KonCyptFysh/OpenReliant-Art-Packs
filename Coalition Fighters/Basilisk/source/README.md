# Basilisk editable source

Current scene: `basilisk_worn_pbr_v4.blend`. Earlier scenes remain as prior passes. It contains both native parts, 526 stored triangles and 526 visible intact-ship triangles. Images are packed and also saved using relative `resources/` paths; the snapshot was reopened and checked for geometry, UV, normal, transform and material parity.

`Original_Basilisk_UV` and `Basilisk_Atlas_UV_v1` preserve the original mapping. `Basilisk_Delivery_UV_v1` repairs the 18 identified machinery faces. Native continuation splits are recorded in `authoring/native_preservation.json` and reproduced by `authoring/export_native.py`; they must be retained when exporting UV changes.

`originals/` contains immutable decoded sources. `maps/` preserves the restored base colour, normal, roughness, metallic, height and region masks. The source atlas is 256-square, built-in imagegen output is 1254-square and delivery maps are 4096-square; delivery resolution does not imply generated 4K detail. The exact prompt is in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains local Blender previews from both sides, rear and underside. They are not in-game screenshots. These document the initial pass; artwork 1.3 has since been approved in game.

`authoring/nose_finish_v2/` records the local imagegen cleanup, traced nose mask, reflection tuning and two-field native-light correction. `review/nose_finish_v2/` contains Blender material views. `review/light_spill_v2/` contains isolated official-engine diagnostic comparisons with the original light, the light disabled and its restrained replacement. These comparisons leave the installed model and game settings untouched.

`authoring/nose_seam_v3/` records six front-nose UV corrections, byte-preservation checks and border sampling through five texture resolutions. `review/nose_seam_v3/` contains matched before/after Blender views of both nose edges. Texture pixels and material values are unchanged from v2.

`authoring/glass_gun_v4/` records frame-fitted reflection masks, the exact cropped gun material, the selected-face remap and native/map checks. `review/glass_gun_v4/` contains close-up authoring views of both sides and the canopy. The base colour is preserved pixel-for-pixel.

The user approved artwork 1.3 on 9 October 2026. Current publication validation is recorded at the pack root. `review/gallery_v1/` contains the actual official-engine gallery photographs. Older authoring reports describe their respective passes and retain historical review status.
