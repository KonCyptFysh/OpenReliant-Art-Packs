#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ ! -f "$install_dir/game-data/mods/117-prowler-worn-v1/mission961.dte" ]]; then
    printf '%s\n' 'The Prowler review mod is missing.' >&2; exit 1
fi
printf '%s\n' 'Prowler revision 1.2: corrected nozzle glow and full-range window power surges.' 'F5 thrust 0/50/100%; F6 small hit; F7 heavy hit; F8 restore; F9 engine-disable.' 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.18.0 is required.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission 961 --ship 30 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
