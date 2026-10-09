"""Pack unchanged 480x400 source frames into native films with a shader size tag.

Requires Pillow and the unmodified upstream sltool. Four transparent pixels of
padding at right/bottom identify our 484x404 films without matching arbitrary
480x400 textures. The shader shows only the original content at 120x100 logical
pixels. Padding is generated in temporary storage, never in editable sources.
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
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    source = ROOT/'source/portraits/frames'
    out = ROOT/'mods/recommissioned-hud'
    native = {p.stem.lower(): p for p in args.native.glob('*.fm8')}
    folders = sorted(p for p in source.iterdir() if p.is_dir() and (not args.sequence or p.name == args.sequence))
    assert folders
    def build(folder):
        start = time.monotonic()
        original = native[folder.name.lower()]
        frames = sorted((folder/'frames').glob('*.png'))
        old = info(args.sltool, original)
        assert old == (len(frames), 120, 100), (folder.name, old, len(frames))
        with tempfile.TemporaryDirectory(prefix='rc-portrait-') as temporary:
            for p in frames:
                with Image.open(p) as im:
                    assert im.size == (480, 400)
                    packed = Image.new('RGBA', (484, 404))
                    packed.paste(im.convert('RGBA'), (0, 0))
                    packed.save(Path(temporary)/p.name, compress_level=1)
            target = out/original.name
            subprocess.run([str(args.sltool), 'fm8', 'encode', temporary, str(target)], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert info(args.sltool, target) == (len(frames), 484, 404)
        record = {'source': folder.relative_to(ROOT).as_posix(), 'runtime': target.relative_to(ROOT).as_posix(),
                  'frames':len(frames), 'fps':15, 'content_size':[480,400], 'encoded_size':[484,404],
                  'logical_size':[120,100], 'bytes':target.stat().st_size,
                  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                  'native_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
                  'seconds':round(time.monotonic()-start,2)}
        print(json.dumps({'film':original.name,'frames':len(frames),'seconds':record['seconds']}), flush=True)
        return record
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(build, folders))
    if not args.sequence:
        assert len(records) == len(native)
        (ROOT/'tracking/portrait-runtime-inventory.json').write_text(json.dumps(records, indent=2)+'\n')

if __name__ == '__main__': main()
