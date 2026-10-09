# HUD source and release workflow

This directory is the public snapshot of HUD revision 1.8. Keep runtime files
flat in mods/recommissioned-hud. Edit templates/layout/artwork in source, run
the appropriate tools, and record matching source/runtime hashes before a
future release. source/engine-patch is historical reference, not a dependency.

Source rebuild: see tools/README.md. `build_mod.py` builds PNG/script/metadata
exports and reuses the inventoried FM8 films. `build_portraits.py` rebuilds the
films using upstream sltool and a local extracted original pilot-film set.
Tests and original game data are excluded from player downloads.

Validate runtime and approved art with tools/verify_working_copy.py. Package
with the art-pack repository's top-level tools/package_mod.py after recording
truthful, bounded validation and release authorization. Preserve previously
published packages/tags. Continue further artwork in the established authoring
workspace; do not edit parallel copies independently.
