# Recommissioned HUD

Custom HUD artwork and authored layout for OpenReliant. Some schematics still
use the original game artwork.

**HUD 1.3 is a working test candidate; public release remains on hold.** The
ordinary drop-in mod now uses the expanded upstream HUD readings on unmodified
main `30163d9`, including #868. There is no companion engine in the package.
The source-archive dev build is a local test dependency only. The normal game
launcher remains on published 0.7.0, where the script keeps native instruments.

This pass adds the authored radar, gauges, player and target status, whole-ship
large targets, damage, power, wing status, objectives and comms to the existing
weapon panels and larger counters. Native fallback remains for subtargets,
ammunition-bearing guns, missing art and radar range transitions. Warning lights,
radio portraits, messages and prompts remain native. The power display uses a
temporary allocation triangle instead of the native animated ball.

The export contains **924 flat runtime files, including 909 PNGs**. All 586
previous PNGs are unchanged. Additional mirrored grids/status art and composed
gauge states are generated from preserved masters. Approved subtargets 393–409,
including Ion Cannon 406, remain unchanged; the 775 nested live authoring files
are preserved. Exact exports are copied to the live HUD and isolated dev review.

**Known test issue:** some scenes lose pieces of sprites and text without script
errors. It appeared in the synthetic state sweep and a Mirage control scene;
normal Coyote flight was clean. The cause is not established. This pass is ready
for continued local review, not a final visual approval or public release.

Use `launch-hud-upstream-test.sh` for the isolated review mission or
`launch-openreliant-dev.sh` for the menu on the same development build.
Current details: [port and checks](docs/UPSTREAM_HUD_PORT.md),
[known issues](KNOWN_ISSUES.md), and `tracking/hud-api-expansion.json`.
Earlier 240f075 author notes remain dated evidence; #832 part 3 has now merged.
Nothing has been posted upstream by this pass.

The large-target art backlog remains 17 jobs covering 19 images, plus fuel-pod
frame 410. Finished subtargets must not be reworked or relabelled.

- [Working exports and local testing](WORKFLOW.md)
- [Asset status](ASSET_STATUS.md)
- [Installation and removal](INSTALL.md)
- [Release notes](CHANGELOG.md)
- [Maintainer guide](docs/MAINTAINER_GUIDE.md)

When released, players will extract the named mod ZIP's `mods` directory into
their existing game-data directory. A StarLancer installation for OpenReliant is
required. The source-code archive is not the intended player download.
