#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ ! -f "$install_dir/game-data/mods/103-basilisk-worn-v1/mission988.dte" ]]; then
    printf '%s\n' 'The Basilisk mod is missing from OpenReliant/game-data/mods/103-basilisk-worn-v1.' >&2
    exit 1
fi
printf '%s\n' 'Basilisk inspection: one ship, no enemies or objectives.' 'Press 7 for external orbit; arrow keys rotate; Shift+Up/Down zoom.'
exec "$install_dir/releases/openreliant-v0.8.1-linux-x86_64/openreliant" "$install_dir/game-data" --mission 988 --ship 49 --view 1 --no-sound "$@"
