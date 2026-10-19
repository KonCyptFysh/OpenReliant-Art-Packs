> Player downloads contain only the asset runtime mod. Test scenes and diagnostic controls are development-only; see `dev/` where present.

# Azan - Worn Paint

User-approved worn artwork **1.0**, packaged as **0.1.0-beta.1** for **OpenReliant 0.8.1**, under Coalition Fighters.

Restores the original silver-grey panels, red star and warning triangles, hazard stripes and amber glazing. Structural normal, roughness and metallic maps add recessed window edges, bounded radiator relief and panel seams. Glass interiors have flat normals and a smooth reflective response. One unprefixed PNG material set is shared with engine-generated loadout colours.

Four stretched or collapsed inner tail-edge triangles receive metric planar UVs. Native fan/strip continuity was checked across all 1,670 faces in 18 detail meshes; 107 continuation counts were corrected to retain the intended UVs. Geometry, normals, winding, parts, attachments and animation records remain unchanged. The Blender source is a static authoring pose; the native game export preserves the original animation.

The user accepted the first pass without revisions. Official 0.8.1 native round-trip and texture-loader checks passed, along with portable source and installed-file checks. The gallery now uses fresh official OpenReliant 0.8.1 captures of the current artwork, with the shared elevated three-quarter camera and consistent framing. Broader gameplay, damage and distance transitions remain outside the completed review.

[In-game gallery](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?category=coalition-fighters&asset=azan) · [Beta release](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/azan-v0.1.0-beta.1)

Use `dev/tools/launch-azan-test.sh` for the quiet single-ship inspection. See INSTALL.md and source/README.md.
