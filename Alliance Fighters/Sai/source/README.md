# Sai editable source

Current scene: `sai_worn_pbr_v1.blend`. All images are packed and use portable relative resource paths. The snapshot was reopened and verified against the canonical source for geometry, normals, UVs, transforms and material assignments.

`maps/` contains the restored atlases, individual PBR maps and supporting masks. `originals/` preserves the unedited native model and decoded source textures. `authoring/` contains the exact built-in imagegen prompts and traced material regions. The two generated atlases are 1254-square restoration outputs; delivery maps are 4096-square for sam_1 and 2048-square for sam_2, preserving their original relative texel scale. Delivery sizes do not imply native generated detail at that resolution.

`Original_Sai_UV` and `Sai_Atlas_UV_v1` preserve the original mapping; `Sai_Delivery_UV_v1` repairs eleven thin-fin or collapsed UV faces. All geometry, native normals, attachments and the fin-down animation are retained. Lower-detail model UVs are original.

The authoring workspace contains four Blender studio review views. `review/gallery_v1/` contains the actual OpenReliant publication captures. The user approved the installed in-game appearance on 8 October 2026.
