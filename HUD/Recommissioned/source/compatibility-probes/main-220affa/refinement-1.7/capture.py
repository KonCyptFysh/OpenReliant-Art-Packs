"""Capture an isolated mission and retain exact build/runtime evidence."""
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--binary', type=Path, required=True)
parser.add_argument('--game', type=Path, default=root / 'test-game')
parser.add_argument('--view', default='2')
parser.add_argument('--ship', default='4')
parser.add_argument('--mission', default='991')
parser.add_argument('--size', default='1920x1080')
parser.add_argument('--ticks', default='80')
parser.add_argument('--sound', action='store_true')
parser.add_argument('--no-mods', action='store_true')
parser.add_argument('--gamma-space', action='store_true')
args = parser.parse_args()
env = os.environ.copy()
env.pop('XDG_ACTIVATION_TOKEN', None)
env['SDL_VIDEODRIVER'] = 'x11'
screenshot = root / 'evidence' / (args.name + '.png')
log = screenshot.with_suffix('.log')
command = [str(args.binary.resolve()), str(args.game.resolve()), '--mission', args.mission,
           '--ship', args.ship, '--view', args.view, '--size', args.size, '--no-sound',
           '--screenshot-ticks', args.ticks, '--screenshot', str(screenshot)]
if args.sound:
    command.remove('--no-sound')
    env['SDL_AUDIODRIVER']='dummy'
if args.no_mods:
    command.append('--no-mods')
if args.gamma_space:
    command.append('--gamma-space')
start = time.monotonic()
with log.open('w') as stream:
    result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=240)
record = {'command': command, 'exit_code': result.returncode, 'seconds': round(time.monotonic()-start, 1),
          'binary_sha256': hashlib.sha256(args.binary.read_bytes()).hexdigest(),
          'capture': screenshot.name if screenshot.exists() else None,
          'diagnostics': [line for line in log.read_text().splitlines()
                          if any(x in line.lower() for x in ['error', 'warning(scripts)', 'recommissioned hud:', 'screenshot', 'hud_cache', 'hud_state', 'hud_bounds', 'hud_replaced', 'hud_api', 'hud_freeze'])]}
if screenshot.exists():
    record['capture_sha256'] = hashlib.sha256(screenshot.read_bytes()).hexdigest()
screenshot.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2), flush=True)
assert result.returncode == 0 and screenshot.exists()
