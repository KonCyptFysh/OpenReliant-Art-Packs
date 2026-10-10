# Authoring history

The packed editable scene in `../saracen_worn_pbr_v1.blend` is the current approved source. Recipes record this initial pass; do not rerun them over later manual edits.

Set SARACEN_WORKSPACE to a separate writable workspace, ART_PACK_REPOSITORY to the art-pack repository and OPENRELIANT_SLTOOL to the official 0.8.1 sltool executable. Recreate `source/` from `../originals/`, `maps/` from `../maps/`, `work/reconstruction_v1/` for recipes/reports and `review/reconstruction_v1/` for authoring previews. `build_materials.py` expects the source scene created by `parse_native.py` and `build_source.py`. Blender scripts require Blender; native export uses Python, NumPy and Pillow.

Machine-specific report paths are replaced by environment placeholders. Runtime review and publication status are recorded at the pack root. No duplicated g/r loadout maps are emitted by this exporter.
