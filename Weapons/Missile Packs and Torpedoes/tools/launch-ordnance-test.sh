#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -d "$script_dir/releases" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
review_dir="$install_dir/reviews/ordnance-v1"
binary="$install_dir/releases/openreliant-v0.7.0-linux-x86_64/openreliant"
labels=(
    '01 screamer - flight'
    '01 screamer pod - flight'
    '02 raptor - flight'
    '02 raptor POD - flight'
    '03 havoc - flight'
    '04 jackhammer - flight'
    '05 bandit - flight'
    '06 vagabond - flight'
    '07 Solomon POD - flight'
    '07 solomon - flight'
    '08 imp - flight'
    '09 hawk - flight'
    '09 hawk POD - flight'
    '10 torpedo - flight'
    '21 screamer - loadout'
    '21 screamer pod - loadout'
    '22 raptor - loadout'
    '22 raptor POD - loadout'
    '23 havoc - loadout'
    '24 jackhammer - loadout'
    '25 bandit - loadout'
    '26 vagabond - loadout'
    '27 Solomon POD - loadout'
    '27 solomon - loadout'
    '28 imp - loadout'
    '29 hawk - loadout'
    '29 hawk POD - loadout'
    '30 torpedo - loadout'
    '31 fuel pod - loadout'
    'Coalition capital-ship torpedo'
    'Fuel pod - mounted'
    'Alliance capital-ship torpedo'
)
list_items() {
    for i in "${!labels[@]}"; do printf '%2d  %s\n' "$((i+1))" "${labels[$i]}"; done
}
if [[ "${1:-}" == --list ]]; then list_items; exit 0; fi
if [[ "${1:-}" == --help ]]; then
    printf '%s\n' 'Usage: launch-ordnance-test.sh [item number] [OpenReliant options]' 'Without a number, opens an item-selection menu. --list lists all 32 variants.'
    exit 0
fi
choice="${1:-}"
if [[ -n "$choice" ]]; then
    shift
elif command -v kdialog >/dev/null && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    menu=()
    for i in "${!labels[@]}"; do menu+=("$((i+1))" "${labels[$i]}"); done
    choice=$(kdialog --title 'Ordnance material review' --menu 'Choose a missile, pack, fuel pod or torpedo:' "${menu[@]}") || exit 0
else
    list_items
    read -r -p 'Item number (1-32): ' choice
fi
if [[ ! "$choice" =~ ^([1-9]|[12][0-9]|3[0-2])$ ]]; then printf '%s\n' 'Choose an item number from 1 to 32.' >&2; exit 2; fi
if [[ ! -x "$binary" || ! -f "$review_dir/game-data/mods/ordnance-inspection/mission991.dte" || ! -f "$review_dir/game-data/mods/97-ordnance-worn-v1/orord1_hull.png" ]]; then
    printf '%s\n' 'The ordnance review environment is missing. Run the pack’s prepare-review.py first.' >&2
    exit 1
fi
printf 'Reviewing: %s\n' "${labels[$((choice-1))]}"
printf '%s\n' 'Quiet inspection: no enemies or objectives.' 'Press 7 for external orbit; arrow keys rotate; Shift+Up/Down zoom.' 'Close the game and run this launcher again to choose another item.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
mkdir -p -- "$review_dir/logs"
launch_log="$review_dir/logs/item-$choice-$(date +%Y%m%d-%H%M%S).log"
cd -- "$review_dir"
"$binary" "$review_dir/game-data" --size 1920x1080 --fps 60 --mission 991 --ship "ordnance-inspection:item$choice" --view 1 "$@" 2>&1 | tee -- "$launch_log"
