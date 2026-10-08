# Sai editable source

Current scene: `sai_worn_pbr_v4.blend`, with the existing **Sai_Left_Right_UV_v2** layout. The scene's geometry, UVs, normals, materials and packed texture images are unchanged from revision 3. The added native draw-group metadata records the corrected runtime grouping at all detail levels; it is also embedded as `Sai_Native_Draw_Groups_v4.json`.

`authoring/uv_joins_v4/fix-native-uv-joins.py` splits native fan/strip continuations where their shared corners have different UV coordinates. This step is necessary after remapping individual faces: retaining the original groups across a new seam causes OpenReliant to reuse the wrong corner UVs. The exporter checks every continuation and preserves all bytes outside the grouping counters.

The verified engine references and detailed checks are in `authoring/uv_joins_v4/validation.json`. The existing `maps/kanji_v3/`, `maps/decals_v2/`, `decals/kanji_v1/` and decal placement records remain authoritative and unchanged. The red nose inscription reads 侍飛将 vertically and the black fin inscription reads 神風 horizontally on both sides.

`review/uv_joins_v4/` contains local diagnostic renders using the game's effective corner coordinates before and after the correction. These are not in-game captures. Previous source scenes, maps and authoring stages remain preserved.

The user approved revision 4.0 for Git publication; the exact approval and scope are recorded in `approval-v4.json`.
