# Editing and publishing art packs

## Repository structure

This is a release-only repository. Each published asset has `mods/<stable-mod-folder>/`, an asset manifest, release/validation records, licences and user documentation. The category hierarchy is for browsing; runtime files stay flat inside their mod folder.

Editable scenes, layered artwork, masks, original extractions, portrait frames, working history and developer fixtures remain in the established local authoring workspace. Keep local backups there. Never refresh a portable `source/` snapshot here or attach a source archive to a public release. Copy only approved runtime exports and release evidence into this repository. Unpublished ship work remains local until publication is requested.

Configure `git config core.hooksPath .githooks` once per clone. Run `python3 tools/release_policy.py` before committing; it checks the staged index and rejects private source/development material. The push hook checks each published commit and its reachable history, preventing an old clone from restoring removed masters. CI repeats this boundary check without downloading LFS assets.

## One asset at a time

1. Finish and verify the selected asset. Record source and runtime hashes and meaningful rendering checks.
2. Update its status, known work and changelog. Set packaging validation only for checks that actually passed; disclose limitations.
3. Build its player ZIP with `python3 tools/package_mod.py --root "Alliance Fighters/Coyote"` (substitute the selected folder). Generated ZIPs live in that folder's ignored `dist/` directory.
4. Stage and commit only that asset plus its required catalogue/site updates. Git LFS must be configured before staging artwork. Verify no unrelated asset has entered the commit.
5. Upload that commit and its LFS objects. Publish its own versioned pre-release and attach the verified player ZIP and checksum. Never upload the entire old combined repository history.
6. Verify the remote commit and release checksums before marking the catalogue entry `available`. Run `python3 tools/build_site.py` and publish the small catalogue update. Only then begin the next asset's upload.

Asset tags are namespaced, such as `coyote-v0.1.0-beta.1`. Never overwrite a published package or tag; use a new version for changed assets. The gallery uses each entry's verified individual release link. Unreleased or unfinished entries remain `coming-soon`, with no active download button.

## Website

`catalog.json` is the catalogue source. `tools/build_site.py` validates its entries and copies it into `docs/catalog.json`. GitHub Pages serves `docs/`; the preview library is pinned and hosted locally. Preview GLBs and screenshots are separate, reduced-size public viewing copies; editable masters remain local. Verify the gallery on desktop and mobile, including navigation, 3D loading, download links and coming-soon states.

The catalogue uses schema 2: broad groups contain detailed categories, and ship liveries contain their own previews and release metadata. Keep existing asset IDs, category folders and native mod folder names stable. Put a new asset in the planned roster with `coming-soon`; put a new paint finish under the existing asset's `liveries`. The progress bar counts an asset once. See [CATALOGUE.md](CATALOGUE.md) for the format, inventory boundaries and validation commands.

For a dependent pack, add native mod-folder names to catalogue `requires` and the same combined names to `[Mod] Requires` in its packaged `mod.ini`. The build validates that match. A prerequisite must be enabled and load earlier; there is no native dependency version-range field. Planned requirements can be displayed before either pack is released, but published entries must not link to unpublished local prerequisites.

Keep machine-specific paths, local logs and temporary conversions in ignored `.local/`. Do not publish game archives, credentials or the old all-fighters ZIP. The local handoff outside this repository contains the existing authoring/deployment path map.

The public gallery identity is **KonCyptFysh / StarLancer Art Packs**. Keep OpenReliant references in compatibility information, installation instructions and credits; preserve the independent gallery header and KF icon.

Run `python3 tools/build_site.py` after editing website JavaScript or CSS too. It refreshes content-based cache versions in `docs/index.html` and the helper-module import in `docs/app.js`; commit those generated references together. This prevents returning visitors from running a cached script against changed page controls. The Node checks include page startup and both navigation levels.

## Licence metadata

Every artwork mod has `License=CC-BY-NC-SA-4.0` under `[Mod]` and a flat `license.txt` with the licence link, attribution and third-party exclusions. Preserve both during exports. The licence covers KonCyptFysh's original contributions; retain other contributors' notices. OpenReliant's external catalogue currently links to the mod's own licence file. Its releases use the `Version` in `mod.ini`, so a released metadata revision needs a new patch version. Update the manifests and record metadata-only verification when art bytes are unchanged.

Use concise public titles such as `Patriot - Worn Paint`. Keep version numbers in `Version` and release tags; keep repair details in `Description`, changelogs and known-work notes.

## OpenReliant 0.8 texture packaging

Most established fighter and ordnance packages target official OpenReliant 0.8.1. Preserve a higher per-pack minimum where required: Kurgen, Prowler and Reliant need official 0.18.0 for its scripted lighting. Ship only each unprefixed PNG texture and its normal/ORM maps. Do not duplicate these as g/r-prefixed loadout variants: the engine generates their colours. Preserve historical originals and capture-engine labels. Rebuild manifests, increment both mod and package versions, and verify new downloads before changing catalogue links. See the official [loadout texture documentation](https://github.com/OpenReliant/openreliant/blob/main/docs/guide/modding.md#textures-in-the-loadout).

## Resolution variants

For each released non-HUD asset, generate and verify 1K, 2K and 4K downloads from the approved master. See [TEXTURE_RESOLUTIONS.md](TEXTURE_RESOLUTIONS.md). A changed master invalidates its recorded variants; regenerate matching colour, normal, ORM and emissive maps together. Keep the same scripts and native mod folder across tiers. Never publish only the refreshed master and leave stale lower-resolution variants.

## Runtime-only player downloads

Player ZIPs contain only the asset mod under `mods/<stable-folder>/`. Keep licence files required by the asset inside that folder. Keep review missions, diagnostic scripts, inspection cameras, hotkeys, overlays, launchers and authoring sources in local development workspaces. Keep only release validation records in the repository. Never add them to `include_documents` or runtime manifests. Use `package_kind: asset`; a genuine mission mod must explicitly declare `package_kind: mission`. Packaging checks reject development content.

For a packaging-only cleanup, new versioned downloads supersede old bundles. Preserve original ZIPs locally, verify the replacements, switch the catalogue, and then remove superseded public ZIP/checksum attachments. Keep historical tags and release notes with a link to the clean successor.
