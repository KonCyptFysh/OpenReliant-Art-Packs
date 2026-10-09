# Loki - Worn Paint

Current package: **0.1.0-beta.2**, artwork **1.1**, requiring **OpenReliant 0.8.1**. Redundant loadout colour variants have been removed; the engine generates green/red views from the original PNG material set.

Approved artwork 1.1, packaged as beta 0.1.0-beta.2 for official OpenReliant 0.8.1. The amber windows now have inward bevel normals so the panes sit below the frame; glass interiors stay flat.

Restored worn grey industrial panels, hazard bands, warnings and smooth amber glazing, with restrained structural normal maps and separate roughness/metallic maps. Painted graphics and glass interiors retain flat normals; the window surrounds slope inward.

The replacement preserves all seven native parts, their hierarchy, original geometry, UVs, normals, attachments and animation keyframes. The original lower-detail material tables name the unrelated LIMPET atlas; this model now uses its restored Loki atlas at every detail level. No shared LIMPET texture is overridden. Primitive continuation repairs stop strips/fans from reusing texture coordinates across UV seams.

Use `tools/launch-loki-test.sh` to inspect the folding mechanism in a quiet single-ship scene. Fixed folded and fighting-position modes are also provided. The native export and inspection scenes pass format checks. Both fixed poses were captured and visually checked in official OpenReliant 0.7.0 on Linux. Broader gameplay and repeated animation-cycle testing remain outside this beta’s completed checks.

Editable source and exact image-generation prompts are under `source/`. See `INSTALL.md` and `KNOWN_ISSUES.md`.

[In-game gallery](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?category=coalition-fighters&asset=loki) · [Beta release](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/loki-v0.1.0-beta.2)
