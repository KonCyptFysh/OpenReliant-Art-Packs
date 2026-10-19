> Player downloads contain only the asset runtime mod. Test scenes and diagnostic controls are development-only; see `dev/` where present.

# Reliant - Worn Paint

**Approved beta 0.1.0-beta.13.runtime1, artwork revision 11.0. Requires OpenReliant 0.18.0.**

The ANS Reliant restoration covers the carrier exterior, bridge glazing, service galleries, radiators, engines and two shared Alliance turret models. It includes a rebuilt launch hangar, visible alternating warning flashes, and consistently scaled lining inside all six launch/landing tubes and their doors.

Rectangular windows have metal frames, scratched opaque glazing and illumination that remains readable at a distance. The ship carries a military-style ANS RELIANT stencil. Registered colour, normal, roughness, metallic and emissive maps give the hull and interior surfaces depth while retaining the native geometry and animation.

Cabin lighting responds to damage. Engine interiors heat from red toward white; the surrounding petals stay red and cool faster. Exhaust attachment positions are preserved. These effects require MOD EFFECTS; MATERIALS and PER-PIXEL LIGHTING show the authored surface response.

Choose one of the 1K, 2K or 4K downloads. All tiers use the same models and scripts. The 4K files include resampled reconstruction sources; they do not imply every detail was authored natively at 4096 pixels. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for scope and limits.

Development launchers and the corrected cycling-door landing test are retained under `dev/` and in the local review installation. They are not included in player downloads.

[Gallery](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?category=alliance-capital-ships&asset=reliant) · [Beta release](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/reliant-v0.1.0-beta.13.runtime1)

Editable sources are `source/reliant_worn_pbr_v11.blend` and `source/reliant_hangar_v11.blend`. Runtime meshes preserve original vertices, normals, attachment positions and animation tracks; documented UV/material changes and collision-preserving face reordering are retained.
