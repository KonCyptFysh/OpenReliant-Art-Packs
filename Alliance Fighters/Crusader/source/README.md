# Crusader editable source

`crusader_worn_pbr_v2.blend` is the current packed, portable scene. Revision 1 is retained. Image resources are also included under `resources/`; maps and masks are under `maps/`. Original flight, training, loadout models and textures are preserved in `originals/`.

Revision 2 changes the engine collar UVs on 24 stored faces of the finest model, preserving their positions, normals and all earlier UV layers. All other faces keep their prior UVs. Native fan/strip records for the repaired faces are delivered as independent triangles with equivalent winding; other native records and lower-detail models are unchanged from revision 1.

`recipes/audit_v2/` contains the material and UV authoring recipe, saved built-in imagegen prompt, reference attribution, native exporter and validation evidence. `review/audit_v2/` contains local Blender inspection renders, not in-game captures.

To reproduce in a separate writable copy, run `recipes/audit_v2/build_revision.py` with Blender, then `export_native.py` and `verify_maps.py` with Python, NumPy and Pillow. Set `SLTOOL` to the official executable. Revision 1 inputs and the new generated badge are included; the build never overwrites revision 1.
