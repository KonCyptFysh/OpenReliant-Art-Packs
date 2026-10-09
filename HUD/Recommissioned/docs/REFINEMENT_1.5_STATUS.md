# HUD refinement status

## HUD 1.5 refinement, 9 October 2026

- Fixed legacy HUD flashes at startup and during missile changes. Current images
  load in bounded callbacks before the same frame is presented; actual missing
  artwork still falls back to the complete native instrument. Radar warms only
  its current frame, not all 43 frames.
- Moved the missile name onto the upper wireframe, centered at y=35 at 1080p.
- Rebuilt all 90 missile poses with a continuous halo derived from the full-size
  silhouette. Preserved source renders, opaque foreground colours and geometry.
  Black, white and orange comparisons and a white-background gameplay capture
  no longer show the detached/stippled contour.
- Verified the ordinary Grendel counter decreases from 3000 to 2982. Verified
  solid/split pair indicators with Ctrl+G, gun-group cycling, and FULL GUNS.
  FULL GUNS hides the pair indicator by legacy design; changing gun type does
  not toggle the synchronized firing setting.
- Found an upstream gap: `t_grendel` in mission 29 exposes no `hud.guns.rounds`;
  the native panel also omits it. A standalone reproduction and proposed fix
  are preserved under `source/compatibility-probes/main-220affa/refinement-1.5`.
- Confirmed the installed portraits are legacy. Inventoried 9,353 updated
  480x400 frames in 225 sequences. A standard FM8 test encodes and plays them,
  but the native radio renders the higher-resolution film four times too large.
  Keep HD films out of the live pack until sizing can preserve the surrounding
  frame/text. Full original sequences remain at the inventoried authoring path.
- Tested 1,245 continuous HUD frames including 12 missile switches: no fallback
  frames or script diagnostics. Passed 1080p/720p layout and invalid-art fallback
  checks. Public release remains held; the engine stays unmodified main 220affa.

All 924 runtime files remain flat. The 90 missile PNGs, layout INI, player script
and version metadata changed; the other 819 PNGs and approved subtargets 393–409
(Ion Cannon 406) are unchanged. User gameplay review and prior art/QA work remain.
