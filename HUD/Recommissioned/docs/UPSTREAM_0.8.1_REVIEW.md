# OpenReliant 0.8.1 HUD review

Checked 9 October 2026 against official v0.8.1 and unmodified main `220affa78729a2ce7dcb49602e4f38a4a53d5dc1`.
The release archive matches GitHub's SHA-256. Main is one commit ahead, for campaign ordering, with no HUD API/rendering changes.

| Issue | Upstream | Local evidence and remaining work |
|---|---|---|
| [#889](https://github.com/OpenReliant/openreliant/issues/889) Gun rounds/pairing | Closed, #904 | Wolverine reports 3000 and paired=false under FULL GUNS. Adopt fields in the mod; live firing test pending. |
| [#890](https://github.com/OpenReliant/openreliant/issues/890) Subtarget identity | Closed, #904 | Reliant Engine reports `subtarget_class=engine`. Map approved art by PartClass; turret and laser_turret share the native icon. |
| [#891](https://github.com/OpenReliant/openreliant/issues/891) Lights/device state | Closed, #904 | New light/charge/countermeasure/hit fields observed. Device and flashing gameplay coverage pending. |
| [#892](https://github.com/OpenReliant/openreliant/issues/892) Six font sizes | Closed, #902 | All six pairs match pixel-for-pixel; every row has nonzero text ink. |
| [#893](https://github.com/OpenReliant/openreliant/issues/893) Transition state | Closed, #904 | Window opening values observed up to 1, radar rings and missile places exposed. Mod integration pending. |
| [#894](https://github.com/OpenReliant/openreliant/issues/894) Missing picture pieces | Open | Old state-sweep reproduction now complete after API renames, with no script errors. Author asks for live logs/video and persistence versus flicker if it recurs. |
| [#895](https://github.com/OpenReliant/openreliant/issues/895) Subtarget leaks | Closed, #903 | Current-main ReleaseSafe reproduction exits without the former 30 leaks. |
| [#509](https://github.com/OpenReliant/openreliant/issues/509) Power ball | Open, related scope | No scripted native-ball reuse API found. No comment has been posted on #509. |

The author could not identify the reported missing pieces in the old screenshots, but fixed a plausible GPU upload failure in #963 and requested retesting. The current reproduction is clean; this is not a causal proof of that particular fix or long-session QA.

The stable API rename in [#969](https://github.com/OpenReliant/openreliant/pull/969) affects this pack:

- `colour` to `color`, and `centre` to `center` in styles.
- `hud.guns.synchronised` to `synchronized`.
- `hud.power.guns` to `weapons`, including the table used for the percentage label.
- `hud.objectives.shown` to `showing`.

The unmigrated test produces explicit style errors and disables displays. A test-only copy with these changes runs. One initial unmigrated run also timed out during a simultaneous engine build; do not treat that as a separately established regression.
The production manifest should require the supported 0.8 API when migrated. 0.8.1 also fixes mods' mission scripts when using `--mission`.

The API stability promise starts at 0.8: additions remain possible and breaking changes must be deprecated first. Flashes and window progress are the previous native frame's values. Hit quadrants represent armour hits. Missile selection moves one place at a time; there is no smooth native rotation to reproduce.

No production sources, runtime export, installed game or launcher were changed. All 924 deployed files still match, and the 17 approved subtargets remain unchanged. This review posts nothing upstream; final release remains held.

Evidence and the unpromoted migration preview are under `.local/upstream-0.8.1-review/`; portable hashes and test limits are in `tracking/upstream-0.8.1-review.json`.
