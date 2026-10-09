Radar/target API probe for upstream 240f075, 8 October 2026

Copy readings into an isolated game-data/mods folder. Enter a mission in cockpit
view with a target selected. At frame 30 the script logs HUD readings, including
radar contact count/positions/looks and target presentation. At frame 60 it
requests the separate chase camera. Frame 180 logs the same fields with native
instruments hidden. A mission-held camera may reject the switch; inspect the
logged switch result. No game assets are included.

The same font-size diagnostic is preserved in ../main-86aa967/font-sizes.
This probe is not included in the ordinary HUD runtime package.
