# Kurgen editable source

Continue from **kurgen_worn_pbr_v7.blend**. It contains the corrected window scope and restored vents. Earlier v1 and v2 scenes are historical snapshots; do not rebuild over the latest scene from an earlier recipe.

Geometry, custom mesh normals, mounts and original UV layers are preserved. The added Kurgen_Front_Bridge_UV_v3 layer maps only four finest-detail front faces to a 512-square crop. Native exports apply matching isolation to the lower-detail front faces, plus a separate small crop for four coarsened side faces. The Blender scene displays the finest-detail model; the distance-model crop is retained under maps/window_scope_v3 with its native mapping evidence.

maps/window_scope_v3 holds current hull, bridge and bridge-LOD maps and semantic masks. authoring/window_scope_v3 records exact selected faces, native preservation, emission-surface placement, validation and restoration recipes. These document the sequence rather than forming a one-command portable rebuild. Start future work from the latest scene and project state. The prior generated window art is reused only in the explicitly approved sections; no new artwork generation was used for this correction.

Packed images and relative resources were reopened and verified. review/window_scope_v3 contains authoring views, not public gallery photos. Original models, atlases and earlier revisions remain preserved.

## Runtime lighting PoC 1.3

The accepted v3 Blender scene and all bitmap maps remain current. `authoring/dynamic_lighting_v4` holds the runtime scripts, shader, native-light patch evidence, tests and preserved v3 model. See the package LIGHTING_POC.md.

## Runtime petal revision 1.4

`authoring/nozzle_petals_v5` is the current complete runtime source set and includes the petal-mask audit. The v3 material scene remains current; v4 response scripts are unchanged.

## Runtime response revision 1.5

`authoring/power_response_v6` is the current runtime source set, with response tests, petal-mask audit and instrumented integration-test source. The v3 material scene remains current; earlier runtime revisions remain archived.

## Turret star revision 1.6

The current packed v7 scene replaces only the shared turret basecolour image. `maps/turret_star_v7` holds the repaired atlas; `authoring/turret_star_v7` holds its original-orientation evidence, geometric guide, local mask, built-in image-generation prompt, and validation. The v3 scene remains an immutable earlier material snapshot. `authoring/power_response_v6` still provides the unchanged current cabin and engine runtime behavior. The turret effects request is a draft, not an implemented feature.

## Approved beta revision 1.7

Continue artwork from the packed v7 scene. `authoring/response_release_v8` is the current runtime behavior source: shorter critical-health fault intervals, with unchanged heat and material behavior. The prior v6 response remains archived.
