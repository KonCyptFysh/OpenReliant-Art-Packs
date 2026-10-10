# HUD source and release workflow

This directory is the public source/runtime snapshot of HUD revision 1.10 for OpenReliant 0.9.0. Keep runtime files
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

## Complete player package

Players receive the finished HUD as a single `.hog` mod, not a source checkout
or a set of portrait conversion steps. Keep all 1,184 runtime files together.
All 257 HD films are pre-encoded; the old portrait shader is not included.

For maintainers, with Git LFS artwork present and the runtime inventory verified,
use the official OpenReliant 0.9.0 tool to produce the complete archive:

```sh
mkdir -p dist
sltool hog pack mods/recommissioned-hud dist/recommissioned-hud.hog --checksum
```

The tested archive extracted to the exact runtime hashes and loaded successfully
on official 0.9.0. Its 1080p portrait capture, with Mod Effects disabled, is
byte-identical to the folder-mod capture. See tracking/drop-in-package-1.10.json.
This packaging check does not publish a new release. The existing beta.1 ZIP and
tag remain unchanged; only the current source/runtime update is published to Git.
