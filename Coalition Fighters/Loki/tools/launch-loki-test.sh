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
    folded) mission=983 ;;
    fighting) mission=982 ;;
    cycle) mission=981 ;;
    *) printf '%s\n' 'Usage: launch-loki-test.sh [folded|fighting|cycle] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/105-loki-worn-v1/mission$mission.dte" ]]; then
    printf '%s\n' 'The Loki review mod is missing.' >&2; exit 1
fi
printf '%s\n' "Loki inspection: $mode, native articulated leg and foot poses." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == cycle ]]; then printf '%s\n' 'Starts folded, then repeatedly moves to fighting position and folds back. Each movement takes four seconds with pauses between.'; fi
if [[ "$mode" == fighting ]]; then printf '%s\n' 'Allow four seconds for the native animation; the fighting pose then holds.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.8.1-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.8.1 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 65 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
