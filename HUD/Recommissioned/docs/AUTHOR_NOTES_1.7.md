# HUD portrait follow-up — not posted

I've got the HD portraits working as a drop-in mod on main 220affa now, using
FM8 replacements and a device.glsl override. The shader fits the HD picture
into the normal portrait area, so the game still runs the speech, animation,
name, opening emblem and queue. No engine fork or scripted playback timer.
Comms still overlaps the portrait, which is the behaviour I'm keeping.

It's a workable test solution, though it depends on MOD EFFECTS and the exact
renderer shader layout, and another device.glsl mod can override it. The HUD
bounds API still sees the oversized source quad. So a fixed 120x100 logical
film rectangle would still be useful and would let me drop this shader hack.
The native drawImageAs-style fix discussed earlier should retain row shake
and clipping. This isn't a claim that an engine change is required to test
HD films anymore; it would make the mod much more portable.

All 225 sequences convert/decode with their original frame counts. I've
checked the full HUD at 1080p/720p, a name label and native hit shake. Normal
films are pixel-identical with and without the shader. Full queue/interruption
QA is still outstanding. Files and reproduction notes are under
source/compatibility-probes/main-220affa/refinement-1.7; the paired shader and
FM8 files are in mods/recommissioned-hud. Prior non-portrait notes still apply.
