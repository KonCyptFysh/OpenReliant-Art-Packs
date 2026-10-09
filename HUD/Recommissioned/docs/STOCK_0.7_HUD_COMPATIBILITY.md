# HUD compatibility with official OpenReliant 0.7.0

Checked 7 October 2026 against the official Linux x86_64 release, tag `v0.7.0`, commit `3b27f16779e53c03ccf177bfd2f9ec46a27bbfb7`. The normal local launcher now uses that unmodified release. The prior custom build is retained for rollback, not selected for community distribution.

**Release requirement:** a player downloads the mod, extracts it into the normal mods directory and enables it on official OpenReliant. No replacement executable, compiler or separate engine installation. The public release remains on hold until this works with the intended design.

## What the companion actually was

The companion was a modified OpenReliant executable, not a plugin loaded by the official game. It added a reader for our authoring tool's `hud_layout.ini`, resolved the pack's `rc_*` filenames, and drew the instruments using internal game state. It fitted the 1920x1080 layout to the window, controlled individual image/text rectangles, mapped the authored radar and missile animation frames, and replaced parts of the built-in HUD drawing. Its transparency handling also cleared RGB under fully transparent pixels before filtering.

That demonstrated the intended artwork and layout, but it introduced an engine-maintenance dependency. Preserving its source is useful as a design reference; shipping or continually porting that executable is no longer the release plan. The new 0.7.0 companion compilation was stopped and no new companion was installed.

## What stock 0.7.0 already supports

| Requirement | Official support | Implication for this mod |
|---|---|---|
| Drop-in folder or HOG | Yes; flat files with `mod.ini` | Keep the ordinary packaging workflow. |
| Higher-resolution HUD art and alpha | Yes, using native shape names such as `HUDHARD_215.png` | Native replacements keep the original drawing rectangle. File resolution does not choose screen placement. |
| Arbitrary image position and size | Yes, through `hud.picture` in a player script | A script can consume our layout or generated layout data; a built-in reader for our exact INI is not intrinsically required. |
| Larger custom text | Yes, scripts provide text scale and font selection | The inability to resize every existing native label is a different problem from drawing new text. |
| HUD font replacement | Yes, `BLUFONT.ttf` works | Keep the existing font and licence. A separate scripted custom-font bug has a workaround below. |
| Some live readings | Yes; the player object exposes speed, throttle, afterburner fuel, countermeasures, armour and shields | Do not ask upstream to add these again. |
| Native gun-mode bars and captions | Already part of the built-in gunnery display | Their earlier omission was in our custom renderer, not a missing stock feature. |

The scripting probe successfully drew our 350x221 radar image and larger text, including live fuel and countermeasures, using the official executable. The original radar remained underneath. Existing scripting support is therefore a useful foundation, but the current pack has no player script implementing a HUD replacement.

Primary references: [native sprite replacement rules](https://github.com/OpenReliant/openreliant/blob/v0.7.0/docs/guide/modding.md#shapes), [scripted drawing and HUD displays](https://github.com/OpenReliant/openreliant/blob/v0.7.0/docs/guide/scripting.md#drawing), and [the scripting API](https://github.com/OpenReliant/openreliant/blob/v0.7.0/docs/guide/reference.md).

## Confirmed gaps for the intended full HUD

### Replacing or configuring the native instruments

Scripts draw after the native HUD. `hud.set_display_enabled` controls displays registered by scripts; it does not hide built-in radar, gauges, labels or contacts. The public HUD API has no per-instrument replacement/layout facility. The native instrument-window layouts and text positions remain in engine code. Transparent replacements could hide some pictures but would not reliably move or remove all accompanying live text and drawing.

A useful upstream extension would let a mod either configure native instrument geometry/text sizes while retaining native behavior, or take over selected instruments through supported callbacks with fallback on disable/error. An exact `hud_layout.ini` parser is only one possible implementation, not the requested dependency.

Evidence: [`Display.drawOverlay`](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/openreliant/main.zig#L2031-L2043), [HUD package declarations](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L350-L453), and [native window layouts](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/game/hud/windows.zig#L129-L147).

### Live instrument state for a script replacement

The exposed player object does not provide the complete state used by the native HUD: selected gun group and firing mode, gun charge/energy, selected missile and remaining inventory, HUD-selected target/subtarget, radar range/transition, and the native kill readout are examples. The existing `object.target` describes its current AI order's target, not a promised snapshot of the player's HUD selection. Reading static weapon records or intercepting button presses is not an equivalent replacement for authoritative live state, especially across saves and mission-driven changes.

The probe's proposed field names were rejected at runtime. The complete package/object declarations and generated reference were also inspected; those checks establish the gap, rather than assuming that rejection of a guessed name proves absence. A supported read-only instrument snapshot, or configurable native widgets which retain this logic, would avoid duplicating gameplay behavior in the mod.

Evidence: [object fields](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/objects.zig#L67-L308), particularly [`object.target`](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/objects.zig#L156-L168), and [native gunnery state](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/game/hud/gunnery.zig#L64-L111).

### Script picture-cache capacity and lifetime

Script-loaded images/fonts share a 128-file and 64 MiB budget. Pictures are counted at decoded RGBA size, cached by context/filename, and retained until presentation shutdown, including retired contexts. There is no exposed unload/eviction control. This does **not** mean ordinary native PNG replacement mods are limited to 128 files; it concerns the scripting picture/font cache.

Two isolated reproductions passed up to the documented limits and failed at the next asset:

- Sixteen different 1024x1024 RGBA pictures loaded; the seventeenth returned `BadSize`. Each costs 4 MiB decoded, even when requested at a 1x1 screen size.
- 128 distinct small-picture filenames loaded; the 129th returned `TooManyAssets`.

The current 90 missile poses alone total 360 MiB decoded. They need not all be visible together, but loading them across a session still consumes the retained cache. Our exports should be optimized where possible; a sustainable full-resolution script path also needs a supported lifecycle/budget strategy, or an alternative native asset path. Merely renaming the files does not remove this cache behavior.

Evidence: [cache limits and image loading](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L30-L91).

## Mod-side work, not upstream defects

- Only 26 of the current PNGs are exported under recognized native aliases; 559 use `rc_*` names. Stock registers those files but does not automatically know which instruments should request them. Additional native aliases can restore more art at stock geometry; a script port can request arbitrary filenames. This mapping is our responsibility.
- The current INI is our authoring format. Its absence from the official parser is not itself a bug. We can translate it to a format or script supported by upstream.
- White matte cleanup and the 1024 missile exports are asset changes. All 585 current PNGs already have zero RGB under alpha zero, so those fixes do not require a companion executable. Remaining edge quality still needs visual testing in each rendering path.
- The 17 unfinished large-schematic jobs, fuel-pod review and neutral-render texture detail are artwork work. They must not be confused with compatibility blockers.
- The completed subtargets 393–409 remain unchanged. Ion Cannon is frame 406. Their `rc_*` exports are preserved but are not automatically active native replacements on stock.

## Separate font bug and existing upstream work

The same valid `BLUFONT.ttf` works as a native font replacement and through scripted `font="hud"`. Passing its filename to `hud.measure` with `base_font="hud"` or the flight default instead returns `InvalidFont`; the same file with either menu base succeeds. The source appears to fit all scripted custom fonts with ramp coverage, whereas the native HUD uses palette coverage. That is a likely cause, not a patched/verified diagnosis. The built-in `hud` font selection is a practical workaround, so this is not a reason to fork the engine.

The author's existing [issue #520](https://github.com/OpenReliant/openreliant/issues/520) already covers remaining palette-font work, including small target-range/radio fonts. [Issue #509](https://github.com/OpenReliant/openreliant/issues/509) covers high-resolution software-drawn power-ball/loadout images. Neither should be described as an unreported discovery. Existing completed scripting work includes [#558](https://github.com/OpenReliant/openreliant/issues/558) and [#590](https://github.com/OpenReliant/openreliant/issues/590).

## Local evidence and next release gate

The official archive SHA-256 is `bf6472a46aba0f5eade965feed773f945e212dc9275e51d57a219a9ddd3d10f2`; the installed executable SHA-256 is `7f828013dea07ca02972a5a4d2463b15308f5609e2f716766be010e5219b1253`. Every installed release file matched the official archive. The normal launcher and isolated native/HUD-pack scenes exited with status 0 after saving their captures. Screenshot mode deliberately closes the window.

All 589 live HUD files still match the unchanged runtime manifest `8ef978007b866a3d8d111fba43698a34a68d2c970efb119902afaaf9232c5c98`. All 17 approved subtargets retain their exact bytes and source/export pixel equality. Editable probes are in `source/compatibility-probes`; `tracking/stock-0.7-audit.json` lists checks and hashes. Machine-specific logs, screenshots and rollback paths remain under ignored `.local/stock-0.7/`.

Local drafts, not submitted upstream:

1. [Native HUD replacement and instrument state](../tracking/issue-drafts/HUD-UPSTREAM-01.md).
2. [Script picture-cache lifecycle and capacity](../tracking/issue-drafts/HUD-UPSTREAM-02.md).
3. [Custom TTF rejected with HUD base font](../tracking/issue-drafts/HUD-UPSTREAM-03.md).

## Proposed ways forward

The issue drafts include implementation options derived from the working HUD, rather than only a list of missing features:

| Option | Engine work to discuss upstream | Work kept inside this mod |
|---|---|---|
| Configurable native instruments | Generic root/child geometry, text sizing and artwork/animation slots, retaining native state | Export the agreed layout format and map artwork into its slots |
| Script replacements | Per-instrument takeover with native fallback; read-only presentation snapshots; sustainable picture cache | Port the proven placement/drawing logic to a player script distributed with the images |
| Incremental first slice | Support radar, gunnery and missiles first; leave other instruments native | Compare these against the earlier working layout before expanding |

The first option is a focused way to retain built-in behavior; the second offers more freedom for future designs. Both avoid a separate executable for players once released upstream. We should follow the author's preferred architecture rather than maintain a parallel engine branch.

For images, the notes propose bounded, renderer-safe eviction or explicit handles, with an adequate configurable working-set budget. They also explain which mod export optimizations help and why atlases alone do not solve the byte limit. For fonts, they identify a likely shared-helper fix and the already working `font="hud"` workaround. Proposed fixes are labelled unimplemented; the earlier engine work is preserved as reference material, not presented as an upstream-ready patch.

The release gate is an official-engine implementation that reproduces the agreed placement and live behavior from a single mod folder, followed by fresh-install/disable/rollback and gameplay tests. The current stock installation is ready for comparison testing; the full authored HUD is not yet a compatible public modpack.
