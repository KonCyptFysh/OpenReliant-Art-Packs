# API-freeze feedback probes, 9 October 2026

Unmodified upstream main 57c394b5bb7e9ddc5d171db07f039449854d98c1, Zig 0.17.0 ReleaseSafe, Linux x86_64.
These are independent diagnostic inputs, not part of the playable HUD export.
gun-state, subtarget-state, light-state and presentation-state are read-only
player observers. Suggested missing field names deliberately return nil.
Only subtarget-state supplies a new mission fixture, selecting Reliant component
4 (Engine); the numeric component index is not a semantic part class.

The six-size font probe is preserved under ../main-86aa967/font-sizes.
The rendering state sweep is preserved under ../main-30163d9/state-sweep;
it deliberately modifies simulation state and belongs only in an isolated test.
Mission 991 sources elsewhere under source/test-fixtures remain unchanged.

Current issue drafts: tracking/github-issues/api-freeze-2026-10-09.
Prepared ZIPs/evidence: .local/api-freeze-2026-10-09/ready-to-submit.
No issue has been posted by this preparation pass. Public release remains held.

Mission generators derive from OpenReliant's MPL-2.0 source; the licence is
included in each attachment. Generated DTE files need no compiler to run.
To regenerate the named-component mission with the tested checkout/compiler:

    zig run --dep openreliant -Mroot=subtarget-scene.zig -Mopenreliant=ENGINE_SOURCE/src/root.zig -- mission991.dte

Keep approved subtarget art 393–409 unchanged; Ion Cannon is frame 406.
