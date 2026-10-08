# Grendal editable source

Current scene: `grendal_worn_pbr_v2.blend`. The prior v1 scene remains available. All images are packed with portable relative resource paths. The snapshot was reopened and checked against the canonical authoring scene for geometry, normals, UVs, transforms and material assignments.

`maps/` contains the restored atlas, individual PBR maps and supporting masks. `originals/` preserves the unedited native models and decoded source texture. `authoring/` contains the exact built-in imagegen prompts and traced material regions. The restoration outputs are 1254-square; delivery maps are 4096-square. Delivery size does not imply native generated detail at that resolution.

`Original_Grendal_UV` and `Grendal_Atlas_UV_v1` preserve the original mapping; `Grendal_Delivery_UV_v1` repairs sixteen collapsed gun-flap edge faces and two stretched rear-gun barrel faces. All geometry, native normals, attachments and animation records are retained. Lower-detail UVs retain their original mappings.

The scene contains 12 native parts, 716 stored triangles and 696 visible triangles. Intact-ship hidden caps remain stored. Flight, training and the legacy shared gun variant use the same restored artwork and corresponding finest-LOD UV repairs. Loadout-prefixed textures for the loadout are byte-identical copies; its tint is engine behavior.

The local authoring review images use Blender lighting. `review/gallery_v1/` contains the actual OpenReliant publication captures. The user approved artwork revision 1.1 for beta release.

## Radiator alignment revision

`Grendal_Radiator_UV_v2` retains the earlier delivery UVs and changes only 26 collar faces on the two forward gun housings. Fin rows share a native longitudinal coordinate, giving evenly spaced cooling ribs around the housing without diagonal interpolation kinks. Their transverse mapping is divided into facet banks. Geometry, custom normals, colour and material maps remain unchanged. The prior UV layers and source scene remain available. The same 26 face repairs are applied to matching flight, training and shared-model variants, giving 44 repaired UV faces per variant including the prior pass. The user accepted this radiator revision for the current beta.
