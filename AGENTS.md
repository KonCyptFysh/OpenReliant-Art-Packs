# Publication conventions

Before publishing any ship or refreshing its gallery, follow `GALLERY_PREVIEWS.md`
and `tracking/gallery-standard.json`. Use fresh official engine captures from the
current repository runtime, the shared elevated front three-quarter camera, native
blue nebula and consistent 4:3 framing. Do not select ship previews from the user's
Pictures folder, review screenshots or Blender stills. Preserve those originals.
Run the gallery provenance checks and verify the live site after the push.

Player downloads are runtime-only. No test missions, inspection scripts/cameras, debug hotkeys/overlays or developer launchers may appear in a released asset mod or ZIP. Preserve developer fixtures in the local authoring workspace, outside the publication repository.

## Release-only repository policy — 1 November 2026

The user requires editable masters and artwork history to remain LOCAL ONLY.
This repository publishes runtime mods, release metadata, licences, documentation,
small public gallery previews, and the tools needed to package and publish them.
Never copy or commit Blender scenes, layered art, source textures, masks, editable
height fields, portrait-frame masters, original extractions, working snapshots,
review captures, test fixtures or authoring history here. Do not upload source
archives as release attachments. Preserve that material in the established local
authoring workspace and its local backups. This overrides earlier instructions
to refresh portable source snapshots in the repository.

Run `python3 tools/release_policy.py` against the staged index before committing.
Use the tracked hooks with `git config core.hooksPath .githooks`; they retain Git
LFS handling for runtime assets. CI applies the same publication boundary.
Do not use a broad add/force-add to bypass ignored local artwork. Source hashes
may be retained as provenance; source files and their inventories stay local.
