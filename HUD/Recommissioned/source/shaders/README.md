# HD portrait presentation, HUD 1.7

`device.glsl` is the editable mod export. `device.upstream-220affa.glsl` is its
unchanged upstream baseline. Only the marked fragment-stage block differs.
Source: OpenReliant/openreliant commit 220affa78729a2ce7dcb49602e4f38a4a53d5dc1,
`src/platform/shaders/device.glsl`, MPL-2.0. Full licence supplied in runtime-meta.

The public whole-shader mod feature loads a flat device.glsl. The added block
recognizes our 484x404 FM8 textures by the reserved magenta padding pixel, only
on unlit HUD primitives at depth 1. It discards the oversized quad outside a
120x100 logical rectangle and samples the original 480x400 content at 4x UV.
Sample centres are clamped inside content to avoid padding bleed. Stock lighting,
dithering, outputs and mod-function hooks are retained. Linear and gamma-space
paths use the appropriate marker colour. Ordinary textures are unaffected.

Native playback still chooses and advances every frame, handles the actual
speech, line queue, name, opening emblem, closing animation and hit shake.
This is a mod-side shader workaround, not a Luau animation player or an engine
patch. Radio input is untouched. Comms may overlap the portrait as requested.

Requirements/limits:
- Tested only on main 220affa / 0.8.1. Whole shader interfaces are explicitly
  version-dependent even if the mod scripting API is stable.
- MOD EFFECTS must be on when starting. Another device.glsl mod can replace it.
  Shader rejection/disable/override leaves native HD films oversized. Remove
  both this shader and the 225 replacement FM8 files to restore native films.
- HUD API bounds still include the raw oversized quad; our layout does not use
  those bounds to place comms. There is additional discarded fragment work.
- All native queue/interruption code remains intact; exhaustive campaign and
  every interruption combination are not covered by this pass.
- Native FM8 colour is quantized to 256 entries. PNG originals are preserved.

A fixed logical film rectangle in the engine remains the cleaner upstream
solution and would eliminate this version-specific shader dependency.
