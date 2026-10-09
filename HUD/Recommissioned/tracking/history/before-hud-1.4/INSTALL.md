# Installation

**Draft public-release instructions. No release ZIP is attached yet.** A working candidate has been installed locally for testing; do not copy the whole preparation repository into the game.

For the current local test, only `mods/recommissioned-hud/*` maps to the existing flat `mods/HUD/*`. Keep `HUD/hud`; the normal launcher now uses official v0.7.0 with the documented HUD limitations. Do not enable a second HUD folder or HOG. See [working verification](validation.json); machine-specific deployment and backup paths are in ignored `.local/deployment.json`.

## Requirements

The final package must run on official OpenReliant without a replacement
executable. It is not ready for community installation yet. The new replacement
APIs are merged upstream but not in published 0.7.0. The current mod detects this
and keeps native instruments on that release. See the [current port](docs/UPSTREAM_HUD_PORT.md).

For local review, `launch-hud-upstream-test.sh` in the OpenReliant installation
opens mission 991 on unmodified upstream commit 30163d9, checked as main on
8 October 2026. `launch-openreliant-dev.sh` opens the normal menu on that same
development build. Both use separate settings,
saves and cache, a pinned copy of the exported HUD, and the other installed art
mods. The normal launcher is unchanged. The test binary must not be included in
the eventual player mod package. The previous development review is retained;
current installation and launcher backup paths are recorded in
`.local/api-expansion/deployment-30163d9.json`. The displayed version may still say
0.7.0 for this source-archive build; use the commit and binary hash in
`tracking/hud-api-expansion.json` to identify it.

## When the beta is released

1. Close OpenReliant. Back up the older version of this mod and any customised layout outside the game's `mods` directory.
2. Download the named `openreliant-recommissioned-hud-0.1.0-beta.1.zip` Release attachment and its SHA-256 checksum.
3. Extract the ZIP. Merge its `mods` directory into the game-data directory containing `resource.hog`. Each mod folder must have `mod.ini` and its loadable files directly inside it.
4. Remove or disable older copies first, including any equivalent HOG archive. Use one copy of each mod. Do not overlay a new version on an old folder that might leave obsolete files behind.
5. Start OpenReliant, open GAME OPTIONS then MODS, enable the mod, check its load order, and restart to apply changes. Later mods override earlier files with the same names.

The installed development HUD is currently named HUD. Disable or back up that old folder before enabling the release folder recommissioned-hud. No companion-runtime installation will be required by the intended release.

## Remove or roll back

Close the game and move this package's mod folders outside `mods`, or disable them in the mods screen and restart. Restore the backed-up mod folders to roll back. Do not remove your game files or saves. For the current local engine rollback only, the prior launcher/build are preserved and the machine-specific backup is recorded in `.local/stock-0.7/stock-installation.json`.
