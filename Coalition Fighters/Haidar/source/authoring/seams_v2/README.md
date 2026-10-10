# Revision history

The current packed scene is `../../haidar_worn_pbr_v2.blend`. Preserve later manual edits; these scripts document this revision and should not be rerun blindly.

Set HAIDAR_WORKSPACE to a writable copy of the canonical Haidar worn workspace, ART_PACK_REPOSITORY to a review repository, and OPENRELIANT_SLTOOL to the official 0.8.1 native tool. `build_revision.py` starts from the preserved v1 scene recorded in prior_project_state.json. `refine_repair.py` reuses its validated glass maps and refines only repair texture scale/contrast and retained shoulder louvres. The final scene/maps are described by validation.json. Native export, map checks, texture-loader evidence and portable snapshot checks are separate records.

The generated glazing reference and full prompt are retained in imagegen_prompts.json. Final glass tint and optical properties are a uniform material bake. Prior runtime files remain archived in the canonical revision workspace; originals, v1 maps, scene and reports are retained in this source tree.
