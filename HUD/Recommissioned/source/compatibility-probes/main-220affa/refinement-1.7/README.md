# HD portrait reproduction, test-only

Use the complete HUD 1.7 export on unmodified main 220affa. Copy mod.ini,
observer.luau, mission991.dte and rc_portrait.ut from this folder into a separate
flat test mod. Run mission 991, ship 4, view 2 at 1920x1080 with sound enabled.
The mission deliberately plays the full Bandit film under the BRIDGE OFFICER
test label for 20 seconds. This tests name size separately from film size; it
is not the production pilot mapping. Native pilot names/films are unchanged.

The observer only logs window state. The mission uses normal native commands.
The source fixture builds using upstream Zig 0.17.0 and src/root.zig, with no
engine edits. The adjacent capture/input helpers record the test environment;
paths in those helpers refer to the local refinement workspace.

The 1080p/720p overlap captures use the earlier mission that opens comms via
OpenInstrument. Interactive synthetic-key attempts were inconclusive this
pass; the game either entered options or ignored injected keys. Their image
labels alone do not establish successful input/pause checks. The second run
does verify a readable name, extended playback, hit shake and recovery.
HUD 1.6 previously verified native/modded C and number selection, and no input
code changed in HUD 1.7. User confirmation of live controls is still useful.
