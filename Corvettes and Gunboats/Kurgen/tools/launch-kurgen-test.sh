#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ ! -f "$install_dir/game-data/mods/116-kurgen-worn-v1/mission962.dte" ]]; then
    printf '%s\n' 'The Kurgen review mod is missing.' >&2; exit 1
fi
printf '%s\n' 'Kurgen lighting PoC: F5 thrust 0/50/100%; F6 small hit; F7 heavy hit; F8 restore armour; F9 engines on/off.' 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\n' 'Official OpenReliant 0.18.0 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission 962 --ship 60 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
