# Non-visual loadout texture validation

This probe uses the unchanged official OpenReliant v0.8.1 texture loader (source commit `b91c70bba414b2b2dc16bcf687647b41701deb8a`). It reads a shipped PNG material set, makes green and red copies, checks their colour channels, and checks that the inherited normal and ORM mipmaps match the uncoloured material byte for byte. It reads the original image bytes; output is bounded to a 256-pixel longest side. It does not launch or modify the game, draw a preview, or certify gameplay/GPU rendering.

With Zig 0.17, system zlib development files and an unmodified checkout of that release:

```sh
zig build-exe -O ReleaseFast -lc -lz --dep openreliant -Mroot=texture-probe.zig --dep zlib -Mopenreliant=/path/to/openreliant/src/root.zig -Mzlib=zlib-abi.zig -femit-bin=texture-probe
./texture-probe /path/to/mod-folder unprefixed_texture_name
```

The tiny zlib declaration supplies the standard ABI used by the upstream PNG decoder. No OpenReliant source is changed. Per-pack results and the exact input hashes are recorded in `compatibility-0.8.json`.
