# Known issues and tracked work

## Current review, 9 October 2026

Official **0.8.1** contains the requested gun, subtarget, warning/device and
transition readings, plus the font and shutdown-leak fixes. Main `220affa`
is one campaign-ordering commit ahead; its HUD code is unchanged from the release.
See [the verified review](docs/UPSTREAM_0.8.1_REVIEW.md) and
[test records](tracking/upstream-0.8.1-review.json).

The deployed HUD 1.3 still uses the previous development API. It needs the
five naming changes and new-reading integration before normal use on 0.8.1.
Only isolated test copies were adapted in this review; runtime export, installed
game, launcher and approved subtargets 393-409 are unchanged. Ion Cannon is 406.

- **HUD-MIGRATION-08:** migrate authoritative sources/manifest, rebuild, test and
  deploy. New gun rounds/pairing, part class, light/device state and animation
  values remove those upstream API blockers; the mod still needs to use them.
- **HUD-RENDER-01 / #894:** still open upstream. The old changing-state reproduction
  is visually complete on both new builds. Long live gameplay, and whether any
  recurrence persists or flickers, remain unverified. Do not claim the report closed.
- **Power ball:** #509 remains open; scripted reuse is not provided. The mod's
  allocation triangle remains a placeholder; native presentation is an option.
- **Gameplay/presentation QA:** devices and flashing in action, target changes,
  dense radar, long missions, resizing, localization and user artwork/layout review.
  New flashes/window progress describe the previous native draw, a frame behind;
  missile places change in steps. Hull/armour hit flashes are not shield-hit flashes.
- **Artwork:** 17 large-schematic jobs and fuel-pod frame 410 remain unfinished.
  Existing messages/prompts/radio portraits remain native. Public release is held.

The six-size font test now matches its controls at every size, and current-main
ReleaseSafe reports no leaks in the selected-component shutdown reproduction.
The old InvalidFont draft and resolved #793/#794/#832 should not be resubmitted.

| ID | Work | Type | Milestone |
|---|---|---|---|
| [HUD-ART-BERISCEM](tracking/issue-drafts/HUD-ART-BERISCEM.md) | BERISCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-COMMSCEM](tracking/issue-drafts/HUD-ART-COMMSCEM.md) | COMMSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-CYCLSCEM](tracking/issue-drafts/HUD-ART-CYCLSCEM.md) | CYCLSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-CZADSCEM](tracking/issue-drafts/HUD-ART-CZADSCEM.md) | CZADSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-DREISCEM](tracking/issue-drafts/HUD-ART-DREISCEM.md) | DREISCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-FUELSCEM](tracking/issue-drafts/HUD-ART-FUELSCEM.md) | FUELSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-KRESSCEM](tracking/issue-drafts/HUD-ART-KRESSCEM.md) | KRESSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-NANNSCEM](tracking/issue-drafts/HUD-ART-NANNSCEM.md) | NANNSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-PACKSCEM](tracking/issue-drafts/HUD-ART-PACKSCEM.md) | PACKSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-PCORSCEM](tracking/issue-drafts/HUD-ART-PCORSCEM.md) | PCORSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-RESBSCEM](tracking/issue-drafts/HUD-ART-RESBSCEM.md) | RESBSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-SDROSCEM](tracking/issue-drafts/HUD-ART-SDROSCEM.md) | SDROSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-SHAVSCEM](tracking/issue-drafts/HUD-ART-SHAVSCEM.md) | SHAVSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-SHERSCEM](tracking/issue-drafts/HUD-ART-SHERSCEM.md) | SHERSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-SSATSCEM](tracking/issue-drafts/HUD-ART-SSATSCEM.md) | SSATSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-STALSCEM](tracking/issue-drafts/HUD-ART-STALSCEM.md) | STALSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-ULYSSCEM](tracking/issue-drafts/HUD-ART-ULYSSCEM.md) | ULYSSCEM: finish schematic artwork | unfinished-art | HUD art completion |
| [HUD-ART-410](tracking/issue-drafts/HUD-ART-410.md) | Fuel pod frame 410: review the missing replacement | needs-review | HUD art completion |
| [HUD-COMPAT-01](tracking/issue-drafts/HUD-COMPAT-01.md) | Deliver the authored HUD as a drop-in mod on official OpenReliant | compatibility | 0.1.0-beta.1 |
| [HUD-QA-01](tracking/issue-drafts/HUD-QA-01.md) | Run the OpenReliant HUD release checks | testing | 0.1.0-beta.1 |
| [HUD-REVIEW-01](tracking/issue-drafts/HUD-REVIEW-01.md) | Reassess old text and composite backlog for OpenReliant | needs-review | Later review |

## Resolved historical items

[HUD-ART-399](tracking/issue-drafts/HUD-ART-399.md): the maintainer confirmed frame 399 is finished as part of the completed 393–409 set. All 17 installed images match the approved TGA sources pixel-for-pixel. This former crop review is closed and must not be imported as an open issue.

[HUD-FIX-01](tracking/issue-drafts/HUD-FIX-01.md): HUD 1.1 is implemented, exported and locally verified. The 589 repository/runtime hashes match. Fine missile texture detail remains limited by the neutral renders; release coverage and compatibility remain the open QA/compatibility items.

## Upstream compatibility drafts

The user submitted the first two requests; both are closed with fixes merged.
The historical third draft is retired. See the historical
[0.7.0 audit](docs/STOCK_0.7_HUD_COMPATIBILITY.md) and the current
[upstream port](docs/UPSTREAM_HUD_PORT.md).

- [HUD-UPSTREAM-01 / #793](https://github.com/OpenReliant/openreliant/issues/793): replacement and initial state API merged in #833; remaining state merged in #864/#866/#868.
- [HUD-UPSTREAM-02 / #794](https://github.com/OpenReliant/openreliant/issues/794): cache eviction and 128 MiB budget merged in #831.
- [HUD-UPSTREAM-03](tracking/issue-drafts/HUD-UPSTREAM-03.md): custom TTF with HUD base; current native-font workaround works.

Submission-ready wording and attachment instructions: [GitHub drafts](tracking/github-issues/README.md). The longer notes above remain the technical reference.
