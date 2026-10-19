from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
D=Path('${RELIANT_WORKSPACE}');W=D/'work/machinery_v9';M=D/'maps/machinery_v9';O=D/'maps/opaque_glass_v8';B=D/'history/stages/pre_machinery_v9'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
maskimage=Image.open(W/'bay-edit-mask.png');mask=np.array(maskimage)>0
regions=json.loads((D/'work/windows_v5/window-material-regions.json').read_text())['windows']
for r in regions:
    a,b,c,d=r['outer_frame'];assert not mask[b-2:d+2,a-2:c+2].any()
changed=['orr2_hull.png','orr2_hull_orm.png','orr2_hull_normal.png','orr2_hull_height.png','orr2_hull_height.npy'];diffs={}
for p in M.iterdir():
    if p.name not in changed:
        assert sha(p)==sha(O/p.name),p.name
        continue
    a=np.load(p) if p.suffix=='.npy' else np.array(Image.open(p))
    b=np.load(O/p.name) if p.suffix=='.npy' else np.array(Image.open(O/p.name))
    assert np.array_equal(a[~mask],b[~mask]),p.name
    different=np.any(a!=b,axis=-1) if a.ndim==3 else a!=b;diffs[p.name]=int(different.sum())
    assert diffs[p.name]>0
state=json.loads((D.parent/'project_state.json').read_text())
for n,h in state['source_originals'].items():assert sha(D/'source'/n)==h,n
checks={}
for tier,folder,size in [('4k','openreliant_0_18_v1',4096),('2k','review_v1_2k',2048),('1k','review_v1_1k',1024)]:
    T=D/'exports'/folder/'mods/119-reliant-worn-v1';P=B/'exports'/folder/'mods/119-reliant-worn-v1'
    assert {p.name for p in T.iterdir()}=={p.name for p in P.iterdir()}
    for p in T.iterdir():
        if p.name not in changed+['mod.ini']:assert sha(p)==sha(P/p.name),p.name
    safe=np.array(maskimage.resize((size,size),Image.Resampling.BOX).filter(ImageFilter.MaxFilter(9)))>0
    for name in changed[:3]:
        new=np.array(Image.open(T/name));old=np.array(Image.open(P/name))
        assert new.shape==(size,size,3)
        assert np.array_equal(new[~safe],old[~safe]),(tier,name,'outside bay/filter footprint changed')
    n=np.array(Image.open(T/'orr2_hull_normal.png')).astype(np.float32)/127.5-1
    err=float(np.max(abs(np.linalg.norm(n,axis=-1)-1)));assert err<.015
    assert '0.1.0-beta.9' in (T/'mod.ini').read_text()
    checks[tier]=dict(normal_max_length_error=err,native_mesh_and_uv_byte_identical=True,scripts_byte_identical=True,windows_and_emission_unchanged=True,dimensions=[size,size])
scene=json.loads((W/'scene-validation.json').read_text());assert scene['passed']
layout=json.loads((W/'component-layout.json').read_text())
out=dict(passed=True,bays=layout['bays'],component_count=len(layout['components']),changed_pixels=diffs,frame_colour_and_relief_unchanged=True,pixels_outside_bays_unchanged=True,all_64_windows_and_all_emission_unchanged=True,originals_unchanged=True,tiers=checks,scene=scene)
(W/'material-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('MATERIAL CHECKS PASSED: THREE BAYS; WINDOWS, FRAMES, UVS AND SCRIPTS RETAINED',flush=True)
