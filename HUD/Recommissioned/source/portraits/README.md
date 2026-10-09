# Editable HD portrait sources

9,353 original 480x400 PNG frames in 225 sequences. These are exact copies of
the maintainer's upscaled pilot portraits, checked against the source inventory.
The frames remain unchanged. `sequence-map.json` records the native file names,
frame counts and archive-member checksums. Every source sequence matches its
native counterpart; playback remains 15 frames per second in the game.

`tools/build_portraits.py` uses the unmodified upstream sltool encoder. It adds
four transparent pixels at the right and bottom in temporary files, producing
484x404 native FM8 files with 480x400 visible content. The reserved palette
colour at the bottom-right plus dimensions and HUD draw state identify the
films to the paired shader. The padding is never drawn. FM8 uses a shared
256-colour palette per film, so runtime conversion quantizes colour; it does
not resize, sharpen or redraw the originals.

Rebuild with Python/Pillow and sltool from tested main 220affa:

    python tools/build_portraits.py --sltool /path/to/sltool --native /path/to/extracted/pilots

The native folder is read only and is used to check names/counts/checksums.
The command writes the 225 flat FM8 files and tracking/portrait-runtime-inventory.json.
Then `tools/build_mod.py` preserves these checked film exports while rebuilding
the HUD, and exports `source/shaders/device.glsl` alongside them. A missing or
changed film is an error, never silently discarded. Update manifests and run
`tools/verify_working_copy.py` after a coherent export, before deployment.

The shader is based on the exact upstream device.glsl saved beside its editable
version. See source/shaders/README.md for compatibility and known limits.
Public release remains held; this does not license underlying StarLancer art.
