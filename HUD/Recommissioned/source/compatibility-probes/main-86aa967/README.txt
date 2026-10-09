Current-main HUD probes, 8 October 2026

Run on unmodified upstream commit 86aa967486e8e0191dbbd572acb8e894a30833f4.
These diagnostic mods are separate from the player HUD package. Copy one named
folder into an isolated game-data/mods directory, with the ordinary HUD disabled.
No original game data is included.

font-sizes: enter any cockpit mission view at 1920x1080. It draws six rows using
the same font at six sizes on the left. The right column uses byte-identical
font files with a separate instance per size. Expected: each row matches its
right-hand counterpart. The black backdrop and text need no custom ship/mission.
The font is Oxanium, under the included SIL Open Font License.

readings: enter a mission in cockpit view. At frame 60 it requests the separate
chase camera through openreliant.camera.set_view. At frame 30 and 180
the script logs HUD_API lines for the current exposed readings. Compare the
clock and ship readings in both views. A nil caption/view label can be normal.
The fixture proves access in those two views, not every dynamic state or mission.

The associated runtime results are recorded in tracking/main-dev-baseline.json.
