#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
mod_dir="$install_dir/game-data/mods"
if [[ ! -x "$engine" || ! -f "$mod_dir/119-reliant-worn-v1/mission957.dte" ]]; then
    printf '%s\n' 'The Reliant flight review mod and official OpenReliant 0.18.0 are required.' >&2
    exit 1
fi
mods=119-reliant-worn-v1
# Use the existing Patriot artwork when installed; the mission also works with
# the original Patriot. These are separate packs, not copied into the Reliant pack.
for extra in 96-patriot-worn-v1 118-patriot-cockpit-v1; do
    if [[ -f "$mod_dir/$extra/mod.ini" ]]; then mods+=",$extra"; fi
done
printf '%s\n' \
    'Patriot launch from ANS Reliant. Normal flight controls and HUD; no enemies.' \
    'After launch, the Reliant doors repeatedly open, hold, close and hold.' \
    'C: COMMS > 1 Base > 1 Permission to land. Doors finish closing before native landing.' \
    'A selects Reliant. W selects the nearest friendly. Backspace stops; +/- adjusts throttle.' \
    '1 cockpit view; 6 target view; 7 external view; 0 screenshot. F1 shows your bindings.' \
    'Sound is enabled for bridge comms. Add --no-sound for a silent review.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
exec "$engine" "$install_dir/game-data" --mods "$mods" --mission 957 --ship 7 --view 0 --size 1920x1080 --fps 60 "$@"
