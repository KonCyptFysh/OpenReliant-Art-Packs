# Whole-radio scaling: a partial mod workaround

Use mission991.dte, rc_hd_test.fm8 and rc_portrait.ut from the adjacent
refinement-1.5/hd-radio-film reproduction, plus this mod.ini and observer.luau,
in one flat test mod directory. Keep it separate from the other reproduction.
Run with sound enabled, mission 991, ship 2, view 2 at 1920x1080.

The public HUD layout API sets radio.scale to 0.25. After its initial emblem
animation (capture at 150 ticks), the 480x400 film draws at approximately the
usual on-screen size. Its frame, opening emblem, offsets and speaker text
also scale down: the frame is visibly one quarter of its normal dimensions.
The fixture has no speaker-name label; the text scaling follows the shared
native Canvas/pen path rather than a named-speaker screenshot in this test.

This proves that scripting can resize the film, but whole-panel scaling
does not independently fit it into the existing frame. A rebuilt scripted
radio/animation player is not ruled out; it has not been implemented or
validated. Current HUD readings expose window phase/bounds, not the active
film, speaker or playback frame. radio_say describes requested/queued lines,
not a complete playback readout. Do not infer that a simple timer reproduces
queueing, interruption, speech timing or hit shake.

The smallest native improvement still appears to be a fixed 120x100 logical
film rectangle, independent of its source pixel dimensions. These files are
test-only and are not in the deployed HUD.
