# Expose HUD transition progress for scripted replacements

This is a smaller presentation request while the HUD API is still being settled.

Our custom radar works at each settled range, but I switch back to native while it zooms. `hud.radar.zooming` tells me a transition is happening, not which ring frame/progress should be drawn. Likewise, the missile ring has the selected type and ordering but no rotation progress, and open windows don't expose their opening/closing progress.

Could those current presentation values be available to scripts, or is there already a supported way to follow the native animations?

I'd prefer readings from the animations themselves rather than starting separate timers in the mod, so they stay together through pauses, view changes and rapid input. An animation progress or current step for each would be enough; exact names are up to you.

Attached: `05-animation-progress.zip`. The small observer keeps native instruments visible and logs power, radar range/zoom, missile selection/ring fields and open windows. In the included mission, use V for radar range, period for missile selection, and the normal window controls. It demonstrates the exposed values; it is a feature request, not a game crash.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
