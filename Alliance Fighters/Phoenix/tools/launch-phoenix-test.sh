#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ ! -f "$install_dir/game-data/mods/98-phoenix-worn-v1/mission990.dte" ]]; then
    printf '%s\n' 'The Phoenix mod is missing from OpenReliant/game-data/mods/98-phoenix-worn-v1.' >&2
    exit 1
fi
printf '%s\n' 'Phoenix inspection: one ship, no enemies or objectives.' 'Press 7 for external orbit; arrow keys rotate; Shift+Up/Down zoom.'
exec "$install_dir/launch-openreliant.sh" --mission 990 --ship 11 --view 1 "$@"
