# Authoring history

The packed scene in `../galahad_worn_pbr_v1.blend` is the current source. Recipes document this first pass; do not regenerate over later manual changes. Native animations and launch mounts remain in the SHP and decoded source records. The editable Blender scene is a static pose.

Machine-specific report paths use environment placeholders. A reconstruction workspace needs `source/` from `../originals/`, `maps/` from `../maps/`, and named work and review folders. Set GALAHAD_WORKSPACE, ART_PACK_REPOSITORY and OPENRELIANT_SLTOOL appropriately before adapting/running the historical recipes. Blender scripts require Blender; map/native export uses Python, NumPy and Pillow. Packaging/install recipes are records of the original local operation and need destination review before reuse.

Prompts, reference images and generation output hashes are retained. Structural masks keep the painted RAF crest flat while glass has an independent inset and metal frame. Native join corrections preserve the original per-face UV coordinates.
