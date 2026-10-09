# Allow mods to replace or configure native HUD instruments and read their live state

Submission-ready wording: [GitHub issue draft](../github-issues/01-hud-replacement-and-state.md). This file retains the fuller engineering notes.

Local draft; not posted. Type: feature request / modding API. Related: [#558](https://github.com/OpenReliant/openreliant/issues/558), [#590](https://github.com/OpenReliant/openreliant/issues/590).

## Use case

We are preparing a high-resolution HUD replacement with an authored 1920x1080 layout, independently placed instruments and larger labels. Players should install one ordinary mod folder on the official release, with no custom executable. We can adapt our export format and scripts to the supported API; we are not asking the engine to adopt our particular INI file.

Tested with the official v0.7.0 Linux x86_64 binary, commit `3b27f16779e53c03ccf177bfd2f9ec46a27bbfb7`, at 1920x1080. Native PNG/font substitution works, as do scripted `hud.picture` placement and scaled text.

## Gap

1. The native HUD is drawn before script overlays. The HUD package exposes display registration and enabling for scripts, but no supported way to replace/configure a built-in instrument. Drawing a larger custom radar leaves the original radar and its contacts underneath. Hiding native image files alone does not handle native text and geometry.
2. Scripts can read useful object state such as shields, armour, speed, fuel and countermeasures, but not the full state already used by the native HUD. Examples needed for a faithful replacement are gun group/firing mode and charge, selected missile/ammunition, HUD-selected target/subtarget, radar range/transition, and the native kill count. `object.target` is documented/implemented as the current AI order's target, so it is not an equivalent HUD selection contract.

Source evidence: [`Display.drawOverlay`](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/openreliant/main.zig#L2031-L2043), [HUD API](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L350-L453), [object fields](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/objects.zig#L67-L308), and [native gunnery state](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/game/hud/gunnery.zig#L64-L111).

## Minimal reproduction

Put any transparent `radar.png` in a flat mod folder with:

```ini
[Mod]
Name=HUD overlay check
Version=1.0
OpenReliant=0.7
[Scripts]
Player=check.luau
```

```lua
local hud = require("openreliant.hud")
return { engine_handlers = { on_frame = function()
    if not hud.shown then return end
    hud.picture(vector.create(785, 855, 0), "radar.png", vector.create(350, 221, 0))
    hud.text(vector.create(40, 280, 0), "Custom HUD overlay", {scale = 1.5})
end } }
```

Start a flight mission at 1920x1080 with the radar visible. The picture/text draw correctly and the native instrument remains. `set_display_enabled` only addresses script-registered displays; no native instrument name is documented. The absence of native control is also visible in the package declarations above.

## Requested capability

A supported native HUD customization path, either:

- Configurable native instrument position, dimensions, anchors, text scale and sprite/animation mappings, retaining the engine's existing live behavior; or
- Per-instrument replacement callbacks plus read-only snapshots of the same data the native renderer consumes.

Disabling the mod or a failed replacement should restore native drawing. Replacements should respect cockpit/view visibility, mission changes and instrument open/close behavior. These details matter more than the choice of file format/API names. Native gun-mode bars already exist; the request is to restyle/reposition them or access their state, not add that gameplay feature again.

The scripting image-cache limits are a separate concern in HUD-UPSTREAM-02. Native aliases and translating our private layout file remain our mod's responsibility.

## Concrete implementation options

These are proposals, not APIs that already exist. The earlier working renderer is preserved in this mod repository's `source/engine-patch/overlay/src/engine/game/hud/` and the complete patch is in `source/engine-patch/recommissioned-hud-1.1.patch`. It is a reference implementation against an earlier development revision, not a patch ready to merge into v0.7.0. The intent is to extract reusable upstream capabilities from it, not ask upstream to adopt a mod-specific renderer wholesale.

### Option A: configurable native instruments

Retain the native instrument state and drawing routines; add a validated layout/style description loaded through the mod filesystem. Start with named instrument roots and child elements: position, size, anchor, text height/alignment, image slot and clipping bounds. Provide a reference resolution and a uniform fit/anchor policy for other window sizes. Default/missing values retain the native layout.

Merely moving an entire panel will not reproduce this HUD: its ship, label, ammunition, mode bar, radar contact ellipse and background grids have independent geometry. Support those child rectangles and bind artwork by semantic slot. Radar needs an explicit frame list mapped to the existing zoom progression, and missile artwork needs a type/pose mapping. The working implementation already separates root/child rectangles in `recommissioned_layout.zig` and demonstrates these bindings in `recommissioned.zig`.

This is the lower-risk first option to discuss for preserving native behavior: existing gunnery bars, target selection and missile counts continue to use the same engine logic. Our exporter would produce the agreed generic layout description and native sprite aliases. It still requires engine development upstream; it is not just accepting arbitrary coordinates from the current INI.

### Option B: extend the existing script HUD API

Add a per-instrument replacement registration alongside `hud.register_display`, and pass a read-only presentation snapshot to its callback. Continue advancing native instrument state/open-close animation even when its drawing is replaced. Record a replacement's commands separately; only suppress native drawing after that callback succeeds. Disabled/erroring mods restore native rendering. Define deterministic ownership when multiple mods replace the same instrument.

Reuse the already computed native presentation data rather than reproduce gameplay logic in Luau:

| Instrument | Existing information used by the working renderer | Proposed script-facing value |
|---|---|---|
| Gunnery | `gunnery.Shown`, `gunnery.items`, the current `gun_mode` | Active groups, resolved label/ammo, full/synchronised/individual mode, visibility |
| Missiles | `missile_display.Shown.ring.entries`, each entry's `left()`, `place` and `name` | Selected type/count, carousel pose/order, resolved name |
| Radar | `State.radar_range`, `radar_rings`, existing contact calculation | Range, transition progress, filtered contacts with projection/side/selection data |
| Target | `target_display` facts and small/large/subtarget presentation data | Actual HUD-selected target/part, resolved name, range, speed and health |
| Other readouts | Existing object fields plus native readout calculations | Authoritative missing counters/energy and visibility, without duplicating state |

Snapshots should contain stable scalar values/identifiers and resolved text, not raw engine pointers. Keep target filtering, native units, special weapon behavior and mission/view rules in the engine. The renderer demonstrates that this data exists already: it consumes `gunnery.items` and missile ring entries instead of implementing weapon selection itself. A script port of its placement/drawing code would then live entirely inside the mod folder.

This option is more flexible for future HUDs. It also depends on resolving the script-image lifecycle/budget issue in HUD-UPSTREAM-02. It is an alternative to Option A, not a requirement to implement both in full.

### Incremental delivery and acceptance

Use radar, gunnery and missiles as the first supported instruments, with all others continuing to draw natively. This gives a small visible acceptance case before expanding to the whole HUD. Preserve the working renderer's 43 radar frames, enlarged independent labels and actual solid/split firing-mode behavior as comparison material.

Acceptance: a single ordinary mod folder reproduces those three instruments on an official binary at 1920x1080 and 1280x720; gun/missile/radar changes follow native state; disabling the mod or forcing a callback error restores the native instrument; mission reload and save/load do not desynchronise readings. The earlier local tests demonstrate the design, but the new upstream API still needs its own validation.

## Update, 8 October 2026 — main 30163d9

HUD 1.3 adopts #864/#866/#868 for radar, gauges, status/whole-target and the
damage, power, wing, objectives and comms panels. #832 is now closed. The current
924-file drop-in runtime is deployed for local review; no private engine patch.
Known rendering loss in selected scenes, native subtarget fallback, power-ball
fidelity and full gameplay/release QA remain open. See
`../hud-api-expansion.json` and `../../KNOWN_ISSUES.md` for current evidence.
Earlier baseline statements above are historical.
