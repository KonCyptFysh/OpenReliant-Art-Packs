import os
from pathlib import Path
import json,numpy as np
from PIL import Image
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/seams_v2';r=json.loads((W/'validation.json').read_text());im=np.asarray(Image.open(r['maps']['repair']['basecolor']['path']).convert('RGB')).astype(float)/255;N=im.shape[0];edges={}
for name,m in r['models'].items():
 vs=np.array(m['vertices'])
 for f in m['faces']:
  if f['material']!=1 or f['hidden']:continue
  for i,j in [(0,1),(1,2),(2,0)]:
   pos=vs[[f['vertices'][i],f['vertices'][j]]];q=np.array(f['uv'])[[i,j]];key=tuple(sorted(tuple(np.round(p,2)) for p in pos))
   if tuple(np.round(pos[0],2))!=key[0]:pos=pos[::-1];q=q[::-1]
   edges.setdefault(key,[]).append((name,f['id'],pos,q))
def sample(q):
 xy=q*[N,-N]+[-.5,N-.5];x=np.clip(xy[:,0],0,N-1.00001);y=np.clip(xy[:,1],0,N-1.00001);xx=x.astype(int);yy=y.astype(int);fx=(x-xx)[:,None];fy=(y-yy)[:,None];return (im[yy,xx]*(1-fx)+im[yy,xx+1]*fx)*(1-fy)+(im[yy+1,xx]*(1-fx)+im[yy+1,xx+1]*fx)*fy
results=[];t=np.linspace(.08,.92,29)[:,None]
for e,fs in edges.items():
 if len(fs)!=2:continue
 a,b=fs
 if np.max(np.abs(a[3]-b[3]))<1e-5:continue
 ac=sample(a[3][0]*(1-t)+a[3][1]*t);bc=sample(b[3][0]*(1-t)+b[3][1]*t);err=np.abs(ac-bc);results.append(dict(faces=[[a[0],a[1]],[b[0],b[1]]],max_channel_difference=float(err.max()),mean_difference=float(err.mean()),crosses_native_parts=a[0]!=b[0]))
report={'scope':'Independent bilinear sampling of the delivered repair base colour on both sides of shared geometry edges with separate UV islands','samples_per_edge':len(t),'edges':results,'max_difference':max(x['max_channel_difference'] for x in results),'mean_difference':float(np.mean([x['mean_difference'] for x in results]))};(W/'baked_seam_samples.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'edges':len(results),'max_difference':report['max_difference'],'mean_difference':report['mean_difference'],'worst':sorted(results,key=lambda x:-x['max_channel_difference'])[:4]},indent=2))
