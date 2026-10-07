# Editable ordnance source

Current source: `ordnance_worn_audit_v3.blend`. All 32 native variants and 100 part/LOD objects remain present; LOD0 is visible. Object transforms arrange the review board only. Mesh positions remain native.

`Original_Ordnance_UV`, `Ordnance_Delivery_UV_v1` and `Ordnance_Delivery_UV_v2` preserve prior mappings. `Ordnance_Delivery_UV_v3` is active. The two revised pods also retain source UVs, collar sample coordinates, masks and editable material graphs. Image resources are packed and have relative paths into `resources/`. Earlier scenes and native originals remain available.

Export the edited UVs and material assignments:

```sh
blender --background --python recipes/audit_v3/ordnance_export_v3.py -- ordnance_worn_audit_v3.blend native /path/to/new-runtime-output
```

The exporter verifies original positions, topology and custom normals. Edited legacy triangle groups are separated with effective winding preserved. Other native chunks, including attachments, animation and LOD records, remain byte-exact. Existing fuel top cap flags are cleared on the flight model at all three LODs and the two loadout LODs; duplicate loadout LOD0 faces 0/1 stay hidden. No geometry was added or removed.

The portable scene reproduces all 32 delivered SHPs byte-for-byte. The seven repaired families reuse their flight mapping in loadout. Native display-only doors and geometry are retained. Coarse triangles that span multiple ring segments retain their previous nondegenerate mappings where necessary.

`recipes/audit_v3/` contains the repair, collar bake, loadout reuse, exporter and validation history. Continue from the latest scene; do not blindly rerun earlier reconstruction recipes over later edits. The workspace restoration helper creates a new directory and points it to the current scene.

Authoring history recipes accept `ORDNANCE_WORKSPACE` (default: current directory). Capture and validation helpers use `OPENRELIANT`, `SLTOOL` and `ORDNANCE_REVIEW`; the snapshot helper also requires `ORDNANCE_ASSET_ROOT`. Continue from the approved scene. The history recipes may require their recorded intermediate checkpoints and are not a one-command rebuild.
