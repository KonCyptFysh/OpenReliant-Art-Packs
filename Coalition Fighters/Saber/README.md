# Saber - Worn Paint

First worn restoration approved after in-game visual review on 9 October 2026. Source and runtime files are available in Git under Coalition Fighters; a downloadable beta and public gallery entry have not yet been published.

Restores the original silver-grey and red Coalition livery, stars, hazard markings and amber cockpit glass. The glazing has flat normals and a smooth reflective material response. Panel and radiator relief follows explicitly traced structures; painted markings do not create bump relief.

Twenty-two collapsed or stretched machinery-strip faces are repaired. Every native fan/strip join was checked across all 1,938 faces and 15 detail meshes to prevent shared UV coordinates from pulling unrelated artwork across seams. Native geometry, normals, winding, attachments, collision and animation records remain byte-identical.

Targets official OpenReliant 0.7.0. Format checks, decoded maps, portable source and installed-file hashes passed. Local Blender views were checked from both sides, rear and underside. The user reviewed the restored Saber in a quiet in-game flight and reported no immediate visual problems. Broader gameplay, ejection and distance transitions remain untested.

Use `tools/launch-saber-test.sh` for the quiet single-ship inspection. See `INSTALL.md` and `source/README.md`.
