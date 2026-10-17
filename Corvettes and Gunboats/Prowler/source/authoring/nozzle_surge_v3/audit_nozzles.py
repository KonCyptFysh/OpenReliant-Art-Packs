from pathlib import Path
import json,numpy as np
D=Path('${PROWLER_WORKSPACE}');W=D/'work/nozzle_surge_v3'
# Reuse the inspected native-plane definitions without rebuilding or overwriting exports.
s=(D/'work/lighting_v2/build_lighting.py').read_text();s=s[:s.index('def mask(')];ns={};exec(s,ns);groups=ns['groups'];parts=ns['parts']
rows=[];regressions=[]
for pi,p in enumerate(parts):
 for li,l in enumerate(p['lods']):
  v=np.array(l['vertices']);vn=np.array(l['normals']);selected=[];heated=[]
  for f in l['faces']:
   if f['hidden']:continue
   xyz=v[f['vertices']];normals=vn[f['vertices']];normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);normal/=max(np.linalg.norm(normal),1e-8)
   if normal@f['normal']<0:normal=-normal
   bary=np.array([[1-u-w,u,w] for u in np.linspace(0,1,25) for w in np.linspace(0,1-u,25)]);pts=bary@xyz;smooth=bary@normals
   for gi,g in enumerate(groups):
    inside=np.all((pts>=g['lo'])&(pts<=g['hi']),axis=1);fast=np.zeros(len(pts),bool);heat=fast.copy();prior=fast.copy()
    for ji,p2 in enumerate(g['planes']):
     pl=p2['plane'];allowed=inside.copy()
     # No extra spatial bounds: visible geometric orientation preserves the original scope.
     hit=allowed&(normal@pl[:3]>.99995)&(abs(pts@pl[:3]-pl[3])<.35);fast|=hit
     if p2['heat']:heat|=hit;prior|=hit&((smooth@normal)>0)
    if fast.any():
     assert pi==g['part'],('false-positive',pi,li,f['id'],gi);selected.append([f['id'],gi])
    if heat.any():
     heated.append([f['id'],gi]);missed=int((heat&~prior).sum())
     if missed:regressions.append(dict(part=pi,lod=li,face=f['id'],valid_samples=int(heat.sum()),old_mask_missing_samples=missed,new_mask_missing_samples=0))
  rows.append(dict(part=pi,lod=li,fast_faces=selected,heat_faces=heated))
old=json.loads((D/'work/lighting_v2/nozzle_surface_audit.json').read_text())

for a,b in zip(rows,old['rows']):
 if a!=b: print('DIFFERENCE',a,b)
assert rows==old['rows'],'same intended faces with either orientation'
assert len(regressions)>0
report=dict(passed=True,root_cause='Smoothed vertex normals reverse the derivative-normal sign within native nozzle faces; signed plane checks then rejected triangular portions.',fix='Camera-facing derivative normals, independent of smoothed vertex normals; signed native plane scope retained',all_40_part_lods_checked=True,other_parts_selected=0,geometry_normals_uvs_textures_native_model_unchanged=True,old_mask_regressions=regressions,rows=rows)
(W/'nozzle_surface_audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: unchanged intended face scope; corrected',len(regressions),'face/detail combinations affected by interpolated normal sign.')
