import json,numpy as np
from pathlib import Path
D=Path('${KARAK_WORKSPACE}');ps=json.load(open(D/'source/native_parts.json'));a=[]
for p in ps:
 for li,l in enumerate(p['lods']):
  for f in l['faces']:
   if f['hidden']:continue
   xyz=np.array([l['vertices'][v] for v in f['vertices']]);e=xyz[1:]-xyz[0];n=np.cross(*e);area=np.linalg.norm(n)
   if area<1e-7:continue
   n/=area;t=e[0]/np.linalg.norm(e[0]);xy=e@np.stack((t,np.cross(n,t)),axis=1);uv=np.array(f['uv']);s=np.linalg.svd(np.linalg.solve(xy,uv[1:]-uv[0]),compute_uv=False);a.append(dict(part=p['name'],lod=li,face=f['id'],ratio=float(s[0]/max(s[1],1e-12)),uv_area=float(abs(np.linalg.det(uv[1:]-uv[0]))),uv=f['uv']))
report=dict(all_visible_materials=sorted(set(f['material'] for p in ps for l in p['lods'] for f in l['faces'] if not f['hidden'])),visible_lod0=sum(x['lod']==0 for x in a),visible_lod0_top=sorted([x for x in a if x['lod']==0],key=lambda q:-q['ratio'])[:12],collapsed=[x for x in a if x['uv_area']<1e-10])
(D/'work/reconstruction_v1/source_uv_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2)[:6200])
