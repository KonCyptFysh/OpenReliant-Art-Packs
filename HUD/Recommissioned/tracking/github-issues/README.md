# GitHub submission drafts

Latest: [0.8.1 review](../../docs/UPSTREAM_0.8.1_REVIEW.md). The user submitted #889-#895. Six are closed; #894 remains open. Do not resubmit these drafts. The stored ZIPs preserve their original pre-freeze API and need the documented naming changes on 0.8.

**Historical API-freeze submissions:** [9 October API-freeze drafts](api-freeze-2026-10-09/README.md), checked on `57c394b5`. The entries below are historical. Do not resubmit closed #793/#794/#832 or the old InvalidFont report.

The user submitted the first two drafts as
[#793](https://github.com/OpenReliant/openreliant/issues/793) and
[#794](https://github.com/OpenReliant/openreliant/issues/794). Both are closed,
with fixes merged in #833 and #831. See `docs/UPSTREAM_HUD_PORT.md` for the new
mod implementation and the remaining #832 work. These fixes are not in published
0.7.0. The third draft has no confirmed submission; its custom-font case now works
on the inspected upstream revision, so recheck before submitting it.

| Draft | Kind | Attach |
|---|---|---|
| [Native HUD replacement and live state](01-hud-replacement-and-state.md) | Feature request | `01-hud-replacement-repro.zip`; optionally `01-radar-overlay.png` |
| [Script image-cache lifecycle](02-script-image-cache.md) | Feature request | `02-script-image-cache-repro.zip` |
| [Custom TTF with HUD base](03-custom-font-hud-base.md) | Bug report | `03-custom-font-hud-base-repro.zip` |

Use each file's first heading as the issue title and the rest as its body. Attach the corresponding ZIP when submitting so its reproduction steps are self-contained. The font report follows the fields in the upstream bug form; select “I don't know” for the original-game comparison because this is an OpenReliant scripting feature. The other two are feature requests, not original-game regressions.

The drafts use the tested v0.7.0 behavior and retain the proposed solutions. Full engineering notes remain under `tracking/issue-drafts/HUD-UPSTREAM-*.md`. The source changes are references, not ready-to-merge patches. Public modpack release remains on hold.

Machine-specific attachment paths and SHA-256 hashes are recorded in `tracking/github-issues/submission-manifest.json`. The ZIPs and screenshot are under ignored `.local/github-issue-attachments/` and are also collected in `.local/github-issues-ready-to-submit.zip`. No runtime art or source exports were modified for this submission pass.
