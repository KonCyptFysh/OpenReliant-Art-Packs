# Loki editable source

Current scene: `loki_worn_pbr_v1.blend`. Seven native parts, 526 highest-detail triangles, original custom normals and UVs. Child parts remain attached to their native parents. Frame 1 is the initial folded pose; frame 101 is fighting position at 25 fps. Intermediate poses reproduce native angle interpolation and mount-axis transforms.

Images are packed and also stored under relative `resources/` paths. Reopening the snapshot preserves geometry, normals, UVs, materials and five checked animation poses. `originals/native_parts.json` contains every original detail level and keyframe. The game model retains original native animation bytes; Blender is not used for an animation export round trip.

`Original_Loki_UV` and `Loki_Delivery_UV_v1` initially match. Preserve repeat sampling: some original coordinates intentionally extend beyond the atlas. Both original model material slots are mapped to `orlk1_hull`; flight and loadout variants use identical maps.

`maps/` holds colour and structural material maps and masks. `authoring/imagegen_prompts.json` records the two builtin image-generation edits. The first atlas interpretation was refined after model inspection identified the amber cockpit panes. `authoring/regions.json` records traced structural regions. No albedo-noise-to-normal conversion is used. `review/reconstruction_v1/` and `review/window_recess_v1/` are Blender authoring views. `review/gallery_v1/` contains the final actual in-game photographs.

For authoring scripts set LOKI_WORKSPACE to the canonical worn workspace, ART_PACKS_REPOSITORY to this repository and OPENRELIANT_HOME to the installation. Historical build recipes are retained for reproducibility; continue from the latest scene and preserve later edits.

Artwork 1.1 continues from this same scene. Current revision evidence and recipe: `authoring/window_recess_v1/`. The initial `authoring/` records are retained as history. New normal/height maps end in `_v1_1`; window interiors sit at a negative height beneath a smooth inward bevel. Every normal texel outside the window band is preserved. The mesh, original vertex normals, UVs, materials and animation poses were checked unchanged.

Artwork 1.1 is approved for beta publication. The source manifest inventories this exact portable snapshot.
