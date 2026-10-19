from pathlib import Path
import ast,numpy as np
from PIL import Image,ImageDraw,ImageFilter
D=Path('${RELIANT_WORKSPACE}');W=D/'work/refinement_v2';M=D/'maps/refinement_v2';N=2048
mod=ast.parse((W/'build_materials.py').read_text());polys=next(ast.literal_eval(n.value) for n in mod.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='polys2' for t in n.targets))
def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
im=Image.new('L',(N,N));dr=ImageDraw.Draw(im)
for poly in polys:dr.polygon([(round(x*N/256),round(y*N/256)) for x,y in poly],fill=255)
mask=np.asarray(im)>0;old=mask.astype('float32')
for _ in range(10):im=im.filter(ImageFilter.MinFilter(3));old+=(np.asarray(im)>0)
old*=256/N;new=np.zeros((N,N),'float32')
for poly in polys:
 a,b=np.floor(np.min(poly,0)*N/256-2).astype(int);c,d=np.ceil(np.max(poly,0)*N/256+2).astype(int);a=max(a,0);b=max(b,0);c=min(c,N);d=min(d,N)
 y,x=np.mgrid[b:d,a:c].astype('float32');x=(x+.5)*256/N;y=(y+.5)*256/N;inside=np.zeros(x.shape,bool);dist=np.full(x.shape,1e6,'float32')
 for k,(u,v) in enumerate(poly):
  w,z=poly[(k+1)%len(poly)];vx,vy=w-u,z-v;t=np.clip(((x-u)*vx+(y-v)*vy)/max(vx*vx+vy*vy,1e-6),0,1);dist=np.minimum(dist,np.hypot(x-u-t*vx,y-v-t*vy))
  if abs(z-v)>1e-6:inside^=((v>y)!=(z>y))&(x<(w-u)*(y-v)/(z-v)+u)
 new[b:d,a:c]=np.maximum(new[b:d,a:c],dist*inside)
h=np.load(M/'orr2_hull_height.npy');glass=Image.open(M/'orr2_hull_glass.png').convert('L').resize((N,N));exclude=np.asarray(glass.filter(ImageFilter.MaxFilter(15)))>0
yy,xx=np.mgrid[:N,:N].astype('float32');X=(xx+.5)*256/N;Y=(yy+.5)*256/N
for a,b,c,d,rad in [(108,159,251,159,.65),(112,169,247,169,.50),(114,158,114,173,.8),(138,158,138,173,.65),(182,157,182,172,.7),(202,158,202,172,.65),(221,159,221,172,.55)]:
 vx,vy=c-a,d-b;t=np.clip(((X-a)*vx+(Y-b)*vy)/max(vx*vx+vy*vy,1e-6),0,1);exclude|=np.hypot(X-a-t*vx,Y-b-t*vy)<rad+.2
h+=(-3.4*smooth(0,1,new)+3.4*smooth(0,1,old))*(~exclude)
np.save(M/'orr2_hull_height.npy',h)
dy,dx=np.gradient(h,256/N);nx=-dx*.85;ny=dy*.85;scale=np.maximum(1,np.hypot(nx,ny)/2.65);normal=np.stack([nx/scale,ny/scale,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
im=Image.fromarray(np.uint8(np.clip(normal*.5+.5,0,1)*255+.5)).resize((4096,4096),Image.Resampling.LANCZOS);n=np.asarray(im).astype('float32')/127.5-1;n/=np.linalg.norm(n,axis=-1,keepdims=True);Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255+.5)).save(M/'orr2_hull_normal.png')
Image.fromarray(np.uint8(np.clip((h+8)/16,0,1)*255+.5)).resize((4096,4096),Image.Resampling.LANCZOS).save(M/'orr2_hull_height.png')
print('Analytic bridge bevels saved')
