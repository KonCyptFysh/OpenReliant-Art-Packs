from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/opaque_glass_v8';M=D/'maps/opaque_glass_v8';O=D/'maps/frame_relief_v6'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mask=np.array(Image.open(W/'glass-edit-mask.png'))>0
glass=np.array(Image.open(M/'orr2_hull_glass.png'))
frame=np.array(Image.open(M/'orr2_hull_window_frame.png'))
assert not np.any(mask & (frame>0))
changed=['orr2_hull.png','orr2_hull_emissive.png','orr2_hull_orm.png','orr2_hull_normal.png','orr2_hull_height.png','orr2_hull_height.npy']
diffs={}
for p in M.iterdir():
    if p.name not in changed:
        assert sha(p)==sha(O/p.name),p.name
        continue
    a=np.load(p) if p.suffix=='.npy' else np.array(Image.open(p))
    b=np.load(O/p.name) if p.suffix=='.npy' else np.array(Image.open(O/p.name))
    assert np.array_equal(a[~mask],b[~mask]),p.name
    different=np.any(a!=b,axis=-1) if a.ndim==3 else a!=b
    diffs[p.name]=int(different.sum())
orm=np.array(Image.open(M/'orr2_hull_orm.png'));assert not np.any(orm[...,2][mask])
em=np.array(Image.open(M/'orr2_hull_emissive.png'));old_em=np.array(Image.open(O/'orr2_hull_emissive.png'))
assert np.array_equal(em[~mask],old_em[~mask])
assert not np.any(em[frame>0])
windows=json.loads((D/'work/windows_v5/window-material-regions.json').read_text())['windows'];brightness=[]
assert len(windows)==64
for rec in windows:
    a,b,c,d=rec['outer_frame'];sel=glass[b:d,a:c]==255
    new=em[b:d,a:c][sel].mean(axis=0);old=old_em[b:d,a:c][sel].mean(axis=0)
    assert new[0]>old[0] and new[1]>old[1] and new[2]>old[2]
    brightness.append(dict(id=rec['id'],old_mean_rgb=old.tolist(),new_mean_rgb=new.tolist()))
state=json.loads((D.parent/'project_state.json').read_text())
for n,h in state['source_originals'].items():assert sha(D/'source'/n)==h,n
oldroot=D/'history/stages/pre_opaque_glass_v8/exports'
checks={}
for tier,folder,size in [('4k','openreliant_0_18_v1',4096),('2k','review_v1_2k',2048),('1k','review_v1_1k',1024)]:
    T=D/'exports'/folder/'mods/119-reliant-worn-v1';P=oldroot/folder/'mods/119-reliant-worn-v1'
    assert {p.name for p in T.iterdir()}=={p.name for p in P.iterdir()}
    for p in T.iterdir():
        if p.name not in changed+['mod.ini']:assert sha(p)==sha(P/p.name),p.name
    for name in changed[:4]:assert Image.open(T/name).size==(size,size)
    n=np.array(Image.open(T/'orr2_hull_normal.png')).astype(np.float32)/127.5-1
    err=float(np.max(abs(np.linalg.norm(n,axis=-1)-1)));assert err<.015
    assert '0.1.0-beta.8' in (T/'mod.ini').read_text()
    checks[tier]=dict(normal_max_length_error=err,native_mesh_and_uv_byte_identical=True,scripts_byte_identical=True,dimensions=[size,size])
scene=json.loads((W/'scene-validation.json').read_text());assert scene['passed']
out=dict(passed=True,window_count=64,frames_gaskets_uvs_and_layout_preserved=True,changed_pixels=diffs,pixels_outside_glass_unchanged=True,emission_confined_to_existing_panes=True,glass_metallic_zero=True,originals_unchanged=True,brightness_per_pane=brightness,tiers=checks,scene=scene)
(W/'material-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('MATERIAL VALIDATION PASSED: 64 PANES, EXACT FRAMES AND UVS, ALL THREE RESOLUTIONS',flush=True)
