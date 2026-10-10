# Editable HD portrait sources

10,909 editable 480x400 PNG frames in 257 sequences, covering every film name
in the original PILOTS.HOG. The original 225 sequences / 9,353 frames remain
byte-identical. HUD 1.9 adds 17 RealBasicVSR x4 restorations / 842 new frames
and 15 exact HD aliases, filling all 32 previously missing uppercase filenames.
`sequence-map.json` records the native file names, restoration provenance,
frame counts and archive-member checksums. Every source sequence matches its
native counterpart; playback remains 15 frames per second in the game.

`tools/build_portraits.py` uses the unmodified OpenReliant 0.9.0 sltool encoder.
It encodes the source frames directly as 480x400 FM8 films. OpenReliant 0.9.0
fits every face film to its native 120x100 logical rectangle, then applies HUD
scaling. No shader, marker or padding is needed. The shared 256-colour film
palette quantizes colour; the export does not resize or redraw the originals.

Rebuild with Python/Pillow and the official 0.9.0 sltool:

    python tools/build_portraits.py --sltool /path/to/sltool --native /path/to/extracted/pilots

The native folder is read only and checks names, counts and checksums.
The command writes 257 flat FM8 files and tracking/portrait-runtime-inventory.json.
It accepts both .fm8 and .FM8 names. `--missing` preserves verified 480x400 exports
and rebuilds old padded exports. Changed existing source or export hashes are
rejected for films being reused. `tools/build_mod.py` includes only checked films.
Update manifests and run `tools/verify_working_copy.py` before deployment.

HUD 1.10 requires OpenReliant 0.9.0. The old 1.9 shader and notices are preserved
under source/compatibility/hud-1.9 as history, excluded from runtime exports.
The public beta download remains HUD 1.8; this Git source/runtime snapshot is 1.10. This does not license underlying StarLancer art.

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
