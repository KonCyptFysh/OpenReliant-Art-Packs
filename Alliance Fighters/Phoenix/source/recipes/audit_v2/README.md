# Phoenix audit v2

This pass starts from the v1 scene recorded in the canonical project state. It changes only four belly-band UV faces and the glass material within the existing pane mask. All earlier UV layers are retained. Do not rerun the historical build over later manual edits. Set PHOENIX_WORKSPACE to the canonical worn directory, with its parent project_state.json, and OPENRELIANT_SLTOOL to the official 0.7.0 validator when exporting. `verify_native_roundtrip.py` checks the three exports against originals and v1, including glass-map locality.
