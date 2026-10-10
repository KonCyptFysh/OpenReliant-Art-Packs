# Editable source snapshots

The HUD 1.10 source/runtime snapshot is captured here. The script templates and export
recipes are maintained in this repository. Artwork masters and external
authoring originals are preserved. Refresh an edited artwork snapshot deliberately,
export in the repository, then deploy those exact files to the existing HUD mod.
Do not edit two source copies independently.

- `hud/`: 593 selected raster masters, the current edited `hud_layout.ini`, and
  portable missile-pose metadata. TGA masters are used ahead of PNG previews.
- `hud/target/subtargets/`: the 17 approved 393–409 TGAs, unchanged. `scenes/`
  contains their 34 selected base and wireframe Blender scenes. The snapshot
  packs reference images and uses relative output/resource paths; authoring
  scenes outside this repository are untouched. Re-exporting those scenes is
  not automatic approval to change the accepted TGA framing or selection corners.
- `scripts/`: editable HUD templates and pinned vanilla ship-art mappings.
- `runtime-meta/`: current mod identity and separate font instances, with the license notice.
- `compatibility-probes/`: isolated developer tests; excluded from player runtime.
- `engine-patch/`: historical reference only, not required by the ordinary mod.
  Pinned upstream revision, complete HUD delta, final source
  additions and tests, license and rebuild procedure. No binaries or caches.

`source-manifest.json` inventories selected source and export-tool files by
repository-relative path and SHA-256, including original source hashes for
traceability where snapshots were made portable. Runtime files have their own
root `asset-manifest.json`. Machine-specific origins and test evidence are
kept under ignored `.local/`.

Git LFS is available. Binary artwork is tracked with Git LFS. Clone with LFS enabled to obtain the
editable images and films; GitHub source ZIPs may contain pointers.
