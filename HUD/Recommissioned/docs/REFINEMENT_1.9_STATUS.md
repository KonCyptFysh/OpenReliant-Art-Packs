# Portrait completion status

## HUD 1.9 portrait completion, 9 October 2026 — Git source/runtime update

- Completed all 32 missing archive filenames: 17 new RealBasicVSR x4 video
  restorations (842 frames), 14 exact aliases of existing HD films, and one
  alias of a newly restored film. All 257 native names are now represented.
- The editable collection contains 10,909 PNG frames at 480x400. The original
  225 sequences / 9,353 frames and their runtime films remain byte-identical.
- Runtime additions use the existing 484x404 tagged-film encoding and unchanged
  portrait shader. All 1,556 added frames decode with correct opaque content,
  transparent padding and reserved marker. Counts and native 15 fps timing match.
- The exporter now includes uppercase .FM8 names and can build only missing
  entries while checking existing source/runtime hashes.
- Isolated McGann/Puma captures at 1080p and Stinger at 720p show the existing
  portrait fit and frame placement. The test-only Bridge Officer slot/name is
  used to display these films; no campaign pilot assignment has been changed.
- The author's warning concerns the 0.8 script-command renames, already handled
  in HUD 1.4. A source comparison through current main 319d5ac found no later
  HUD command rename or portrait shader change. Tests still use unmodified
  220affa / 0.8.1; current main was inspected, not installed.

There are 1,187 flat runtime files. Only mod.ini changed among the previous
1,155 files; all sprites, layout, script, shader and approved subtargets
393–409 remain unchanged. The first public beta remains 1.8 / beta.1.
This Git snapshot contains HUD 1.9. No new player release is published; beta.2 and further user review remain pending.
All 1,187 runtime exports are deployed to game-data/mods/HUD and verified
against their repository hashes. The previous flat deployment is backed up
outside the game directory, and all 775 nested source files remain unchanged.
See tracking/portrait-completion-1.9.json for codec and gameplay evidence.
See tracking/portrait-deployment-1.9.json for deployment and backup records.
