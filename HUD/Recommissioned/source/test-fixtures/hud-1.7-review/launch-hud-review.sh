#!/usr/bin/env bash
# Private review shell. Normal runs stay open until the player exits.
set -euo pipefail
install_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
review_dir="$install_dir/reviews/hud-1.7"
binary="$install_dir/releases/openreliant-main-220affa-linux-x86_64/openreliant"
mode=${1:-}
if [[ -n "$mode" ]]; then shift; fi

if [[ "$mode" == --help || "$mode" == -h ]]; then
  cat <<'HELP'
HUD 1.8 private review
  launch-hud-review.sh                 choose a test
  launch-hud-review.sh portraits       repeating HD portrait, Grendel, HUD panels
  launch-hud-review.sh flight          normal sandbox, Grendel; F2/F3 change ship
  launch-hud-review.sh menu            game menu for Instant Action or campaign
  launch-hud-review.sh legacy          same portrait scene with the native HUD
  launch-hud-review.sh check           verify the copied HUD and engine
Extra OpenReliant options follow the mode, for example --size 1280x720 or --ship 8.
Sound stays enabled: the portrait fixture uses a silent transmission on repeat.
C opens comms; number keys select. 0 saves a screenshot. Escape opens the pause menu.
The test has its own settings, saves and logs. Public release remains held.
HELP
  exit 0
fi

[[ -x "$binary" && -f "$review_dir/runtime.sha256" ]] || {
  printf 'The HUD review installation is incomplete: %s\n' "$review_dir" >&2
  exit 1
}
if [[ "$mode" == check ]]; then
  (cd -- "$review_dir" && sha256sum --quiet --check runtime.sha256)
  printf '%s  %s\n' ed31461a1158f533be31fd8d494c150e1e2c975fc79eb37a1e376366556c8b2a "$binary" | sha256sum --quiet --check -
  printf 'HUD 1.8: all 1,154 runtime files and the unmodified engine match.\n'
  exit 0
fi
if [[ -z "$mode" ]]; then
  if [[ -t 0 ]]; then
    cat <<'MENU'
HUD 1.8 — private review
  1) HD portraits and HUD panels
  2) Normal sandbox flight
  3) Game menu / Instant Action
  4) Legacy HUD and portrait comparison
  q) Quit
MENU
    read -r -p 'Choose a test [1]: ' mode
    mode=${mode:-1}
  else
    mode=portraits
  fi
fi
profile="$review_dir/hud"
scene=()
case "$mode" in
  1|portraits) scene=(--mission 990 --ship 2 --view 2) ;;
  2|flight) scene=(--mission 0 --ship 2 --view 2) ;;
  3|menu) ;;
  4|legacy) profile="$review_dir/legacy"; scene=(--mission 990 --ship 2 --view 2) ;;
  q|quit) exit 0 ;;
  *) printf 'Unknown test: %s. Use --help.\n' "$mode" >&2; exit 2 ;;
esac

unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
mkdir -p -- "$review_dir/logs"
launch_log="$review_dir/logs/$(date +%Y%m%d-%H%M%S)-${mode}-$$.log"
printf 'HUD review: %s\nLog: %s\nScreenshots: %s/screenshots\n' "$mode" "$launch_log" "$profile"
printf 'C: comms; 0: screenshot; Escape: pause/leave. Keep Mod Effects enabled.\n'
{
  printf 'Build: unmodified main 220affa / HUD 1.8\nCommand:'
  printf ' %q' "$binary" "$profile" --no-intro --size 1920x1080 --fps 60 "${scene[@]}" "$@"
  printf '\n'
} > "$launch_log"
set +e
"$binary" "$profile" --no-intro --size 1920x1080 --fps 60 "${scene[@]}" "$@" >> "$launch_log" 2>&1
status=$?
set -e
printf 'Exit status: %s\n' "$status" >> "$launch_log"
if ((status != 0)); then
  printf 'The test ended with status %s. Details: %s\n' "$status" "$launch_log" >&2
else
  printf 'Test closed normally. Log saved.\n'
fi
exit "$status"
