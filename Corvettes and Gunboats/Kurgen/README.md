> Player downloads contain only the asset runtime mod. Test scenes and diagnostic controls are development-only; see `dev/` where present.

# Kurgen - Worn Paint

**Approved beta 0.1.0-beta.1, revision 1.7. Requires OpenReliant 0.18.0.**

Restores the worn Coalition corvette with readable structural normals, restrained metal and roughness maps, lit bridge windows and a repaired shared turret star in its original rotation. Vents remain vents; window illumination is confined to the approved bridge sections.

Cabin lighting dims with armour loss. Substantial hits cause brief interruptions; at or below 30% hull, irregular power faults occur without further hits. Steady lighting stays below seven seconds between disruptions. Broad stern light follows thrust rapidly, while recessed nozzle disks and inner petals retain heat and cool more slowly.

Geometry, original normals, collision, native attachment positions and turret animations are retained. Front bridge UV isolation prevents window emission on the rear shoulder. The native static stern lamp is disabled so the surface effect can follow thrust. One canonical unprefixed PNG material set supports engine-generated loadout colours.

Run the included `dev/tools/launch-kurgen-test.sh` after installing the mod. F5 changes thrust, F6 applies a small hit, F7 a heavy hit, F8 repairs armour and F9 disables engines. See [LIGHTING_POC.md](LIGHTING_POC.md) for behavior and controls.

Dynamic per-barrel turret emissives and light cast onto nearby ships are deferred pending suitable official APIs. The [turret feature request](TURRET_EMISSIVES_FEATURE_REQUEST.md) is a draft, not an implemented feature or submitted issue. The current engine effect illuminates the Kurgen hull only.

The user accepted the artwork and lighting for this beta. Response tests and official 0.18.0 integration checks pass. Full campaign, damage-distance transitions and other platforms remain outside exhaustive testing. The gallery is an official-engine photograph; the optional 3D view is static and cannot reproduce the game-state lighting.

[Gallery and 3D preview](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?category=corvettes-and-gunboats&asset=kurgen) · [Beta release](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/kurgen-v0.1.0-beta.1)

Editable artwork: `source/kurgen_worn_pbr_v7.blend`. Current runtime behavior: `source/authoring/response_release_v8`.
