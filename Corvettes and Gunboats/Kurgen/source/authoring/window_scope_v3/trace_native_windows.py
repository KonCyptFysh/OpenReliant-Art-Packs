from pathlib import Path
import numpy as np,json
D=Path('${KURGEN_WORKSPACE}')
p=json.loads((D/'source/native_parts.json').read_text())[0];l=p['lods'][0];rows=[]
for w in json.loads((D/'work/windows_relief_v2/window_regions.json').read_text())['windows']:
 if w['shape']=='capsule': a=np.array(w['a']);b=np.array(w['b'])
 else:
  x,y,xx,yy=w['box'];a=np.array([(x+xx)/2,y+1]);b=np.array([(x+xx)/2,yy-1])
 result={}
 for t in np.linspace(.01,.99,30):
  q=a*(1-t)+b*t
  for f in l['faces']:
   if f['hidden'] or f['material']!=0:continue
   uv=np.array(f['uv']);uv[:,1]=1-uv[:,1];uv*=256
   try: ab=np.linalg.solve((uv[1:]-uv[0]).T,q-uv[0])
   except np.linalg.LinAlgError:continue
   if min(ab)<-1e-6 or sum(ab)>1+1e-6:continue
   xyz=np.array(l['vertices'])[f['vertices']];point=xyz[0]+ab@(xyz[1:]-xyz[0])+p['origin'];result.setdefault(f['id'],[]).append(point)
 r=dict(name=w['name'],faces=[dict(face=k,xyz=np.mean(v,axis=0).round(1).tolist(),normal=l['faces'][k]['normal']) for k,v in result.items()]);rows.append(r)
 print(w['name'],[(x['face'],x['xyz']) for x in r['faces']])
Path('/tmp/kurgen-window-face-trace.json').write_text(json.dumps(rows,indent=2))
