"""Register ImageGen bay artwork to the three existing polygon apertures.
All new material channels share the same inverse warp. No traced legacy pipes or
independently generated normal structures survive inside the edited regions.
"""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}')
W=D/'work/service_bays_v10';M=D/'maps/service_bays_v10';O=D/'maps/machinery_v9';M.mkdir(exist_ok=True)
for p in O.iterdir():
 if not (M/p.name).exists():shutil.copy2(p,M/p.name)
box=(420,590,1024,710);a,b,c,d=[v*4 for v in box];H=d-b;N=c-a
y,x=np.mgrid[b:d,a:c].astype(np.float32);x=(x+.5)/4;y=(y+.5)/4
points=np.stack([x,y],axis=-1)
def smooth(lo,hi,v):
 t=np.clip((v-lo)/(hi-lo),0,1);return t*t*(3-2*t)
def blur(v,sigma):
 r=int(np.ceil(sigma*3));q=np.arange(-r,r+1);k=np.exp(-q*q/(2*sigma*sigma));k/=k.sum()
 for axis in [0,1]:
  pad=[(0,0)]*v.ndim;pad[axis]=(r,r);s=np.pad(v,pad,mode='edge');z=np.zeros_like(v)
  for j,w in enumerate(k):
   sl=[slice(None)]*v.ndim;sl[axis]=slice(j,j+v.shape[axis]);z+=s[tuple(sl)]*w
  v=z
 return v
src=np.asarray(Image.open(W/'service-bays-source.png').convert('RGB')).astype(np.float32)/255
lum=src@np.array([.2126,.7152,.0722],np.float32)
def sample(arr,uv):
 u=np.clip(uv[...,0],0,arr.shape[1]-1.001);v=np.clip(uv[...,1],0,arr.shape[0]-1.001)
 xx=u.astype(int);yy=v.astype(int);fu=u-xx;fv=v-yy
 if arr.ndim==3:fu=fu[...,None];fv=fv[...,None]
 return arr[yy,xx]*(1-fu)*(1-fv)+arr[yy,xx+1]*fu*(1-fv)+arr[yy+1,xx]*(1-fu)*fv+arr[yy+1,xx+1]*fu*fv
records=json.loads((D/'work/frame_relief_v6/measured-bevels.json').read_text())[17:20]
coverage=np.zeros((H,N),np.float32);distance_to_frame=np.zeros_like(coverage);coords=np.zeros((H,N,2),np.float32);registration=[]
def intersect_lines(normals,constants):
 return np.array([np.linalg.solve(np.stack([normals[i-1],normals[i]]),[constants[i-1],constants[i]]) for i in range(len(normals))])
for rec in records:
 pts=np.array(rec['points']);vectors=np.roll(pts,-1,axis=0)-pts;normals=np.stack([-vectors[:,1],vectors[:,0]],-1);normals/=np.linalg.norm(normals,axis=-1,keepdims=True)
 widths=np.array([e['width'] for e in rec['edges']]);target=intersect_lines(normals,(normals*pts).sum(-1)+widths/2+.38)
 predicted=(pts-[420,590])*3.596+np.array([0,148]);offsets=[];profiles=[]
 # Locate each generated frame ridge near its reference edge, then sample only
 # the dark interior beyond it. The original outer frame is never composited.
 for i,(p,q,n) in enumerate(zip(predicted,np.roll(predicted,-1,axis=0),normals)):
  along=np.linspace(.18,.82,64);across=np.linspace(-9,9,73)
  uv=p[None,None,:]+along[:,None,None]*(q-p)[None,None,:]+across[None,:,None]*n
  profile=np.median(sample(lum,uv),axis=0);j=int(np.argmax(profile))
  offset=float(across[j]+5.0);offsets.append(offset)
  profiles.append(dict(edge=i,ridge_offset=float(across[j]),sample_inset=offset))
 source=intersect_lines(normals,(normals*predicted).sum(-1)+offsets)
 # Piecewise affine fan, with a shared centre. Distortions are limited to the
 # small differences between generated and native aperture outlines.
 tc=target.mean(0);sc=source.mean(0);region=np.zeros((H,N),bool)
 for i in range(len(pts)):
  t1,t2=target[i],target[(i+1)%len(pts)];s1,s2=source[i],source[(i+1)%len(pts)]
  inv=np.linalg.inv(np.stack([t1-tc,t2-tc],axis=-1));uv=(points-tc)@inv.T
  select=(uv[...,0]>=-.015)&(uv[...,1]>=-.015)&(uv.sum(-1)<=1.015)
  mapped=sc+uv[...,0,None]*(s1-sc)+uv[...,1,None]*(s2-sc);coords[select]=mapped[select];region|=select
 inside=np.zeros((H,N),bool);dist=np.full((H,N),1e6,np.float32);width=np.zeros_like(dist)
 for i,((u,v),(w,z)) in enumerate(zip(pts,np.roll(pts,-1,axis=0))):
  vx,vy=w-u,z-v;t=np.clip(((x-u)*vx+(y-v)*vy)/(vx*vx+vy*vy),0,1);dd=np.hypot(x-u-t*vx,y-v-t*vy);near=dd<dist;dist[near]=dd[near];width[near]=widths[i]
  if z!=v:inside^=((v>y)!=(z>y))&(x<(w-u)*(y-v)/(z-v)+u)
 signed=np.where(inside,dist,-dist);cov=smooth(width/2+.15,width/2+.40,signed)*region
 coverage=np.maximum(coverage,cov);distance_to_frame=np.maximum(distance_to_frame,np.maximum(0,signed-width/2))
 registration.append(dict(pocket=rec['pocket'],source_inner_polygon=source.tolist(),target_inner_polygon=target.tolist(),edge_profiles=profiles))
mask=coverage>0;interior=coverage>.999
art=sample(src,coords).astype(np.float32);art*=np.array([1.0,1.015,.96],np.float32)
# Height from the registered image: broad machinery masses and restrained fine
# fins/seams, with hue suppressed so service labels do not become raised blocks.
gray=sample(lum,coords).astype(np.float32);gray[~mask]=.045
coarse=blur(gray,2.4);clean=blur(gray,.75)
body=smooth(.045,.28,coarse);detail=np.clip(clean-coarse,-.07,.07)
relief=1.45*body+detail*2.1
relief*=smooth(.5,2.1,distance_to_frame)
height=-2.2+relief
# Keep broad metal faces readable without treating grime and wear as deep dents.
normal_detail=.80
oldh=np.load(O/'orr2_hull_height.npy');allh=oldh.copy();patch=oldh[b:d,a:c]*4;allh[b:d,a:c]=(patch*(1-coverage)+height*coverage)/4
saturation=art.max(-1)-art.min(-1);bare=smooth(.12,.36,clean)*(1-smooth(.025,.10,saturation))
rough=np.clip(.76-.31*bare+.04*(1-body),.39,.82);metal=np.clip(.12+.66*bare,.10,.78)
ao=np.clip(.76+.20*body-.10*(1-smooth(0,2.0,distance_to_frame)),.62,.97)
base=np.array(Image.open(O/'orr2_hull.png'));orm=np.array(Image.open(O/'orr2_hull_orm.png'));normal=np.array(Image.open(O/'orr2_hull_normal.png'))
def install(dest,values):
 part=dest[b:d,a:c];new=np.clip(values,0,1)*255;mix=np.uint8(part*(1-coverage[...,None])+new*coverage[...,None]+.5);part[mask]=mix[mask]
install(base,art);install(orm,np.stack([ao,rough,metal],-1))
dy,dx=np.gradient(allh[b-2:d+2,a-2:c]*4,.25);nx=-dx*normal_detail;ny=dy*normal_detail;scale=np.maximum(1,np.hypot(nx,ny)/2.8)
v=np.stack([nx/scale,ny/scale,np.ones_like(nx)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
newnormal=np.uint8(np.clip(v*.5+.5,0,1)*255+.5)[2:-2,2:];normal[b:d,a:c][mask]=newnormal[mask]
for name,arr in [('orr2_hull.png',base),('orr2_hull_orm.png',orm),('orr2_hull_normal.png',normal)]:Image.fromarray(arr).save(M/name)
np.save(M/'orr2_hull_height.npy',allh);hi=np.array(Image.open(O/'orr2_hull_height.png'));hi[b:d,a:c][mask]=np.uint8(np.clip((allh[b:d,a:c][mask]+8)/16,0,1)*255+.5);Image.fromarray(hi).save(M/'orr2_hull_height.png')
fullmask=np.zeros((4096,4096),np.uint8);fullmask[b:d,a:c]=mask*255;Image.fromarray(fullmask).save(W/'bay-edit-mask.png')
Image.fromarray(base).crop((a,b,c,d)).save(W/'new-panel-colour.png');Image.fromarray(normal).crop((a,b,c,d)).save(W/'new-panel-normal.png')
Image.fromarray(np.uint8(np.clip((height+2.2)/1.65,0,1)*255)).save(W/'registered-relief.png')
(W/'registration.json').write_text(json.dumps(dict(revision=10,bays=registration,source='service-bays-source.png',source_mode='built-in ImageGen authored industrial bays',map_method='shared polygon registration; multiscale relief and material response from registered artwork',height_range=[float(height[interior].min()),float(height[interior].max())]),indent=2)+'\n')
print('BAYS REGISTERED AND ALL MATERIAL CHANNELS REBUILT',int(mask.sum()),flush=True)
