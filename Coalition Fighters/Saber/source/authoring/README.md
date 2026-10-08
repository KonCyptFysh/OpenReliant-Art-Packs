# Authoring history

The packed, editable scene in `../saber_worn_pbr_v1.blend` is the current approved source. The original build recipes are retained as history; do not rerun them over an edited scene. Their original machine-local copies remain in the authoring workspace.

To adapt these recipes, set `SABER_WORKSPACE` to a separate writable working directory, `ART_PACK_REPOSITORY` to this repository and `OPENRELIANT_SLTOOL` to the official 0.7.0 sltool executable. Recreate the original working layout there: `source/` from `../originals/`, `maps/` from `../maps/`, `work/reconstruction_v1/` for these recipes and reports, and `review/reconstruction_v1/` for authoring previews. Blender scripts require Blender; the native exporter also uses NumPy and Pillow.

`${SABER_WORKSPACE}` in historical reports replaces the private authoring path. These reports describe the original pass. Machine-local synchronization helpers and launch logs are intentionally excluded from the Git snapshot. Current approval and validation are recorded at the pack root.
