# Recommissioned HUD — public beta

A drop-in StarLancer HUD overhaul for OpenReliant 0.8.1. This first beta
packages HUD revision 1.8: red wireframes, amber instruments, larger text,
missile and gunnery displays, target components, and 225 HD portrait films.
No companion engine or executable is included.

Extract the ZIP's `mods/recommissioned-hud` folder into your OpenReliant game
folder. Keep **Mod Effects enabled**, restart the game after installation,
and remove any older copy of this HUD to avoid loading it twice.
See [installation](INSTALL.md) and [known issues](KNOWN_ISSUES.md).

The HD portraits use a paired `device.glsl` shader. Other mods replacing that
same shader need a merged shader; unrelated shaders are not automatically
incompatible. With Mod Effects disabled or an incompatible/overridden shader,
the films can appear oversized. Portrait speaker names still use native
placement and can overlap the comms heading. Comms remains usable during
portraits by design.

Tested on Linux at 1920x1080 and 1280x720 using unmodified upstream main
220affa (reports 0.8.1). This is bounded beta validation, not full campaign or
cross-platform certification. The renderer workaround may need revision on
later engine builds even if the scripting API stays unchanged.

Editable artwork, script templates and export tools are preserved in `source/`
and `tools/`. Approved subtargets 393–409 are unchanged; Ion Cannon is 406.
The remaining large target schematics and component 410 use native fallback.
The [current refinement notes](docs/REFINEMENT_1.8_STATUS.md) and
[author feedback draft](docs/AUTHOR_NOTES_1.8.md) explain current limitations.
Dated records describe earlier held candidates; this beta was explicitly
approved for publication on 9 October 2026. A final stable release is pending.

Gallery cover: designed composition of the actual mod assets. The other
images are unretouched engine captures from controlled test scenes, not
representative of every mission or ship. Cover source is in `source/gallery`.

KonCyptFysh's original contributions use CC-BY-NC-SA-4.0. Original StarLancer
material, the MPL-2.0 shader and OFL font retain their respective rights/terms.
See [credits](CREDITS.md) and [licensing](LICENSING.md).
