# Recommissioned HUD

This local companion build reads the mod's `hud_layout.ini` and flat `rc_`
images. It keeps the upstream development renderer and emissive support.

Custom pictures clear hidden RGB in alpha-zero pixels before mipmapping.
The mod builder also does this for every exported sprite, including native
HUDHARD and chase-point replacements that use other image loading paths.
No visible source pixels or alpha values change.

Fuel, kill, countermeasure, missile and gunnery readouts use visible capital
height and centre their ink vertically. Other text retains its authored size.
Gunnery draws the weapon name and highlights from live groups, a solid bar
for full or synchronised guns, and a split bar for individual firing. Its
mode caption follows the same state. Its wireframe size remains controlled
by the layout, with all gun overlays sharing that rectangle.
