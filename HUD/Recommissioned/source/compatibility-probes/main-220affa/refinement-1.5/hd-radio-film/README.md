# Higher-resolution face films draw too large

Tested on unmodified main 220affa78729a2ce7dcb49602e4f38a4a53d5dc1 (reports 0.8.1).
Copy only `mod.ini`, `mission991.dte`, `rc_hd_test.fm8`, and `rc_portrait.ut`
into `game-data/mods/hd-radio-film/`. Start:

```
openreliant GAME_DATA --mission 991 --ship 2 --view 2 --size 1920x1080
```

Leave sound enabled: the supplied 20-second silent speech keeps the radio film
playing. Within roughly two seconds, the pilot image expands far beyond the
native radio frame. No HUD replacement script or patched engine is involved.

The film contains three unaltered 480x400 PNG frames from the maintained Bandit
portrait sequence. The normal `sltool fm8 encode source-frames rc_hd_test.fm8`
command succeeds; `sltool fm8 info` confirms 480x400. Larger films are already
accepted by the encoder/decoder despite the guide describing 120x100 faces.
Their colour reduction to FM8's palette is the standard encoder behavior.

The rendering path in `src/engine/game/hud/radio.zig` calls
`Canvas.imageShaken`; `hud/windows.zig:412` then uses `hud.drawImage`, whose
logical size is the texture's pixel dimensions. A 4x texture therefore draws
4x wider and taller while the surrounding radio grid retains its original size.

Suggested solution: give radio films a logical 120x100 display size independent
of source resolution, using the existing `hud.drawImageAs` path or an equivalent
scaled/shaken image helper. Preserve aspect ratio, window animation, hit shake,
speaker text and frame geometry. Whole-instrument `layout.radio.scale` also
shrinks the grid and speaker text, so it cannot independently correct the film.

Expected: a 480x400 replacement has sharper detail inside the same radio panel
as its 120x100 counterpart. A separate film/content rectangle would additionally
allow the authored portrait and speaker placements.

`portrait.zig` is the editable mission fixture; it uses normal DTE commands and
the upstream SDK. The included art is for reproducing this HUD issue; retain
the original project and game-art rights when redistributing.
