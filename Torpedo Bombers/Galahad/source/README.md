# Galahad editable source

`galahad_worn_pbr_v2.blend` is the current revised scene; `galahad_worn_pbr_v1.blend` preserves the first pass. Six parts and 420 finest-detail stored triangles (412 visible) are preserved. Images are packed and also saved with relative `resources/` paths; reopening passed geometry, UV, normal, transform and material-assignment checks. This scene is a static authoring pose; the native game export preserves the animations.

`Original_Galahad_UV`, `Galahad_Atlas_UV_v1` and `Galahad_Delivery_UV_v1` retain original coordinates. `authoring/native_preservation.json` records six continuation corrections across 37 native detail meshes and 1,012 faces; retain these corrections on later exports.

`originals/` contains immutable decoded source files and the RAF references. `maps/` retains both generated atlas passes, all delivered material maps and structural masks. The original atlas is 256 square, generation produced 1254-square images and delivery maps are 4096 square. Full built-in image-generation prompts and provenance are in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains Blender views, not gameplay. Artwork 1.1 is accepted for this beta; broader animation and gameplay checks remain as documented in KNOWN_ISSUES.md.

The canopy_v2 revision inserts a generated detail crop only through a protected local mask. Its exact prompt, source crop and pixel-preservation checks are in `authoring/canopy_v2/`. The rest of the atlas is unchanged. `review/canopy_v2/` contains the current cockpit views.
