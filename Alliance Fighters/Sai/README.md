# Sai - Worn Paint

Artwork revision 4.0 is user-approved for Git publication. The public gallery and downloadable beta remain at the earlier release until a separate beta publication.

The body and fin atlases now have independent left/right paint areas. The revised wave retains the rising-sun motif, and the replacement red 侍飛将 and black 神風 inscriptions read normally on both sides.

The final correction removes the severe nose/canopy stretching introduced by the independent left/right texture remap. The native model still grouped triangles across the new UV seams. OpenReliant reuses shared texture coordinates inside those groups, which pulled unrelated artwork across the canopy and other surfaces. The export now splits the draw groups at incompatible UV joins at every detail level.

Relative to the preceding local revision 3, the final correction changes only 140 primitive-continuation bytes in the native model. All vertex data, face indices, individual UV coordinates, normals, winding, materials, attachments, animation, collision data and texture images are unchanged. The red **侍飛将** and black **神風** retain their approved scale, placement and readable orientation on both sides. The inspection scene retains its `fin down` command.

All 740 native faces were checked against the verified OpenReliant 0.7.0 corner-reuse rules. Local diagnostic renders reproduce the former streaks and show the corrected canopy from both sides. These are Blender diagnostic images, not in-game captures. Native-format round trips, portable source and repository-to-game file hashes passed. The user accepted the completed revision and authorized the Git update. Broader gameplay and distance-transition testing remain outstanding.

Current scene: `source/sai_worn_pbr_v4.blend`. Run `tools/launch-sai-test.sh` for the quiet inspection scene.
