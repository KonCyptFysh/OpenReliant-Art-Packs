#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
mode="${1:-stowed}"
case "$mode" in
    stowed) mission=964 ;;
    launch) mission=963 ;;
    *) printf '%s\n' 'Usage: launch-scimitar-test.sh [stowed|launch] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/115-scimitar-worn-v1/mission$mission.dte" ]]; then
    printf '%s\n' 'The Scimitar review mod is missing.' >&2; exit 1
fi
printf '%s\n' "Scimitar inspection: $mode, with two carried torpedoes." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == launch ]]; then printf '%s\n' 'Timed review: release the first torpedo after about 9 seconds and the second roughly 7 seconds later. The native launch mounts are fixed.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.18.0 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 48 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
