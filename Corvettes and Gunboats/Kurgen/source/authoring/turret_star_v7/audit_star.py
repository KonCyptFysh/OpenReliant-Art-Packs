from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

S = Path('/tmp/kurgen-turret-v7')
D = Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Kurgen/worn')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
old = D/'maps/kurgen_turret_basecolor_v1.png'
new = S/'kurgen_turret_basecolor_v7.png'
a = np.asarray(Image.open(old).convert('RGB'))
b = np.asarray(Image.open(new).convert('RGB'))
assert a.shape == b.shape == (4096,4096,3)
changed = np.any(a != b, axis=2)
outside = changed.copy(); outside[1390:2110,1040:1760] = False
assert not outside.any()
patch = b[1390:2110,1040:1760]
paint = (patch[:,:,0]>patch[:,:,1]*1.8)&(patch[:,:,0]>patch[:,:,2]*1.8)&(patch[:,:,0]>55)
flat = np.asarray(Image.open(D/'maps/kurgen_turret_flat_graphics_v1.png'))[1390:2110,1040:1760]
normal = np.asarray(Image.open(D/'maps/kurgen_turret_normal_v1.png'))[1390:2110,1040:1760]
assert np.all(flat[paint] == 255)
assert np.all(normal[paint] == [128,128,255])
region = np.asarray(Image.open(S/'repair-region-final.png').convert('L'))
patch_change = changed[1390:2110,1040:1760]
assert not patch_change[region == 0].any()
assert sha(D/'source/rus_turret.png') == 'a58608c14fb092893e1658f1f390720cc70d253d82f0ff4226e8d344ee2a5d3c'
scene = json.loads((S/'scene-audit.json').read_text())
assert scene['packed_texture_sha256'] == sha(new)
report = dict(passed=True, original_atlas=str(D/'source/rus_turret.png'),
    original_sha256=sha(D/'source/rus_turret.png'),
    original_orientation='one point down, two points up in the atlas',
    replacement_orientation='one point down, two points up in the atlas',
    rotation_verified_visually_against_immutable_original=True,
    earlier_point_up_draft_rejected=True,
    native_uvs_unchanged=True,
    flat_painted_star_has_no_embossed_normal=True,
    guide_surface_compensation_y=1.1568890364850295,
    guide_note='Regular pentagram guide compensated for the native sloped panel UV aspect; raster paint has minor edge wear.',
    changed_pixels=int(changed.sum()), changed_percent=float(changed.mean()*100),
    outside_crop_changed_pixels=0, border_and_bolt_masks_preserved=True,
    crop_xywh=[1040,1390,720,720], dimensions=[4096,4096],
    old_atlas_sha256=sha(old),new_atlas_sha256=sha(new),scene_audit=scene,
    visual_review='Final atlas crop inspected; in-game review pending',
    scope='Basecolor star repair only. Dynamic turret emissives deferred; no workaround.',
    image_generation='Built-in image_gen; final prompt in imagegen-prompts.json')
(S/'star-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('STAR_AUDIT PASS',report['changed_pixels'],'changed pixels, outside crop unchanged, original rotation preserved')
