# HUD 1.8 private test shell

Run `<OpenReliant-install>/launch-hud-review.sh` in a terminal.
Choose HD portraits, normal sandbox flight, the game menu, or the same portrait
scene with the native HUD. The game remains open until you leave it. Nothing
in the normal launcher, installed HUD or engine is changed by this shell.

The HUD profile contains the exact 1,154 runtime files extracted from the
private HUD 1.8 ZIP under its distributable recommissioned-hud folder name.
The legacy profile contains only the test mission, so its portraits and HUD
are native. Both use unmodified main 220affa. Settings, saves, cache, logs and
screenshots are separate from the normal game; base game archives are shared
read-only. MOD EFFECTS starts enabled. The shell never publishes anything.

## Tests

- Portraits: a quiet, invulnerable Grendel scene. The Bridge Officer portrait
  uses its matching native name. A 20-second silent transmission repeats every
  25 seconds for fifteen minutes so you can inspect opening, animation, closing and a short gap.
  Other ships' and the player's guns are disabled in this inspection scene.
  Press C while the face is visible, and use 1/2/3 to select comms. Check the
  first period, option alignment, face size, text and comms/damage grids.
- Flight: ordinary mission 0 with the mod and normal weapon behaviour. G cycles
  guns, F selects full guns, Ctrl+G toggles synchronisation, and comma/period
  change missiles. Check bars, counts and text; use F2/F3 for different ships.
- Menu: use Instant Action/campaign to review real speaking pilots, interruptions,
  objectives and gameplay. This starts with a separate copied pilot profile.
- Legacy: the same repeating inspection mission without the HUD mod, for a
  direct comparison. No HD FM8 replacement or shader is present in this profile.

Press 0 to save screenshots under the selected profile's screenshots folder.
Escape opens the pause menu; LEAVE MISSION exits. Logs are under reviews/hud-1.7/logs.

Direct commands:

    ./launch-hud-review.sh portraits
    ./launch-hud-review.sh flight --ship 8
    ./launch-hud-review.sh portraits --size 1280x720
    ./launch-hud-review.sh legacy
    ./launch-hud-review.sh check

Keep sound enabled: disabling the audio system can prevent native portrait
playback. The fixture itself is silent, so silence during it is intentional.
Only an explicitly supplied --screenshot option saves one image and exits.
The supplied shell never adds that option during normal use.

Known release limits remain: the HD shader needs MOD EFFECTS and can conflict
with another device.glsl replacement; broader campaign/shader combinations and
remaining artwork need review. This shell is for testing and is not included
in the public HUD runtime. Public release remains held.

HUD 1.8 uses a single shared comms/portrait frame below the portrait and text.
The speaker name is still at its native position; the requested bottom-right
anchor needs the upstream presentation support recorded in AUTHOR_NOTES_1.8.md.
