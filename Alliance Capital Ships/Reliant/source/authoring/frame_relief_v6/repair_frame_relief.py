"""Replace steep generic pocket ramps with bevels measured at painted transitions.
Colour, windows, pipes, native meshes and other atlases are preserved. Geometry is
fit in 4K pixel space; only explicitly identified structural pocket edges are used.
"""
from pathlib import Path
import json, numpy as np
from PIL import Image,ImageDraw
from PIL import ImageFilter
def map_coordinates(a,coords,order=1,mode='nearest'):
 y,x=coords;y=np.clip(y,0,a.shape[0]-1.001);x=np.clip(x,0,a.shape[1]-1.001);iy=y.astype(int);ix=x.astype(int);fy=y-iy;fx=x-ix
 return a[iy,ix]*(1-fy)*(1-fx)+a[iy+1,ix]*fy*(1-fx)+a[iy,ix+1]*(1-fy)*fx+a[iy+1,ix+1]*fy*fx
def gaussian_filter1d(a,sigma,axis=1):
 k=np.exp(-np.arange(-3,4)**2/(2*sigma**2));k/=k.sum();pad=np.pad(a,((0,0),(3,3)),mode='edge');return sum(k[i]*pad[:,i:i+a.shape[1]] for i in range(7))
def maximum_filter(a,size):return np.asarray(Image.fromarray(a).filter(ImageFilter.MaxFilter(size)))
D=Path('${RELIANT_WORKSPACE}');W=D/'work/frame_relief_v6';M=D/'maps/frame_relief_v6';P=D/'maps/windows_v5'
polys=json.loads((D/'work/alignment_v4/measured-geometry.json').read_text())['pockets']
rgb=np.asarray(Image.open(P/'orr2_hull.png').convert('RGB')).astype(np.float32);lum=rgb.mean(-1)
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def field(points,n,depth,widths,centered=False):
 # Signed segment distance, with finite endpoints; per-edge transition width.
 pts=np.array(points);x0,y0=np.floor((pts.min(0)-10)*n/1024).astype(int);x1,y1=np.ceil((pts.max(0)+10)*n/1024).astype(int);x0=max(0,x0);y0=max(0,y0);x1=min(n,x1);y1=min(n,y1)
 y,x=np.mgrid[y0:y1,x0:x1].astype(np.float32);x=(x+.5)*1024/n;y=(y+.5)*1024/n
 inside=np.zeros(x.shape,bool);dist=np.full(x.shape,1e6,np.float32);width=np.zeros(x.shape,np.float32)
 for i,((u,v),(w,z)) in enumerate(zip(pts,np.roll(pts,-1,axis=0))):
  vx,vy=w-u,z-v;t=np.clip(((x-u)*vx+(y-v)*vy)/(vx*vx+vy*vy),0,1);d=np.hypot(x-u-t*vx,y-v-t*vy);take=d<dist;dist[take]=d[take];width[take]=widths[i]
  if z!=v:inside^=((v>y)!=(z>y))&(x<(w-u)*(y-v)/(z-v)+u)
 if centered:out=depth*smooth(-width/2,width/2,np.where(inside,dist,-dist))
 else:out=np.where(inside,depth*smooth(0,width,dist),0)
 return (x0,y0,x1,y1),out
records=[];newpolys=[];allwidths=[]
for pi,points in enumerate(polys):
 points=np.array(points);lines=[];widths=[];edges=[]
 for p,q in zip(points,np.roll(points,-1,axis=0)):
  delta=q-p;length=np.linalg.norm(delta);axis=delta/length;inward=np.array([-axis[1],axis[0]])
  ts=np.linspace(.20,.80,max(20,int(length*2)));ss=np.arange(-2,6.001,.125);pos=p+ts[:,None]*delta;xy=pos[:,None,:]+ss[None,:,None]*inward
  vals=map_coordinates(lum,[(xy[:,:,1]*4-.5).ravel(),(xy[:,:,0]*4-.5).ravel()],order=1,mode='nearest').reshape(len(ts),len(ss))
  vals=gaussian_filter1d(vals,1.0,axis=1);fall=-np.gradient(vals,ss,axis=1)
  allowed=(ss>=-.5)&(ss<=4.5);fall[:,~allowed]=0;peak=fall.argmax(1)
  weights=np.maximum(fall,0)*(abs(np.arange(len(ss))[None,:]-peak[:,None])<=6)
  offsets=(weights*ss).sum(1)/np.maximum(weights.sum(1),1e-6)
  good=np.ones(len(ts),bool)
  for _ in range(3):
   fit=np.polyfit(ts[good]*length,offsets[good],1);resid=offsets-np.polyval(fit,ts*length);good=abs(resid-np.median(resid))<max(.2,2.5*np.median(abs(resid-np.median(resid))))
  if abs(delta[0])<1e-6 or abs(delta[1])<1e-6:fit=np.array([0,np.median(offsets[good])])
  nn=inward-fit[0]*axis;nn/=np.linalg.norm(nn);c=float(nn@(p+inward*fit[1]));lines.append((nn,c))
  # Fit the painted falloff width from the median edge profile. Smoothstep's
  # derivative has variance width^2/20. Bound only to avoid a subpixel ramp.
  prof=np.median(vals[good],axis=0);grad=np.maximum(-np.gradient(prof,ss),0);center=np.median(offsets[good]);grad*=abs(ss-center)<2.2
  var=np.sum(grad*(ss-center)**2)/max(grad.sum(),1e-6);width=float(np.clip(np.sqrt(var*20),2.4,5.5));widths.append(width)
  edges.append(dict(center_shift=float(center),width=width,fit_residual=float(np.median(abs(resid[good]))),samples=int(good.sum())))
 new=[]
 for i,(nn,c) in enumerate(lines):pn,pc=lines[i-1];new.append(np.linalg.solve(np.array([pn,nn]),[pc,c]).tolist())
 newpolys.append(new);allwidths.append(widths);records.append(dict(pocket=pi,points=new,edges=edges,depth=2.2))
# Reconstruct old field at its original 2K sampling, including its resampling;
# subtract only that contribution from the current 4K height master.
oldfield=np.zeros((2048,2048),np.float32)
for pts in polys:
 (a,b,c,d),f=field(pts,2048,-10,[3.4]*len(pts));oldfield[b:d,a:c]+=f
oldfield=np.array(Image.fromarray(oldfield).resize((4096,4096),Image.Resampling.BICUBIC))
newfield=np.zeros((4096,4096),np.float32)
for pts,widths in zip(newpolys,allwidths):
 (a,b,c,d),f=field(pts,4096,-2.2,widths,True);newfield[b:d,a:c]+=f
# V5 cleared the old pocket beneath each inset. Apply those exact clear regions
# to both contributions so nearby windows retain their existing mounting plane.
regions=json.loads((D/'work/windows_v5/window-material-regions.json').read_text())['windows']
protected=np.zeros((4096,4096),bool)
for w in regions:
 if w['backing_height']>=0:continue
 a,b,c,d=w['previous_glass'];oldfield[b-8:d+8,a-8:c+8]=-10;newfield[b-8:d+8,a-8:c+8]=-2.2
 a,b,c,d=w['outer_frame'];protected[b-1:d+1,a-1:c+1]=True
h=np.load(P/'orr2_hull_height.npy')*4;delta=newfield-oldfield;newh=h+delta
# Only replace pixels influenced by a changed ramp. Constant backing shifts leave
# glass and pipe normals untouched. Expand for the finite gradient stencil.
dy,dx=np.gradient(delta,.25);mask=maximum_filter((np.hypot(dx,dy)>.001).astype(np.uint8),size=5)>0
assert not np.any(mask&protected),'New pocket ramp overlaps a retained window'
ny,nx=np.gradient(newh,.25);nx=-nx*.85;ny=ny*.85;slope=np.maximum(1,np.hypot(nx,ny)/2.4);v=np.stack([nx/slope,ny/slope,np.ones_like(newh)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
normal=np.array(Image.open(P/'orr2_hull_normal.png'));normal[mask]=np.uint8((v[mask]*.5+.5)*255+.5)
Image.fromarray(normal).save(M/'orr2_hull_normal.png');np.save(M/'orr2_hull_height.npy',newh/4);Image.fromarray(np.uint8(np.clip((newh/4+8)/16,0,1)*255+.5)).save(M/'orr2_hull_height.png')
# Replace cavity contribution at the same ramp, keeping original backing tone and
# every other material channel. The old fixed ramp must not leave an AO ghost.
orm=np.array(Image.open(P/'orr2_hull_orm.png'));ao=1-.18*smooth(0,12,-newfield*(10/2.2));orm[:,:,0][mask]=np.uint8(ao[mask]*255+.5);Image.fromarray(orm).save(M/'orr2_hull_orm.png')
Image.fromarray(mask.astype(np.uint8)*255).save(W/'frame-edit-mask.png')
(W/'measured-bevels.json').write_text(json.dumps(records,indent=2)+'\n')
over=Image.open(P/'orr2_hull.png').convert('RGB');dr=ImageDraw.Draw(over)
for p in newpolys:
 pts=[tuple(np.array(q)*4) for q in p];dr.line(pts+[pts[0]],fill=(30,230,100),width=2)
over.save(W/'frame-transition-overlay.png')
for name,bb in [('bridge',(0,10,114,515)),('bridge-other',(0,520,114,1024)),('forward',(458,78,824,224)),('machinery',(425,590,1023,704))]:over.crop(tuple(v*4 for v in bb)).save(W/(name+'-trace.png'))
print('FRAME_REPAIR',len(records),'pockets;',int(mask.sum()),'pixels;',sum(len(r['edges']) for r in records),'measured edges',flush=True)
