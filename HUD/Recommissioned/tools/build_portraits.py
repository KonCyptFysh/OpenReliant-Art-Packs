"""Pack unchanged 480x400 source frames into native films for OpenReliant 0.9.0.

The official engine fits every face film to 120x100 logical pixels. Encode the
source frames directly, without the obsolete shader marker or padded border.
"""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, re, subprocess, tempfile, time
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def info(tool, film):
    output = subprocess.check_output([str(tool), 'fm8', 'info', str(film)], text=True)
    match = re.search(r'(\d+) frames of (\d+) x (\d+)', output)
    assert match, str(film)
    return tuple(map(int, match.groups()))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sltool', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True, help='Extracted original pilot FM8 files, read only')
    parser.add_argument('--sequence', help='Build one named sequence')
    parser.add_argument('--missing', action='store_true', help='Preserve verified existing films and build only missing entries')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    source = ROOT/'source/portraits/frames'
    out = ROOT/'mods/recommissioned-hud'
    # The original archive contains both .fm8 and .FM8. Include both on Linux.
    originals = [p for p in args.native.iterdir() if p.is_file() and p.suffix.lower() == '.fm8']
    native = {p.stem.lower(): p for p in originals}
    assert len(native) == len(originals), 'Case-insensitive native filename collision'
    inventory_path = ROOT/'tracking/portrait-runtime-inventory.json'
    previous = json.loads(inventory_path.read_text()) if inventory_path.exists() else []
    existing = {Path(r['source']).name: r for r in previous}
    source_inventory = ROOT/'tracking/pilot-portrait-source-inventory.json'
    source_records = json.loads(source_inventory.read_text())['records'] if source_inventory.exists() else []
    source_hashes = {r['path']: r['sha256'] for r in source_records}
    folders = sorted(p for p in source.iterdir() if p.is_dir() and (not args.sequence or p.name == args.sequence))
    assert folders
    def build(folder):
        start = time.monotonic()
        original = native[folder.name.lower()]
        frames = sorted((folder/'frames').glob('*.png'))
        assert [p.name for p in frames] == [f'frame_{i:04d}.png' for i in range(1, len(frames)+1)]
        source_digest = hashlib.sha256()
        for p in frames:
            source_digest.update(p.name.encode())
            source_digest.update(p.read_bytes())
        source_sha = source_digest.hexdigest()
        if args.missing and folder.name in existing and existing[folder.name]['encoded_size'] == [480, 400]:
            record = dict(existing[folder.name])
            target = ROOT/record['runtime']
            assert target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == record['sha256'], target
            assert target.name == original.name and len(frames) == record['frames']
            assert hashlib.sha256(original.read_bytes()).hexdigest() == record['native_sha256']
            if 'source_sequence_sha256' in record:
                assert record['source_sequence_sha256'] == source_sha, folder
            else:
                for p in frames:
                    assert hashlib.sha256(p.read_bytes()).hexdigest() == source_hashes[p.relative_to(source).as_posix()], p
            record['source_sequence_sha256'] = source_sha
            assert info(args.sltool, target) == (len(frames), 480, 400)
            return record
        old = info(args.sltool, original)
        assert old == (len(frames), 120, 100), (folder.name, old, len(frames))
        for p in frames:
            with Image.open(p) as im:
                assert im.size == (480, 400), p
        # Stage the film so an interrupted encoder cannot replace a good export.
        with tempfile.TemporaryDirectory(prefix='rc-portrait-') as temporary:
            encoded = Path(temporary)/original.name
            subprocess.run([str(args.sltool), 'fm8', 'encode', str(folder/'frames'), str(encoded)], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            assert info(args.sltool, encoded) == (len(frames), 480, 400)
            target = out/original.name
            target.write_bytes(encoded.read_bytes())
        record = {'source': folder.relative_to(ROOT).as_posix(), 'runtime': target.relative_to(ROOT).as_posix(),
                  'frames':len(frames), 'fps':15, 'content_size':[480,400], 'encoded_size':[480,400],
                  'minimum_openreliant':'0.9.0', 'shader_required':False,
                  'logical_size':[120,100], 'bytes':target.stat().st_size,
                  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                  'native_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
                  'source_sequence_sha256':source_sha,
                  'seconds':round(time.monotonic()-start,2)}
        print(json.dumps({'film':original.name,'frames':len(frames),'seconds':record['seconds']}), flush=True)
        return record
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(build, folders))
    if not args.sequence:
        assert len(records) == len(native)
    else:
        updated = {r['source']: r for r in previous}
        updated.update({r['source']: r for r in records})
        records = sorted(updated.values(), key=lambda r:r['source'])
    inventory_path.write_text(json.dumps(records, indent=2)+'\n')

if __name__ == '__main__': main()
