# Karak editable source

`karak_worn_pbr_v1.blend` is the current first-pass scene, accepted for this beta round. Both native parts and all 284 finest-detail stored triangles (264 visible) are preserved. Images are packed and also saved with relative `resources/` paths; the reopened snapshot passed geometry, UV, normal, transform and material-assignment checks.

`Original_Karak_UV`, `Karak_Atlas_UV_v1` and `Karak_Delivery_UV_v1` preserve original coordinates. All visible finest-detail UV triangles passed the degeneracy and distortion checks. `authoring/native_preservation.json` records the fan/strip continuation fixes; preserve them on later exports. Native animation/keyframe data remains in the game model and decoded originals. The Blender scene is a static authoring pose.

`originals/` holds immutable decoded sources. `maps/` contains the generated atlas pass, delivered base/normal/roughness/metallic maps, height and region masks. Generation produced a 1254-square image from the original 256-square atlas; delivery maps are 4096-square. Full prompts are in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains Blender authoring views, not in-game captures. See the pack-root approval record for acceptance of this round. Native gameplay testing remains bounded as documented in KNOWN_ISSUES.md.
