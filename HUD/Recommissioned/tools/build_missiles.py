#!/usr/bin/env python3
"""Rebuild 90 carousel poses from portable neutral renders and continuous silhouette halos."""
import hashlib
import json
import tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import missile_pipeline as pipeline


def build(repo, output):
    source = repo / 'source/hud/missiles'
    recipes = json.loads((source / 'pose-layout.json').read_text())
    report = []
    with tempfile.TemporaryDirectory(prefix='hud-missiles-') as temporary:
        work = Path(temporary)
        for name, slots in recipes.items():
            neutral = source / name / 'neutral_lod0.png'
            for size in (512, 1024):
                folder = work / name / str(size)
                folder.mkdir(parents=True)
                pipeline.composite_slots(Image.open(neutral), slots, size, folder)
            for slot in slots:
                stem = f"slot_{slot['slot']:02d}_{slot['state']}"
                original_path = source / name / (stem + '.tga')
                original = np.array(Image.open(original_path).convert('RGBA'))
                foreground = np.array(Image.open(work / name / '512' / (stem + '.png')).convert('RGBA'))
                opaque = foreground[:, :, 3] == 255
                if not np.array_equal(original[opaque], foreground[opaque]):
                    raise ValueError(f'Authoring recipe differs from {name}/{stem}')
                # The old export enlarged a halo recovered from the 512px
                # composite independently of the newly rendered 1024px missile.
                # Their edges disagree: bright scenery shows through the gap,
                # making a white, stippled contour. Build the soft dark backing
                # from this exact full-resolution silhouette instead.
                full = Image.open(work / name / '1024' / (stem + '.png')).convert('RGBA')
                halo = full.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
                halo = halo.point(lambda value: round(value * 0.60))
                shadow = Image.new('RGBA', full.size, (0, 0, 0, 0))
                shadow.putalpha(halo)
                shadow.alpha_composite(full)
                assert np.array_equal(np.array(shadow)[np.array(full)[:, :, 3] == 255],
                                      np.array(full)[np.array(full)[:, :, 3] == 255])
                pixels = np.array(shadow)
                pixels[pixels[:, :, 3] == 0, :3] = 0
                dest = output / f'rc_missiles_{name}_{stem}.png'
                Image.fromarray(pixels).save(dest)
                report.append({'file': dest.name, 'neutral_master': neutral.relative_to(repo).as_posix(),
                               'master_sha256': hashlib.sha256(neutral.read_bytes()).hexdigest(),
                               'old_size': [512, 512], 'new_size': [1024, 1024],
                               'opaque_recipe_matches_source': True,
                               'outline': 'continuous silhouette-derived halo: 9px max filter, 3px blur, 60 percent alpha',
                               'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
            print(f'{name}: 10 poses at 1024', flush=True)
    return report
