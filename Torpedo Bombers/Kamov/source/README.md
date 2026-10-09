# Kamov editable source

Current scene: `kamov_worn_pbr_v1.blend`. All 16 native parts and 670 highest-detail triangles are retained, with original custom normals and UVs. The earlier converted scene omitted two link rods and was not used as the master.

Timeline frame 1 is stowed; frame 101 is deployed (25 fps). Preview poses reproduce the native angle, offset and mount-axis transforms. The game export retains the original animation chunks verbatim and is not rebuilt from Blender or GLTF. The latter does not carry the native deployment tracks.

Images are packed and duplicated under relative `resources/` paths. The snapshot was reopened and checked against canonical geometry, UVs, normals and materials. `originals/native_parts.json` retains every LOD and native keyframe. `Original_Kamov_UV` and `Kamov_Delivery_UV_v1` initially match. Native primitive continuation corrections must be retained on future exports.

`maps/` holds the restored base colour, normal, roughness, metallic and supporting masks. `authoring/` holds exact generation prompts, region traces and build/check scripts. `audit/` records player/AI identity and native structure. Local Blender previews in `review/reconstruction_v1/` are authoring views; `review/animation_v1/` contains bounded in-game animation-state evidence.

The packed Blender file is the portable editing entry point. The scripts in `authoring/` retain the historical build/check sequence and expect the original staged workspace layout. Set `KAMOV_WORKSPACE`, `ART_PACKS_REPOSITORY` and `OPENRELIANT_HOME` explicitly before using those recipes; they do not execute on opening the Blender file. Historical JSON checks describe their original pre-approval runs. Current approval and release validation are in the asset root. Machine-specific logs are retained outside the public package.
