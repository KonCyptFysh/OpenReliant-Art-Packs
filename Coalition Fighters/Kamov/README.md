# Kamov - Worn Paint

Approved artwork 1.0, released as beta 0.1.0-beta.1 for OpenReliant 0.7.0.

The playable Kamov in mission 25 and the AI use the same ship type (45) and exterior model, `Rus_Kamov.SHP`. One replacement covers both. The separate `kamG_frm.SHP` cockpit interior is unchanged. Engine and mission-file findings are retained in `source/audit/model-audit.json`.

Restores the grey and red Coalition livery, stars, hazard bands and smooth amber glazing. Structural normal maps follow traced panel and radiator detail; painted markings stay flat. All 16 native parts, every deployment keyframe, mount, launch point and collision record are preserved. Native strip/fan continuation repairs prevent texture-coordinate reuse across seams throughout all 1,641 faces and detail levels.

The quiet test scene carries four torpedoes. Separate stowed, deployed, repeating-cycle and manual-launch modes exercise the native mechanism. The bounded official OpenReliant 0.7.0 test verified all four torpedoes move with their carriers and return to the initial position. The user has approved the in-game appearance. Broader mission 25 gameplay remains unverified.

Use `tools/launch-kamov-test.sh` to cycle the bays. Standalone stowed/deployed launchers are also provided. See `INSTALL.md` and `KNOWN_ISSUES.md`.

[Beta release](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/kamov-v0.1.0-beta.1) · [Gallery](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?category=coalition-fighters&asset=kamov)

The gallery uses actual in-game captures of both bay states. Its reduced 3D viewing copy shows the stowed model; the downloadable native model and editable Blender scene retain deployment animation.
