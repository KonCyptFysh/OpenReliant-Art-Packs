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
    stowed) mission=973 ;;
    deployed) mission=972 ;;
    cycle) mission=971 ;;
    launch) mission=970 ;;
    *) printf '%s\n' 'Usage: launch-galahad-test.sh [stowed|deployed|cycle|launch] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/113-galahad-worn-v1/mission$mission.dte" ]]; then
    printf '%s\n' 'The Galahad review mod is missing.' >&2; exit 1
fi
printf '%s\n' "Galahad inspection: $mode, with two carried torpedoes." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == cycle ]]; then printf '%s\n' 'Starts stowed for 8 seconds, then repeats: 4 seconds opening, 8 open, 4 closing, 8 closed.'; fi
if [[ "$mode" == deployed ]]; then printf '%s\n' 'Allow 4 seconds for the native deployment, then the native deploy parts remain extended.'; fi
if [[ "$mode" == launch ]]; then printf '%s\n' 'Timed review: deploy, release the first torpedo after about 9 seconds, then the second about 7 seconds later. The native deploy parts then stow.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.8.1-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.8.1 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 25 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
