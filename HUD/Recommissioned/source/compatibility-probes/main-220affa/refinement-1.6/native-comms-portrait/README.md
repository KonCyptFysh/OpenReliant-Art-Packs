# Native comms during a radio portrait

Tested on unmodified main 220affa78729a2ce7dcb49602e4f38a4a53d5dc1,
reporting 0.8.1. Disable Recommissioned HUD and other presentation mods.
Copy mod.ini, observer.luau, mission991.dte and rc_portrait.ut into a single
flat game-data/mods/native-comms-portrait directory, then run:

    openreliant GAME_DATA --mission 991 --ship 4 --view 2 --size 1920x1080

Keep sound enabled. The fixture plays the game's own Bandit film for a
20-second silent transmission. It does not open comms itself.
Wait for the face, press C, then 1. C opens the native menu over the face;
1 selects Target and opens its taunt submenu while the portrait is playing.
The menu remains usable after the transmission. The observer only logs state.
The editable Zig fixture uses normal mission commands and the upstream SDK.

This establishes current OpenReliant behaviour; it is not a test of the
original StarLancer executable. The maintainer chose to retain the overlap
and input behaviour. No request to block comms during transmissions remains.
