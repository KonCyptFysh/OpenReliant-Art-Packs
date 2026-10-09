#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ ! -f "$install_dir/game-data/mods/108-lagg-worn-v1/mission978.dte" ]]; then
    printf '%s\n' 'The Lagg mod is missing from OpenReliant/game-data/mods/108-lagg-worn-v1.' >&2
    exit 1
fi
printf '%s\n' 'Lagg inspection: one ship, no enemies or objectives.' 'Press 7 for external orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.8.1-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.8.1 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission 978 --ship 44 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
