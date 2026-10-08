# Phoenix reconstruction recipes

The packed scene is the editable deliverable. These recipes preserve the initial reconstruction and native export process; do not rebuild over later manual edits.

For a deliberate reconstruction, choose a new empty directory as `PHOENIX_WORKSPACE`. Create `source`, `maps`, `work/reconstruction_v1` and `review/reconstruction_v1` inside it. Copy `../originals/*` to its `source/`, `../maps/*` to its `maps/`, and these Python recipes to its `work/reconstruction_v1/`. Run `build_source.py` then `build_materials.py` with Blender in background mode. The latter writes the face/UV report used by `export_native.py`. Run that exporter with Python, NumPy and Pillow, setting `OPENRELIANT_SLTOOL` to the official 0.7.0 sltool executable. Its native-format and map checks must pass. `inspection.py` independently generates the original single-ship mission.

The optional `inspect_uv.py` is an authoring diagnostic and also expects the parent ship's current `project_state.json`; it is not required for reconstruction or export. Native preservation reports here describe the delivered bytes. No game visual approval is implied.
