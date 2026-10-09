# Provide a sustainable image-cache lifecycle for large scripted HUDs

Submission-ready wording: [GitHub issue draft](../github-issues/02-script-image-cache.md). This file retains the fuller engineering notes.

Local draft; not posted. Type: modding API/resource management. Related: [#590](https://github.com/OpenReliant/openreliant/issues/590).

Tested with official v0.7.0 Linux x86_64, commit `3b27f16779e53c03ccf177bfd2f9ec46a27bbfb7`.

The script drawing cache has a shared limit of 128 pictures/fonts and 64 MiB. Images are retained until presentation shutdown, including retired script contexts, with no public release/eviction API. This is documented behavior, but it limits full HUD replacements which load different ship schematics and animation poses over a session. It is distinct from the normal native sprite-replacement path.

## Reproductions

Use a player script and call `hud.picture` for successive files from `on_frame` while `hud.shown`. Draw each at `vector.create(1,1,0)` and catch the result with `pcall`; loading across frames avoids conflating the test with the per-frame command limit.

1. Seventeen distinct 1024x1024 RGBA PNGs: files 1–16 load; file 17 returns `picture <name>: BadSize`. Sixteen decoded images fill 64 MiB regardless of PNG compression or requested screen rectangle.
2. 129 separately named copies of a small PNG: files 1–128 load; file 129 returns `picture <name>: TooManyAssets`.

Our isolated probes reproduced both thresholds without crashing the game. The preserved scripts and preparation tool are in this repository's `source/compatibility-probes` and `tools/prepare_stock_hud_probes.py`.

Source: [limits and retention policy](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L30-L33), [picture loading](https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/scripting/drawing.zig#L69-L91), and [documentation](https://github.com/OpenReliant/openreliant/blob/v0.7.0/docs/guide/scripting.md#pictures-shapes-and-fonts).

## Requested outcome

A supported strategy for a mod to retain only its currently needed assets: safe eviction/release, a budgeted cache with useful diagnostics, or an equivalent native asset/atlas mechanism suitable for a complete HUD. We are not requesting unlimited allocation or that every image be resident simultaneously. Changing the current safety limits alone would not address lifetime across changing instruments/missions.

For context, our 90 current missile poses are 1024x1024 and would consume 360 MiB decoded if all cached. We can optimize exports and representation, but should not need a custom engine binary to manage the active image set. Please distinguish capacity errors from invalid image dimensions: `BadSize` at an exhausted cache obscures the cause for mod authors.

## Concrete solution options

1. **Budgeted cache with safe eviction.** Track pictures used by the current/in-flight draw commands and evict least-recently-used unreferenced entries. Retire textures only after the renderer can no longer reference them; do not free an image immediately because a script stopped. Reclaim retired contexts at a safe frame boundary. This is a direct extension of `Assets.loadPicture` and the shared presentation asset store.
2. **Explicit asset handles and release/preload.** Let a script request/pin an image set for the current ship/instrument and release it on change. Queue actual destruction behind the renderer's completion boundary. Expose resident bytes/count and a clear `AssetBudgetExceeded` error. The handle API must still have a bounded budget and cleanup on script failure; release cannot rely solely on a well-behaved mod.
3. **Use the native asset path where appropriate.** If upstream chooses configurable native HUD widgets, those widgets can resolve artwork through the ordinary sprite/texture loader rather than the script picture cache. Extending script shape access to the necessary named sets could also reduce duplicated picture loads. This still needs a resource policy; it must not silently become an unlimited secondary cache.

For either scripting solution, make the active working-set budget configurable or let a mod declare a bounded requirement subject to engine/user policy. Eviction alone cannot fit a genuinely larger simultaneously visible set into 64 MiB. Sharing identical immutable images by resolved content can avoid needless duplication across contexts, while preserving mod identity and reload correctness.

On the mod side, we can crop transparent margins while preserving per-frame pivots/rectangles and load only the current ship's artwork. Atlas/source-rectangle support could reduce file count. An atlas alone does not reduce decoded bytes, and downscaling all source art would sacrifice the resolution this pack is intended to deliver. We would preserve the approved masters and validate any optimized export against the existing layout.

The previous custom renderer proves the artwork can be displayed, but its own cache is not evidence of a safe general lifecycle solution. The recommendation is a bounded cache with renderer-safe eviction plus a configurable working-set budget, not copying an unrestricted mod-specific loader.

Acceptance: cycle through more than 128 distinct assets and more than 64 MiB cumulatively while keeping the resident working set under the configured budget; check that active/in-flight images remain valid, repeated reloads reclaim retired assets, and capacity failures name the budget rather than suggest corrupt PNG dimensions.
