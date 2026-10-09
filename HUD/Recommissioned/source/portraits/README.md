# Editable HD portrait sources

10,909 editable 480x400 PNG frames in 257 sequences, covering every film name
in the original PILOTS.HOG. The original 225 sequences / 9,353 frames remain
byte-identical. HUD 1.9 adds 17 RealBasicVSR x4 restorations / 842 new frames
and 15 exact HD aliases, filling all 32 previously missing uppercase filenames.
`sequence-map.json` records the native file names, restoration provenance,
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
The command writes the 257 flat FM8 files and tracking/portrait-runtime-inventory.json.
It accepts both .fm8 and .FM8 names. Use `--missing` to preserve verified existing
films and encode only additions; changed existing sources or exports are rejected.
Then `tools/build_mod.py` preserves these checked film exports while rebuilding
the HUD, and exports `source/shaders/device.glsl` alongside them. A missing or
changed film is an error, never silently discarded. Update manifests and run
`tools/verify_working_copy.py` after a coherent export, before deployment.

The shader is based on the exact upstream device.glsl saved beside its editable
version. See source/shaders/README.md for compatibility and known limits.
HUD 1.8 remains the published beta; the 1.9 additions are available in Git, without a new player release.
This does not license underlying StarLancer art.

## Video restoration provenance

`tools/restore_portraits.py` uses `tools/portrait_temporal_inference.py`, copied
from the maintainer's established RealBasicVSR inference implementation. It
processes entire sequences with the same GAN x4 checkpoint as the original
HD collection. It adds no interpolated frames. Both previews and game playback
use the verified native rate of 15 fps; older preview metadata's provisional
12.5 fps is not used.

Checkpoint SHA-256:
`52f77c2c835aaa3fe675b3959b2f85010a6c6f63f77f7e279394646e55a4e376`.
The restoration environment used PyTorch 2.11.0+cu130, Pillow, NumPy and FFmpeg.
The inference definitions are the existing Apache-2.0 adaptation of
OpenMMLab RealBasicVSR/BasicVSR; retain the attribution in that source file.

Each added folder has `restoration.json`. Exact aliases reuse finished PNGs
without another upscaling pass. Native audit metadata is in `archive-review-2026-10-09`. Original game films,
native frame archives and local comparison exports are not distributed here.

## Reproducing the additional restorations

The finished HD frames and 17 preview videos are included. To run restoration
again, supply the model checkpoint above and your own StarLancer films. Copy
`archive-review-2026-10-09/inventory.json` and `coverage-review.json` into an
empty audit directory. For each of the 17 names listed by
`additional_distinct_sequences` in the coverage file, run:

    sltool fm8 extract <your-original-film> <audit-directory>/frames/<film-stem>

Keep the film names and extracted frame numbering unchanged, including case.
Then run from this HUD directory with PyTorch, NumPy, Pillow and FFmpeg installed:

    python tools/restore_portraits.py --audit <audit-directory> --checkpoint <model.pth> --output <separate-output>

The tool checks the checkpoint hash and preserves original frame counts and
15 fps timing. Original films and model weights are user-supplied, not bundled.
