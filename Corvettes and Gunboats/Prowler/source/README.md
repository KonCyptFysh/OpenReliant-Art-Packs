# Prowler editable source

Start from `prowler_worn_pbr_v2.blend`. It retains original geometry and UV layers, the active delivery UV layer, packed material maps and four mounted native turret instances for authoring review. The damage part is hidden in the intact view. Runtime still uses the native independent turret model and preserves original wreck data.

The saved source was reopened and its geometry, UVs, normals and relative packed resources verified. `originals/` preserves native models, original textures and decoded records; `maps/` preserves reconstructions, delivery maps and material masks. `authoring/` contains exact image-generation prompts, recipes and validation evidence. Recipes document authoring history and require the named environment paths; they are not a one-command portable rebuild.

`review/` contains Blender authoring views, not public gallery photography.

Revision 1.1: source/authoring/lighting_v2 records the local glass/stencil edits, native lamp change, nozzle geometry audit, runtime shaders and scripts, and functional validation. Earlier scenes and resources remain authoring history.

Revision 1.2: authoring/nozzle_surge_v3 contains the diagnosis, final shader and response logic, all-detail mask audit, response tests and official-engine integration logs. review/nozzle_surge_v3 contains functional diagnostic captures, not gallery photographs. The revision-1.1 Blender scene and texture maps remain current.

Approved revision 1.2: window-lighting refinement remains planned. Authoring/review records describe their historical review state; approval.json at the asset root records publication acceptance. Local runtime logs remain in the canonical workspace, outside the public snapshot.
