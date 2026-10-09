# Message to send

Later user-testing findings: [HUD 1.5 follow-up](AUTHOR_NOTES_1.5.md). The notes below describe the previous pass.

I've moved the HUD onto 0.8.1/current main (`220affa`) and updated it for the frozen API. It's now running as a normal drop-in mod, without any engine changes.

The new readings have covered most of what was holding it up. Gun rounds and the paired/split indicator are working, the selected component now picks the right artwork, and the warning lights, device bars, radar transitions and window movement are hooked up. I tested the Wolverine firing from 3,000 down to 2,976 rounds, switching gun modes, and cloak/ECM charge changes.

The one thing I still don't have a proper answer for is the power ball. Replacing the power window hides the animated ball along with the frame and labels. `hud.power` gives me the values, so I've got a triangle showing the allocation for now, but I'd like to keep the original ball. Could we have a way to draw just that at a position/size, or enough documented texture/geometry/state to recreate it? Being able to replace the frame and text while keeping the ball would also work. I've included a tiny probe so you can see what I mean. I realise #509 is about texture size, so this is a related request rather than assuming that issue covers it.

For #894, I haven't seen the missing pieces in the updated fixed-tick captures or the successful live checks so far. The changing-state scene is drawing complete panels again, and the same capture is byte-identical on official 0.8.1 and main. I also have five live Mirage captures through 1:23 looking complete; the longer test stopped on lost window focus, so that is not a completed endurance test. I'm keeping that as a limited retest rather than saying it's definitely fixed everywhere. If it returns I'll send the session log and a screenshot/video, and note whether it flickers or stays broken until restart.

There are still some unfinished schematics and final layout/art checks on my side. Those aren't API blockers. The approved component artwork is preserved, including Ion Cannon at frame 406.

# Attachments and scope

- `power-ball-probe.zip`: standalone ordinary mod, no custom art or engine changes. Set `replace` false/true in the script to compare the native power panel with the replacement. README includes the optional capture mission and command.
- `Recommissioned-HUD-1.4-working-review.zip`: exact deployed HUD runtime, metadata and notices, plus test instructions. Private working candidate; final release held.
- `HUD-0.8-author-evidence.zip`: selected captures/logs, the exact build/runtime hashes, changed editable scripts, this note and the probe. No game archives or executable.

References: [#889](https://github.com/OpenReliant/openreliant/issues/889), [#890](https://github.com/OpenReliant/openreliant/issues/890), [#891](https://github.com/OpenReliant/openreliant/issues/891), [#892](https://github.com/OpenReliant/openreliant/issues/892), [#893](https://github.com/OpenReliant/openreliant/issues/893), [#894](https://github.com/OpenReliant/openreliant/issues/894), [#895](https://github.com/OpenReliant/openreliant/issues/895), and [#509](https://github.com/OpenReliant/openreliant/issues/509).

Prepared locally; nothing submitted automatically.
