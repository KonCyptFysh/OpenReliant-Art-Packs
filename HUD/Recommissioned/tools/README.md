# HUD working export

Use Python 3 with the versions in `requirements.txt` (Pillow and NumPy):

```sh
python3 -m pip install -r tools/requirements.txt
python3 tools/build_mod.py
```

The exporter reads only repository sources. `hud-export-plan.json` selects the
editable masters and runtime names; `native-replacements.json` records the
native aliases. TGA masters take precedence over nearby PNG previews. Source-only
neutral renders and the unused grid stay out of the runtime folder. Native-only
sprite aliases are exported without redundant `rc_` copies.

`build_script.py` compiles `source/hud/hud_layout.ini`,
`source/scripts/layout-descriptors.json` and `source/scripts/hud.luau` into the
flat `recommissioned.luau` player script. It also reads the preserved ship
wireframes' alpha bounds so taller silhouettes stay below the gunnery heading. This is ordinary mod code using the
upstream HUD API. HUD 1.10 requires OpenReliant 0.9.0 for native film sizing and instrument parts.
See `docs/UPSTREAM_HUD_PORT.md` for the supported panels and remaining gaps.

A separate `wireframes/gunnery_floor` export reverses the rows of the preserved
frame 120 master to match the native renderer's vertical mirror. It changes no
colours or alpha and leaves the original frame export intact. The script uses
this orientation because `hud.picture` does not expose mirroring.

Every normal sprite keeps its dimensions, visible RGBA and alpha. Only RGB
under alpha zero is cleared. The 90 missile poses are recomposed at 1024 from
the selected neutral renders and numeric `pose-layout.json`; their original
512 TGA poses supply the authored black halo. The recipe must reproduce all
opaque pixels of each original pose. No game archive or original game-frame
extracts are needed for this export. It increases sampling resolution but cannot
restore detail absent from the neutral renders or their underlying textures.

The 17 approved subtargets have an additional byte-hash guard. Intentional art
changes need an explicit approval/audit update; the exporter refuses silent
changes to that set. Frame 406 is Ion Cannon; frame 410 is a separate fuel pod.

Export is staged before replacing the runtime files and refuses unknown output
files. The default output is `mods/recommissioned-hud`. It refreshes the runtime
manifest and portable export audits. A changed manifest clears previous release
hash claims and leaves release validation pending. `--output DIRECTORY` can
build a separate comparison copy without changing repository release records.

`package_mod.py` is the existing public-release builder and remains unchanged.
It must continue to reject this candidate while `release.json` is on hold.
Neither tool installs to the game, changes the launcher or publishes a release.

## Portrait additions

`build_portraits.py --missing` preserves verified exports and builds new names,
including uppercase .FM8 members. `restore_portraits.py` restores additional
whole video sequences with the established RealBasicVSR x4 model. See
`source/portraits/README.md` for checkpoint, inputs and output conventions.

## OpenReliant 0.9.0 export

All films encode directly at 480x400. The exporter no longer includes a shader.
The old shader, notices and comms bearing tools are archived under
`source/compatibility/hud-1.9` and never deployed. The runtime uses
`hud.measure(...).ink`, `parts.radio_speaker` and `hud.power_ball`.
