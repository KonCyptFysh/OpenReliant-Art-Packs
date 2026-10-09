#!/usr/bin/env python3
"""Assemble isolated diagnostic mods from preserved scripts and runtime exports."""
from pathlib import Path
import argparse,json,shutil
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('output',type=Path,help='New temporary directory; never the live mods folder')
args=parser.parse_args()
if args.output.exists():parser.error('Output must not already exist')
args.output.mkdir(parents=True)
for case in ('overlay','memory','count','font'):
    source=ROOT/'source/compatibility-probes'/case
    target=args.output/case/'hudprobe';target.mkdir(parents=True)
    for name in ('mod.ini','probe.luau'):shutil.copy2(source/name,target/name)
    for asset in json.loads((source/'assets.json').read_text()):
        shutil.copy2(ROOT/'mods/recommissioned-hud'/asset['runtime_source'],target/asset['probe_name'])
print('Prepared four separate diagnostic mods. Enable only one at a time in an isolated test installation.')
