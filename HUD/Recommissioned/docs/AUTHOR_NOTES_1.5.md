# Follow-up notes for the author — not posted

I’ve got the HUD loading without the legacy flash now, including when switching
missiles. That was my image-loading fallback. I’ve also fixed the missile outline
and checked the gun sync indicator against the native behavior.

Two things remain on the current unmodified main, 220affa:

1. **The Grendel ammo counter disappears in instant action.** Mission 0 gives me
   `grendel` and 3000 rounds, but mission 29 gives me `t_grendel` and nil. It’s
   missing in the native HUD too. `roundsShown` only checks the original ship
   types; resolving the t_* variant before that check looks like the fix.
2. **HD pilot films play, but draw much too large.** My frames are 480x400 and the
   normal FM8 encoder handles them. In-game they draw four times wider and taller
   than the original 120x100 films, while the radio frame stays the same size.
   Could the film keep a 120x100 logical display size regardless of texture
   resolution? Scaling the whole radio panel also shrinks its grid and text.

There are small standalone reproductions for both in the attached review bundle,
with screenshots and exact steps. Neither needs my HUD pack or an engine fork.
The native power-ball reuse request from the earlier notes also remains.

The sync bar itself behaves as intended: Ctrl+G changes the selected pair between
together and alternating; FULL GUNS deliberately doesn’t show a pairing bar.
