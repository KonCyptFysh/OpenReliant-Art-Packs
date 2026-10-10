# Local restoration and framed glazing

`build_revision.py` opens the previous scene recorded in prior_project_state.json, retains all existing mesh data and UV layers, restores original material/chart assignments, and creates a separate delivery layer for small band-registration fixes. It uses the generated frame reference only on traced internal dividers and independently bakes structural height, normal and material masks. The original hull artwork is preserved outside the window footprints.

The authoritative saved result is ../../haidar_worn_pbr_v3.blend. Do not rerun recipes over later manual edits. Set HAIDAR_WORKSPACE, ART_PACK_REPOSITORY and OPENRELIANT_SLTOOL for the export and snapshot helpers. Validation.json, independent_checks.json, native_preservation.json and repository_snapshot.json record exact outputs. Prompt and image provenance are in imagegen_prompts.json. Rejected runtime files remain archived in the canonical workspace and installation backups.
