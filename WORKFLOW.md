# Editing and publishing art packs

## Repository structure

Use the named category folders. Each ship or standalone pack gets its own folder, with `source/`, `mods/<stable-mod-folder>/`, `asset-manifest.json`, `source-manifest.json`, validation and package metadata. The category hierarchy is for the repository and website; runtime files stay flat within their mod folder.

Continue an active artwork pass in its established authoring workspace. At a coherent completion point, refresh the matching portable source snapshot and runtime exports in the appropriate asset folder. Preserve the originals, use packed or relative image references, and deploy those exact repository exports for local testing. Do not edit source snapshots and authoring originals independently.

## One asset at a time

1. Finish and verify the selected asset. Record source and runtime hashes and meaningful rendering checks.
2. Update its status, known work and changelog. Set packaging validation only for checks that actually passed; disclose limitations.
3. Build its player ZIP with `python3 tools/package_mod.py --root "Alliance Fighters/Coyote"` (substitute the selected folder). Generated ZIPs live in that folder's ignored `dist/` directory.
4. Stage and commit only that asset plus its required catalogue/site updates. Git LFS must be configured before staging artwork. Verify no unrelated asset has entered the commit.
5. Upload that commit and its LFS objects. Publish its own versioned pre-release and attach the verified player ZIP and checksum. Never upload the entire old combined repository history.
6. Verify the remote commit and release checksums before marking the catalogue entry `available`. Run `python3 tools/build_site.py` and publish the small catalogue update. Only then begin the next asset's upload.

Asset tags are namespaced, such as `coyote-v0.1.0-beta.1`. Never overwrite a published package or tag; use a new version for changed assets. The gallery uses each entry's verified individual release link. Unreleased or unfinished entries remain `coming-soon`, with no active download button.

## Website

`catalog.json` is the catalogue source. `tools/build_site.py` validates its entries and copies it into `docs/catalog.json`. GitHub Pages serves `docs/`; the preview library is pinned and hosted locally. Preview GLBs and screenshots are separate, reduced-size viewing copies and never replace source or runtime artwork. Verify the gallery on desktop and mobile, including navigation, 3D loading, download links and coming-soon states.

Keep machine-specific paths, local logs and temporary conversions in ignored `.local/`. Do not publish game archives, credentials or the old all-fighters ZIP. The local handoff outside this repository contains the existing authoring/deployment path map.

The public gallery identity is **KonCyptFysh / StarLancer Art Packs**. Keep OpenReliant references in compatibility information, installation instructions and credits; preserve the independent gallery header and KF icon.
