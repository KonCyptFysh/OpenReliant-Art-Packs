# Installation

HUD 1.10 requires official OpenReliant 0.9.0 or later. This Git snapshot contains
the current source and runtime; the existing beta.1 player ZIP still contains
HUD 1.8 for OpenReliant 0.8.1. No new player ZIP is published with this update.

To test 1.10, clone this repository with Git LFS installed and run `git lfs pull`.
GitHub's source-code ZIP is not the player package and may contain LFS pointers.
Copy the contents of `mods/recommissioned-hud` into one flat HUD mod folder under
your OpenReliant game-data `mods` directory. Do not copy `source` or `tools` there.

Close the game and back up any previous HUD outside the active mods directory.
Replace its flat runtime files, rather than copying over them. Remove the obsolete
`device.glsl`, `portrait-shader-notice.txt` and `OpenReliant-MPL-2.0.txt` from HUD 1.9.
All 257 FM8 films must be replaced with the new 480x400 exports. Do not mix the old
padded films with 0.9.0. Preserve any separate editable sources in your old folder.

Use only one enabled HUD copy. Enable it in GAME OPTIONS → MODS and restart.
MOD EFFECTS may be on or off; this HUD no longer overrides a shader. A StarLancer
installation configured for OpenReliant is required. The pack does not include
the game archives or an engine executable.

The maintainer accepted this working update for Git publication. Full campaigns,
localization, prolonged combat and broader playtesting remain pending. See
KNOWN_ISSUES.md for the remaining rendering and artwork limitations.
