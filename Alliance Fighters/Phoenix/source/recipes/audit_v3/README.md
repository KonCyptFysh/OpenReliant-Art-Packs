# Phoenix triangular glazing audit

The historical build starts from the v2 scene recorded in the canonical project state and changes only cockpit UV faces 86 and 91 plus their local window artwork and material masks. It uses a triangle derived from the mesh, with glass and seal insets measured in model space. An existing quiet bronze sample replaces the superseded rounded outline. All other geometry, normals and UV faces remain unchanged.

Set PHOENIX_WORKSPACE to the canonical worn directory and OPENRELIANT_SLTOOL to the official 0.7.0 validator when exporting. `verify_native_roundtrip.py` compares exports against originals and v2. `verify_map_locality.py` checks that glass/seal stay inside the triangle and map edits remain within the window edit mask. Do not rerun historical recipes over later manual edits.
