# Known issues and tracked work

## HUD 1.9 portrait additions

All 257 archive filenames now have HD exports. Previously unused alternatives
remain unused unless a pilot is deliberately assigned to them; this pass adds
assets, not campaign casting changes. The existing shader dependency and native
speaker-name placement limitations remain. Full campaign review of the new
films is pending. The instant-action ammunition report remains deferred.

## First public beta — 9 October 2026

HUD revision 1.8 is approved for this beta as-is. Artwork, script and shader
bytes match the tested candidate. Release metadata and licence notices were
added for publication. The earlier release hold below is historical; final
stable release and broader QA remain pending.

## Current HUD 1.8

The shared comms/portrait frame and visible-ink comms columns are corrected
and tested. A single frame sits beneath portrait and text; damage uses the
same vertical grid placement. See [current evidence](docs/REFINEMENT_1.8_STATUS.md).

Moving the active portrait speaker name independently is still blocked by the
native instrument API. The [author request](docs/AUTHOR_NOTES_1.8.md) now asks
for consistent controls for all native HUD names/titles/labels, including
position/anchor, alignment, size and selective text replacement. Many panel
readings are already exposed and the request explicitly acknowledges them.
The speaker name remains native and may overlap the COMMS heading.

The 1.7 HD shader requirements/conflicts, t_grendel ammunition, native power
ball, unfinished art and broader QA remain open. Public release is held.
Older pass notes below are historical; their completion claims are superseded
by the current status, including the additional comms alignment fix in 1.8.

## HUD 1.7 portrait workaround

The HD portraits now work through a flat mod shader and native FM8 exports on
main 220affa. This supersedes older notes saying that no HD films are deployed.
It is version-dependent, needs MOD EFFECTS and cannot coexist with a different
device.glsl override without merging the shader changes. Raw HUD bounds remain
oversized; public release and broader QA are held. See
[current evidence and limits](docs/REFINEMENT_1.7_STATUS.md) and
[updated author notes](docs/AUTHOR_NOTES_1.7.md).

## Current HUD 1.6 panel pass

Objectives spacing/font size and comms numbering/alignment are fixed in the
working candidate. Comms intentionally remains usable over portraits, as
verified with the mod disabled and requested by the maintainer.
No comms-blocking engine request is needed.

HD portrait sizing is separate: quarter-scale layout resizes the film but
also shrinks its frame/emblem. A complete scripted radio is not ruled out,
but is unimplemented and unverified. HD films remain undeployed. See
[current status](docs/REFINEMENT_1.6_STATUS.md) and
[qualified author notes](docs/AUTHOR_NOTES_1.6.md).
Public release and prior open art/QA work remain held.

## Current HUD 1.5 follow-up

Startup/missile legacy flashes and missile halo gaps are fixed in the mod.
The name now sits on the upper missile grid. Gun pairing is verified and retains
legacy behavior (Ctrl+G; no pair bar in FULL GUNS).

Open upstream items: the t_grendel ammunition readout, and radio film sizing for
480x400 portraits. HD portraits are not deployed. See
[current pass](docs/REFINEMENT_1.5_STATUS.md) and [author notes](docs/AUTHOR_NOTES_1.5.md).
The prior power-ball, unfinished artwork, #894 broader review and release-QA work
below remain. Public release is held.

The HUD 1.4 section below records the earlier integration baseline.

## Current HUD 1.4, 9 October 2026

Stable API migration and new-reading integration are complete and deployed on
unmodified main `220affa`. The previous six upstream requests are delivered and
used by the mod. Details: [integration](docs/INTEGRATION_0.8_STATUS.md) and
[author notes](docs/AUTHOR_NOTES_0.8.md).

- **Native power ball:** supported reuse inside a replacement panel is still absent. The allocation triangle remains a placeholder; a small current-build probe is ready for the author.
- **#894:** no missing pieces seen in current successful retests; keep the issue open pending broader review and any recurrence log/video. Do not claim a proved GPU/cache cause.
- **Release QA:** full campaigns, dense combat, localization, repeated alt-tab/relaunch, dedicated armour-hit and spectral-device coverage, and user layout approval remain.
- **Artwork:** 17 large-schematic jobs and fuel-pod frame 410 remain unfinished. Native fallback is retained. Completed frames 393–409, including Ion Cannon 406, are unchanged.
- **Native presentation:** messages, prompts and radio portraits remain native; one-frame presentation-readout latency is documented upstream. Missile positions change in steps by native design.

Public release remains held. The old InvalidFont, native replacement, image-cache,
font-size and shutdown-leak reports should not be resubmitted as current blockers.

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
