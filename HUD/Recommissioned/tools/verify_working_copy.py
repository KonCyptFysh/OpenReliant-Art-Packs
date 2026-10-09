#!/usr/bin/env python3
"""Verify source/runtime inventories and approved art, optionally against a live HUD."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(root, live=None):
    records = json.loads((root / 'asset-manifest.json').read_text())
    expected = {r['path'] for r in records}
    actual = {p.relative_to(root).as_posix() for p in (root / 'mods').rglob('*') if p.is_file() or p.is_symlink()}
    assert actual == expected, 'Runtime inventory mismatch'
    for item in records:
        path = root / item['path']
        assert not path.is_symlink() and path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], path
        if path.suffix == '.png':
            data = np.array(Image.open(path).convert('RGBA'))
            assert not np.any(data[data[:, :, 3] == 0, :3]), f'Transparent matte in {path.name}'
        if live:
            assert sha(live / path.name) == item['sha256'], f'Live file differs: {path.name}'
    if live:
        assert {p.name for p in live.iterdir() if p.is_file()} == {Path(p).name for p in expected}, 'Extra flat runtime files'
    sources = json.loads((root / 'source/source-manifest.json').read_text())
    actual_sources = {p.relative_to(root).as_posix() for folder in ('source', 'tools') for p in (root / folder).rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts and p.name != 'source-manifest.json'}
    assert actual_sources == {s['path'] for s in sources}, 'Source inventory mismatch'
    for item in sources:
        path = root / item['path']
        assert not path.is_symlink() and sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], path
    approved = json.loads((root / 'tracking/finished-subtargets.json').read_text())['frames']
    for item in approved:
        source = root / 'source/hud/target/subtargets' / item['source']
        runtime = root / 'mods/recommissioned-hud' / item['runtime']
        assert sha(source) == item['source_sha256'] and sha(runtime) == item['runtime_sha256'], item['frame']
        a = Image.open(source).convert('RGBA'); b = Image.open(runtime).convert('RGBA')
        assert a.size == b.size == (528, 416) and a.tobytes() == b.tobytes(), item['frame']
    return {'runtime_files': len(records), 'source_and_tool_files': len(sources), 'approved_subtargets_unchanged': len(approved),
            'runtime_manifest_sha256': sha(root / 'asset-manifest.json'), 'live_hashes_match': bool(live)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--live', type=Path, help='Optional installed flat HUD directory; never modified')
    args = parser.parse_args()
    print(json.dumps(verify(args.root, args.live), indent=2))
