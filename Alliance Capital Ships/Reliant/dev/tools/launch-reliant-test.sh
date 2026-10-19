#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ "${1:-}" == "--flight" ]]; then
    shift
    exec "$script_dir/launch-reliant-flight-test.sh" "$@"
fi
mission=959
if [[ "${1:-}" == "--doors" ]]; then mission=958; shift; fi
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" || ! -f "$install_dir/game-data/mods/119-reliant-worn-v1/mission959.dte" ]]; then
    printf '%s\n' 'The Reliant review mod and official OpenReliant 0.18.0 are required.' >&2; exit 1
fi
printf '%s\n' 'Reliant detail camera: arrows orbit, Shift+Up/Down zoom, Ctrl+arrows pan, PgUp/PgDn focus, Home reset, F4 standard/detail, 0 screenshot. Alt+arrows rotate ship, Alt+,/. roll, Alt+Home reset ship.' 'F5 thrust 0/50/100%, F6 minor hull hit, F7 heavy hit, F8 restore hull.' 'F9 disable engines, F10 critical hull, F12 destroy engine component (restart to restore).' 'Use --doors for the native open-hold-close-hold-reopen inspection sequence.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
exec "$engine" "$install_dir/game-data" --mods 119-reliant-worn-v1 --mission "$mission" --ship 12 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
