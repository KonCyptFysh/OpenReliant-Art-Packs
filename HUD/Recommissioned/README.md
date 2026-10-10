# Recommissioned HUD

**Git source/runtime update: HUD 1.10 for official OpenReliant 0.9.0.**
All 257 HD portrait films now use the engine's native sizing. The speaker name
ends at the portrait's lower right, the power panel uses the native animated
ball, and comms columns use the engine's visible text bounds. Panels stay
anchored to the appropriate screen edge on 16:10 displays.

This is a flat folder mod. There is no engine patch or shader override, and
portraits work with MOD EFFECTS disabled. The 10,909 editable portrait frames,
911 runtime PNGs and approved subtargets 393–409 are preserved. Ion Cannon is 406.
Comms remains usable over a portrait, with the shared frame beneath both.

See [current integration](docs/INTEGRATION_0.9_STATUS.md),
[installation](INSTALL.md), [known issues](KNOWN_ISSUES.md) and
[asset status](ASSET_STATUS.md). Full campaign review, unfinished artwork and
final release QA remain pending.

The [public beta download](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/tag/hud-v0.1.0-beta.1)
remains HUD 1.8, tested on 0.8.1. This Git snapshot contains HUD 1.10 for
OpenReliant 0.9.0. The maintainer accepted this working update for publication;
extensive playtesting remains. No new player release or public ZIP has been made.

- [Working exports and local testing](WORKFLOW.md)
- [Release notes](CHANGELOG.md)
- [Maintainer guide](docs/MAINTAINER_GUIDE.md)

A StarLancer installation for OpenReliant is required. The source-code archive
is not the player download. Keep editable sources when replacing runtime files.
