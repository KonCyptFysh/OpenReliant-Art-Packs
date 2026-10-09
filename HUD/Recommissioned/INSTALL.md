# Install the beta

1. Use OpenReliant 0.8.1 with your own StarLancer game data. Close the game.
2. Extract this ZIP into the game-data folder, keeping the layout
   `mods/recommissioned-hud/mod.ini`. The individual runtime files must stay
   directly inside `recommissioned-hud`, not another nested folder.
3. Move any older Recommissioned HUD folder outside `mods`; do not load both
   an older `HUD` copy and this new `recommissioned-hud` folder.
4. Enable **Mod Effects** and restart the game. Test Instant Action first.

No engine binary, base game archives, test missions or executable installer
is included. The normal mod loader applies the artwork and scripted layout.
The distributed hud_layout.ini records the authored layout; editable scripts
and tools in the repository generate the runtime script from those placements.
The engine does not directly interpret that private layout file.

The HD portrait films and device.glsl are a pair. A different mod overriding
device.glsl needs the shader changes merged. With the shader disabled or
incompatible, portraits can become oversized. To keep this HUD with native
portraits, remove device.glsl and all 225 .fm8 files together from its folder.
Do not remove or alter the original game archives.

To uninstall, close the game and move the whole recommissioned-hud folder
outside mods. Your original game data and saves are not changed by the pack.

Tested build: unmodified main 220affa78729a2ce7dcb49602e4f38a4a53d5dc1,
reporting 0.8.1; Linux, 1080p and 720p. Other platforms and newer renderer
versions are not yet certified. For reports include engine version, screen
size, Mod Effects setting, other enabled mods and a screenshot or log.
