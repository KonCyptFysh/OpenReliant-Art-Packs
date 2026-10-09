# Saber - Worn Paint

Current package: **0.1.0-beta.2**, artwork **1.0**, requiring **OpenReliant 0.8.1**. Redundant loadout colour variants have been removed; the engine generates green/red views from the original PNG material set.

User-approved worn restoration for OpenReliant 0.8.1, packaged as an individual beta under Coalition Fighters. Artwork 1.0 passed the user's in-game visual review on 9 October 2026.

Restores the original silver-grey and red Coalition livery, stars, hazard markings and amber cockpit glass. The glazing has flat normals and a smooth reflective material response. Panel and radiator relief follows explicitly traced structures; painted markings do not create bump relief.

Twenty-two collapsed or stretched machinery-strip faces are repaired. Every native fan/strip join was checked across all 1,938 faces and 15 detail meshes to prevent shared UV coordinates from pulling unrelated artwork across seams. Native geometry, normals, winding, attachments, collision and animation records remain byte-identical.

The original artwork review used official OpenReliant 0.7.0. Format checks, decoded maps, portable source and installed-file hashes passed. Local Blender views were checked from both sides, rear and underside. The user reviewed the restored Saber in a quiet in-game flight and reported no immediate visual problems. Broader gameplay, ejection and distance transitions remain untested.

Use `tools/launch-saber-test.sh` for the quiet single-ship inspection. See `INSTALL.md` and `source/README.md`.

The gallery uses actual in-game overview and rear photographs. Its optional 3D hull preview uses reduced textures and browser lighting.
