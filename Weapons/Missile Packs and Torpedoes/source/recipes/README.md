# Source recipes

Use `audit_v2/ordnance_export_v2.py` with Blender to export the current portable scene. Its neighbouring `ordnance_native.py` supplies the native reader. The v1 exporter and initial build/material scripts are retained as history.

`audit_v2/ordnance_repair_v2.py`, `ordnance_wrap_v2.py` and `ordnance_nozzle_v2.py` document this audit's source edits and editable Blender bakes. They were applied to the then-current canonical v1; do not run them over subsequent hand edits. The JSON records retain affected faces, flight/loadout reuse, native checks and map checks.

`restore_authoring_workspace.py` creates a new independent working copy, including both native scenes, all packed-resource files and immutable native originals. UV and material edits should continue from the v2 scene; geometry edits require a separately reviewed exporter.
