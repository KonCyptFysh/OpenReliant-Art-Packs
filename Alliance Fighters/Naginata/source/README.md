# Naginata: current editable snapshot

Asset revision 4.0; open `naginata_worn_edges_v4.blend`. Its images are packed and also use relative `resources/` paths. Continue authoring in the canonical workspace, then refresh this snapshot.

The v4 delivery UV layer gives 60 wing edge/opening triangles, 28 engine-skin triangles and four exhaust triangles full-area islands in one additional 2048-pixel atlas. It reuses existing steel/bronze wear and the existing round louvre motif. Both exhaust centres follow the original native engine attachments. This is a reconstruction choice based on the legacy motif, not proof of the original artist's exact intent. The main atlas and v3 repair maps are unchanged; the latter still supplies nose repairs.

Vertex positions, triangle topology, corner normals and all previous UV layers remain intact. The snapshot is verified against the new canonical v4 scene; its preservation flag refers to that copy, not to the intentional UV/material changes from v3. Height and region masks accompany the base/normal/roughness/metallic maps. No displacement or emissives were added.

Runtime files are in `../mods/95-naginata-worn-v1`. Both native variants, original lower LODs and damage behaviour are retained. Detailed art acceptance is pending and final release is held. Recipes preserve the algorithms; they require their documented authoring inputs and are not rollback commands.
