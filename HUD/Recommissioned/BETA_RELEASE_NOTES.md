First public beta of Recommissioned HUD, based on the current HUD 1.8 build.

Larger red/amber instruments, gunnery and missile displays, radar, target
components, clearer panel text and 225 HD portrait sequences. Installs as an
ordinary folder mod; no engine fork or companion executable.

**Install:** use OpenReliant 0.8.1, extract `mods/recommissioned-hud` into your
game-data folder, remove older copies of this HUD, enable **Mod Effects** and
restart. Download the player ZIP below, not GitHub's source archive.

**Known beta limits:** the HD portraits use device.glsl and conflict with
another replacement of that same shader unless merged. Disabling/overriding it
can make portraits oversized. Speaker names still have native placement and
can overlap COMMS. Some target schematics use native fallback; native power
ball reuse and the mission-29 t_grendel ammo counter remain open. Broader
campaign, combat, localization and other-platform QA remain pending.

Tested on Linux at 1080p/720p with unmodified main 220affa (reports 0.8.1).
This does not certify every newer renderer build. The cover is a composition
of actual HUD assets; gameplay screenshots are included in the gallery.

Editable source, source/runtime inventories and notices are in
`HUD/Recommissioned`. Source clones require Git LFS. No base game or engine is
included. The remaining author requests will be posted separately by the maintainer.
