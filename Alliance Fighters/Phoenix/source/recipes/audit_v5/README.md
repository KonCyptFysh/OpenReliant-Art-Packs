# Original-footprint glazing correction

This pass starts from the latest installed v3 scene, restores its two front-window UV faces from the preserved v2 layer, and traces the existing pane interiors in the v1 artwork. It updates the glass material within these outlines and restores original frame colours. All native exports exactly match the v2 models, including the accepted belly repair.

Set PHOENIX_WORKSPACE to the canonical worn directory and OPENRELIANT_SLTOOL to the official 0.7.0 validator when exporting. Run the trace before a deliberate rebuild. The build has an explicit v3 starting-scene assertion and must not be run blindly over later manual edits. Validation checks original colours outside glass, material-map locality and exact v2 model hashes.
