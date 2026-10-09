#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
mode="${1:-cycle}"
case "$mode" in
    stowed) mission=987 ;;
    deployed) mission=986 ;;
    cycle) mission=985 ;;
    launch) mission=984 ;;
    *) printf '%s\n' 'Usage: launch-kamov-test.sh [stowed|deployed|cycle|launch] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/104-kamov-worn-v1/mission$mission.dte" ]]; then
    printf '%s\n' 'The Kamov review mod is missing.' >&2; exit 1
fi
printf '%s\n' "Kamov inspection: $mode, with four carried torpedoes." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == cycle ]]; then printf '%s\n' 'Starts stowed for 8 seconds, then repeats: 4 seconds opening, 8 open, 4 closing, 8 closed.'; fi
if [[ "$mode" == deployed ]]; then printf '%s\n' 'Allow 4 seconds for the native deployment, then the bays remain open.'; fi
if [[ "$mode" == launch ]]; then printf '%s\n' 'Use your Launch Missile control to release each torpedo. After all four launch, the bays stow.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.7.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.7.0 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 45 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
