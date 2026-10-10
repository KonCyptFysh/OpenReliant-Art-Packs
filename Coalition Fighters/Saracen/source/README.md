# Saracen editable source

`saracen_worn_pbr_v1.blend` is the current user-approved artwork 1.0 scene. Both native parts and all 616 finest-detail stored triangles are preserved. Images are packed and also saved with relative `resources/` paths; the reopened snapshot passed geometry, UV, normal, transform and material-assignment checks.

`Original_Saracen_UV` and `Saracen_Atlas_UV_v1` preserve original coordinates. `Saracen_Delivery_UV_v1` corrects four wing-edge faces around two collapsed UV triangles. All other coordinates are retained; all visible finest-detail UV triangles passed the degeneracy and distortion checks. `authoring/native_preservation.json` records native UV edits and fan/strip continuation fixes; preserve them on later exports. Native animation/keyframe data remains in the game model and decoded originals. The Blender scene is a static authoring pose.

`originals/` holds immutable decoded sources. `maps/` contains both generated atlas passes, delivered base/normal/roughness/metallic maps, height and region masks. Generation produced 1254-square images from the original 256-square atlas; delivery maps are 4096-square. Full prompts are in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains Blender authoring views. `review/gallery_v1/` contains the four actual user in-game screenshots used for publication. See the pack-root approval and validation records.
