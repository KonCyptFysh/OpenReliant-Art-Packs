# Grendel ammunition missing in instant action

Tested on unmodified main 220affa78729a2ce7dcb49602e4f38a4a53d5dc1 (reports 0.8.1).
No Recommissioned HUD is needed. Copy the files at this folder's root into
`game-data/mods/grendel-ammunition/`, then compare:

```
openreliant GAME_DATA --mission 0 --ship 2 --view 2 --size 1920x1080
openreliant GAME_DATA --mission 29 --ship 2 --view 2 --size 1920x1080
```

The supplied mission0.dte opens the gun panel for inspection. The second command
uses the stock instant-action mission, rather than selecting the menu's simulator
mode. The main-menu instant-action entry also selects mission 29 and ship 2.

The first probe prints `ship: grendel`, `rounds=3000`. The second prints
`ship: t_grendel`, with `hud.guns.rounds` nil. The native gun panel also lacks the
counter on that variant. In the modded ordinary Grendel, firing reduced it to 2982.

Likely fix: `src/engine/game/hud/gunnery.zig:121` switches on
`object.type.base()` without resolving t_* variants. Consider
`object.type.base().untwinned()` before matching Grendel/Wolverine/Reaper, with
coverage for the late variants and mod types based on them. This is a suggested
upstream change, not an engine patch included with the mod.

Expected: the real remaining rounds are available on both variants and displayed
by both native and replacement gunnery. A capacity from ship records cannot
substitute for the live counter.
