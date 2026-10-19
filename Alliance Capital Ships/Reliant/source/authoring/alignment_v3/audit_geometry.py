from pathlib import Path
import json,numpy as np,collections
W=Path('${RELIANT_WORKSPACE}/work/alignment_v3');gs=json.loads((W/'geometry.json').read_text());groups={}
for o in gs:
 v=np.array(o['verts']);o['world']=(np.c_[v,np.ones(len(v))]@np.array(o['matrix']).T)[:,:3];o['uvnative']=np.array(o['uv'])*[256,-256]+[0,256]
 groups[o['name']]=o
A=groups['Reliant Body'];B=groups['Reliant Comms'];out=[]
for fi,f in enumerate(A['faces']):
 if A['face_mats'][fi]!=2:continue
 for gi,g in enumerate(B['faces']):
  if B['face_mats'][gi]!=2:continue
  d=np.linalg.norm(A['world'][f,None]-B['world'][None,g],axis=-1);matches=np.argwhere(d<3)
  if len(matches)>=2:
   r={'body_face':fi,'comms_face':gi,'corners':[]}
   for j,k in matches:r['corners'].append(dict(pos=A['world'][f[j]].tolist(),body_uv=A['uvnative'][fi*3+j].tolist(),comms_uv=B['uvnative'][gi*3+k].tolist()))
   out.append(r)
(W/'cross-part-seams.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
