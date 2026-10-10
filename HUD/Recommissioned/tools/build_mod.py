#!/usr/bin/env python3
"""Export the selected HUD sources to a flat working mod; never deploy or release it."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from build_missiles import build as build_missiles
from build_script import build as build_script

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')

def export(root, output):
    plan = json.loads((root / 'tools/hud-export-plan.json').read_text())
    output = output.resolve()
    if output.is_relative_to((root / 'source').resolve()):
        raise ValueError('Export cannot overwrite source files')
    output.mkdir(parents=True, exist_ok=True)
    metadata = sorted(p.name for p in (root / 'source/runtime-meta').iterdir() if p.is_file())
    expected = {name for item in plan for name in item['outputs']} | {'hud_layout.ini', 'recommissioned.luau', *metadata}
    # Films are exported separately with build_portraits.py and upstream sltool.
    # Reuse only the inventoried exports during an ordinary layout/art rebuild.
    portrait_inventory = root / 'tracking/portrait-runtime-inventory.json'
    portraits = json.loads(portrait_inventory.read_text()) if portrait_inventory.exists() else []
    expected |= {Path(item['runtime']).name for item in portraits}
    unexpected = {p.name for p in output.iterdir()} - expected
    if unexpected:
        raise ValueError(f'Uninventoried output files; review before removing: {sorted(unexpected)}')
    for name in expected:
        if (output / name).is_symlink():
            raise ValueError(f'Output must be a regular copy: {name}')
    audit = []
    with tempfile.TemporaryDirectory(prefix='hud-export-') as temp:
        stage = Path(temp)
        for item in plan:
            if not item['outputs'] or item['recipe'] == 'missile-1024':
                continue
            source = root / item['source']
            original = np.array(Image.open(source).convert('RGBA'))
            pixels = original.copy()
            mask = pixels[:, :, 3] == 0
            changed = int(np.count_nonzero(mask & np.any(pixels[:, :, :3] != 0, axis=2)))
            pixels[mask, :3] = 0
            assert np.array_equal(pixels[:, :, 3], original[:, :, 3])
            assert np.array_equal(pixels[~mask], original[~mask])
            if item['recipe'] == 'rgba-transparent-rgb-zero-split-fill':
                lit = np.array(Image.open(root / item['lit_source']).convert('RGBA'))
                assert lit.shape == pixels.shape
                lit[lit[:,:,3] == 0, :3] = 0
                pixels[item['split_row']:] = lit[item['split_row']:]
            # Native gunnery mirrors its floor vertically. Export that draw
            # orientation separately because hud.picture has no mirror option.
            # This only reverses rows; the editable master and other exports stay intact.
            mirrored = item['recipe'] == 'rgba-transparent-rgb-zero-flip-vertical'
            if mirrored:
                pixels = pixels[::-1].copy()
            if item['recipe'] == 'rgba-transparent-rgb-zero-flip-horizontal':
                pixels = pixels[:, ::-1].copy()
            if item['recipe'] == 'rgba-transparent-rgb-zero-crop':
                x0, y0, x1, y1 = item['crop']
                pixels = pixels[y0:y1, x0:x1].copy()
            for name in item['outputs']:
                Image.fromarray(pixels).save(stage / name)
            audit.append({'source': item['source'], 'outputs': item['outputs'],
                          'invisible_pixels_cleaned': changed, 'alpha_and_visible_rgba_preserved': True,
                          'recipe': item['recipe'],
                          **({'crop': item['crop']} if 'crop' in item else {}),
                          **({'lit_source': item['lit_source'], 'split_row': item['split_row']} if 'lit_source' in item else {}),
                          **({'draw_orientation': 'vertical-mirror'} if mirrored else {})})
        missile_report = build_missiles(root, stage)
        build_script(root, stage)
        shutil.copy2(root / 'source/hud/hud_layout.ini', stage / 'hud_layout.ini')
        for name in metadata:
            shutil.copy2(root / 'source/runtime-meta' / name, stage / name)
        for item in portraits:
            film = root / item['runtime']
            if not film.exists() or digest(film) != item['sha256']:
                raise ValueError('Portrait export missing or changed; run build_portraits.py first: ' + str(film))
            shutil.copy2(film, stage / film.name)
        approved = json.loads((root / 'tracking/finished-subtargets.json').read_text())['frames']
        for item in approved:
            if digest(stage / item['runtime']) != item['runtime_sha256']:
                raise ValueError(f"Approved subtarget changed: {item['frame']}")
        assert {p.name for p in stage.iterdir()} == expected
        for path in stage.iterdir():
            target = output / path.name
            shutil.copy2(path, target)
            assert digest(path) == digest(target)
    records = [{'path': 'mods/recommissioned-hud/' + p.name, 'bytes': p.stat().st_size, 'sha256': digest(p)}
               for p in sorted(output.iterdir())]
    if output == (root / 'mods/recommissioned-hud').resolve():
        previous = (root / 'asset-manifest.json').read_text()
        write_json(root / 'asset-manifest.json', records)
        if previous != (root / 'asset-manifest.json').read_text():
            release = json.loads((root / 'release.json').read_text())
            release.update(status='hold', asset_manifest_sha256=None,
                           hold_reason='Working HUD candidate; user testing, official engine compatibility and final release QA remain pending.')
            write_json(root / 'release.json', release)
            validation = json.loads((root / 'validation.json').read_text())
            validation.update(status='pending', asset_manifest_sha256=None, checks=[])
            write_json(root / 'validation.json', validation)
        write_json(root / 'tracking/sprite-export-audit.json', audit)
        write_json(root / 'tracking/missile-export-audit.json', missile_report)
    print(f'Exported {len(records)} runtime files; 17 approved subtargets unchanged')
    return records

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, help='Default: repository mods/recommissioned-hud')
    args = parser.parse_args()
    export(args.root.resolve(), args.output or args.root / 'mods/recommissioned-hud')
