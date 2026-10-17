# Texture resolution downloads

Every released non-HUD asset offers 1K, 2K and 4K textures in the gallery. Each choice is a complete mod, not a patch. Choose one resolution per asset; different ships can use different tiers. Replace the existing mod folder when changing tiers. The stable folder name and native dependencies stay the same, so do not install tiers side by side. HUD files are excluded.

The limit is the longest edge of each material texture: 1024, 2048 or 4096 pixels. Preserve aspect ratios and leave smaller maps at their existing dimensions. Launcher illustrations (`mod.png`) are excluded from this limit. The Sai's master includes an 8192×4096 atlas: its 4K distribution is capped at 4096×2048, while its original master and historical download remain preserved.

The gallery's photographs and 3D previews continue to show the approved master artwork. The resolution selector changes the ZIP, displayed size, package version, checksum and release notes together. Existing 4K releases are reused where already within the limit. Smaller tiers have a `.res2` package revision, without changing the artwork revision.

## Author once, generate each tier

Keep approved master maps and source scenes in their existing named workspaces. Generate downloads from the validated repository runtime with `tools/resolution_pack.py`; never resize the master in place. The tool requires Python 3, NumPy, Pillow and ImageMagick. It preserves 8-bit or 16-bit precision and exports PNG, which allows OpenReliant to generate loadout colour variants. It does not introduce duplicated g/r textures or precompressed runtime textures.

Example:

```sh
python3 tools/resolution_pack.py --root "Alliance Fighters/Coyote" --tier 1k --source-commit <verified-master-commit>
```

Outputs are under the asset's ignored `dist/resolutions/` directory. Each ZIP contains an exact runtime manifest, source hashes and a filtering record. Generated files are rebuildable; source maps are stored only once in Git LFS. `tracking/resolution-packs.json` pins catalogue downloads to the master manifest; publication fails if the master changes without refreshed resolution variants. Publish each asset's new immutable release and verify every download before listing it. Do not replace historical ZIPs or tags.

## Emissives and material filtering

OpenReliant 0.18 requires each normal, ORM and emissive map to have the same dimensions as its base texture. Author new emission once at master resolution using the same UV layout, then regenerate all tiers together. There is no need to finish future emissive features before making these resolution choices available.

- Colour and emissive maps are decoded from sRGB, averaged in linear light with alpha weighting, and encoded back to sRGB. This preserves average light energy without making every small light brighter.
- Normal maps are averaged as vectors and normalized again. Normal alpha is ignored by OpenReliant. Fine normal variance lost during offline reduction cannot be carried in that channel; lower tiers can soften fine relief and its highlights.
- ORM channels are averaged as linear data, without colour correction.
- Models, UVs, animations, scripts and surface shaders are copied unchanged. Damage flicker, thrust response and heat timing therefore use the same logic at every tier. Procedural masks expressed in UV/model coordinates retain their placement. Future shaders using pixel-sized offsets must handle texture size explicitly.

Inspect small windows, seams and bright/dark boundaries at 1K when adding new effects. Tiny lights can merge or become softer even when average intensity is preserved. Do not expand glow into vents or neighbouring panels to compensate automatically. A tier-specific correction is appropriate only if visual review shows it is needed.

Primary engine references: [material maps at 0.18.0](https://github.com/OpenReliant/openreliant/blob/v0.18.0/docs/guide/modding.md#material-maps), [texture filtering](https://github.com/OpenReliant/openreliant/blob/v0.18.0/src/engine/surrender/surrenderlib/srtexture.zig), and [map loading](https://github.com/OpenReliant/openreliant/blob/v0.18.0/src/engine/surrender/surrenderlib/srtexture/mod_pictures.zig).
