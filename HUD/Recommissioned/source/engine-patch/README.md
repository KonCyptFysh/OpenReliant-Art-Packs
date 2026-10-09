# Current HUD companion source

This preserves the tested HUD 1.1 implementation on upstream OpenReliant commit
`4150676e798176f3bbcc7c9872c52c20a333f296` (0.7.0 development). It is not an
upgrade to the official v0.7.0 release. Engine porting and distribution belong to
the release-preparation chat; do not replace the current launcher during HUD art testing.

`recommissioned-hud-1.1.patch` is the complete delta against that exact upstream
revision, including the earlier authored-layout renderer and the latest sprite,
gunnery and text changes. It is not merely the incremental HUD-1.1.patch from
the previous installation. `overlay/` holds the final versions of all eleven
changed or added files, with embedded tests and layout fixtures.
`upstream.json` pins the before/after source hashes and installed binary hash.
The upstream Mozilla Public License is retained in `LICENSE`.

To rebuild in a separate checkout with Zig 0.16.0:

```sh
git clone https://github.com/OpenReliant/openreliant.git engine-hud
cd engine-hud
git checkout 4150676e798176f3bbcc7c9872c52c20a333f296
# Set HUD_PATCH to this repository's source/engine-patch directory.
git apply --check "$HUD_PATCH/recommissioned-hud-1.1.patch"
git apply "$HUD_PATCH/recommissioned-hud-1.1.patch"
zig build -Doptimize=ReleaseSafe -j2
zig build test -Doptimize=ReleaseSafe --summary all -j2
zig fmt --check src build.zig
```

Dependencies are resolved by the pinned upstream build files. Build caches,
downloaded dependency trees and binaries are intentionally absent here. A new
build must be tested; its binary hash need not equal a build made elsewhere.
The current installed binary has already passed 2,042 tests. The handoff checks
patch application and exact source reconstruction without rebuilding or
changing that installed engine.
