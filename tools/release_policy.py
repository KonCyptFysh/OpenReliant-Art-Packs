#!/usr/bin/env python3
"""Reject private artwork and development files in a publication tree.

The index is checked by default, so ignored local work is never mistaken for
published content. --ref checks an exact commit/tag before it is pushed.
"""
import argparse
from pathlib import PurePosixPath
import re
import subprocess
import sys

CATEGORIES = {
    'Alliance Capital Ships', 'Alliance Fighters', 'Coalition Capital Ships',
    'Coalition Fighters', 'Corvettes and Gunboats', 'Environment and Planets',
    'HUD', 'Torpedo Bombers', 'Uncategorised Ships', 'Weapons',
}
PRIVATE_DIRS = {'source', 'sources', 'authoring', 'history', 'originals', 'masters',
                'dev', 'testing', 'test-fixtures', 'review', 'work', '.local',
                '.agents', '.codex', '__pycache__'}
MASTER_EXTENSIONS = {'.blend', '.psd', '.psb', '.kra', '.ora', '.xcf', '.npy',
                     '.fbx', '.obj', '.mtl', '.spp', '.sbs', '.sbsar'}
ROOT_DIRS = {'docs', 'tools', 'tracking', '.github', '.githooks'}

def private_reason(name):
    p = PurePosixPath(name)
    parts = p.parts
    if any(x.lower() in PRIVATE_DIRS for x in parts[:-1]):
        return 'local authoring/development directory'
    if p.suffix.lower() in MASTER_EXTENSIONS or re.search(r'\.blend\d+$', p.name.lower()):
        return 'editable master'
    if p.name.lower() == 'source-manifest.json':
        return 'private source inventory'
    if parts[0] in CATEGORIES:
        if len(parts) > 3 and parts[2] != 'mods':
            return 'per-asset development material'
        if len(parts) == 3 and p.name == 'WORKFLOW.md':
            return 'local authoring workflow'
        if len(parts) == 3 and p.suffix.lower() not in {'.md', '.json', '.txt'}:
            return 'binary outside the runtime mod'
    elif len(parts) > 1 and parts[0] not in ROOT_DIRS:
        return 'unapproved publication directory'
    if p.suffix.lower() in {'.png', '.tga', '.glb', '.shp', '.fm8', '.mp4', '.zip'}:
        if parts[0] != 'docs' and 'mods' not in parts:
            return 'artwork outside a runtime mod or public gallery'
    return None

def tracked_paths(ref=None):
    args = ['git', 'ls-tree', '-r', '--name-only', '-z', ref] if ref else ['git', 'ls-files', '-z']
    return [s for s in subprocess.check_output(args).decode().split('\0') if s]

def check(ref=None, history=False):
    files = tracked_paths(ref)
    if history:
        if not ref:
            raise ValueError('--history requires an exact --ref')
        raw = subprocess.check_output(['git', 'log', ref, '--pretty=format:', '--name-only', '-z'])
        files = sorted(set(files) | {p.lstrip('\n') for p in raw.decode().split('\0') if p.lstrip('\n')})
    bad = [(name, private_reason(name)) for name in files if private_reason(name)]
    if bad:
        for name, reason in bad[:30]:
            print(f'{reason}: {name}', file=sys.stderr)
        raise ValueError(f'{len(bad)} private/development files would be published. Keep masters in the local artwork workspace.')
    print(f'Release-only publication check passed: {len(files)} paths')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', help='Check an exact commit or tag instead of the staged index')
    parser.add_argument('--history', action='store_true', help='Also reject private paths in all reachable ancestors')
    args = parser.parse_args()
    try:
        check(args.ref, args.history)
    except (ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
