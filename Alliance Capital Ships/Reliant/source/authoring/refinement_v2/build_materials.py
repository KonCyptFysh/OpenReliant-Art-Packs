"""Semantic relief for current restored artwork. No diffuse-brightness-to-height conversion.
Rectangles/structural paths define relief; only rib centre positions are measured inside
explicit radiator regions. Glass, emission, AO and dielectric material share one geometry.
"""
from pathlib import Path
import json, numpy as np
from PIL import Image, ImageDraw
from PIL import ImageFilter
from collections import deque
def gaussian_filter1d(a,sigma):
 r=max(1,int(sigma*3));x=np.arange(-r,r+1);k=np.exp(-x*x/(2*sigma*sigma));k/=k.sum();return np.convolve(np.pad(a,r,mode="edge"),k,mode="valid")
def find_peaks(a,distance,prominence):
 candidates=np.where((a[1:-1]>a[:-2])&(a[1:-1]>=a[2:]))[0]+1;kept=[];r=max(2,int(distance))
 for k in sorted(candidates,key=lambda k:-a[k]):
  if a[k]-max(a[max(0,k-r):k+1].min(),a[k:min(len(a),k+r+1)].min())<prominence:continue
  if all(abs(k-q)>=distance for q in kept):kept.append(k)
 return np.array(sorted(kept),dtype=int),{}
def label(a):
 out=np.zeros(a.shape,np.int32);n=0;rows,cols=a.shape
 for y,x in zip(*np.where(a)):
  if out[y,x]:continue
  n+=1;out[y,x]=n;todo=deque([(y,x)])
  while todo:
   v,u=todo.popleft()
   for b,c in ((v-1,u),(v+1,u),(v,u-1),(v,u+1)):
    if 0<=b<rows and 0<=c<cols and a[b,c] and not out[b,c]:out[b,c]=n;todo.append((b,c))
 return out,n
def find_objects(a):
 boxes={}
 for y,x in zip(*np.where(a)):
  k=int(a[y,x]);b=boxes.setdefault(k,[y,x,y,x]);b[0]=min(b[0],y);b[1]=min(b[1],x);b[2]=max(b[2],y);b[3]=max(b[3],x)
 return [(slice(b[0],b[2]+1),slice(b[1],b[3]+1)) for _,b in sorted(boxes.items())]
def distance_transform_edt(a):
 # Capped square-distance bevel from authored polygon topology, not from colour.
 d=a.astype(np.float32);im=Image.fromarray(np.uint8(a)*255)
 for _ in range(10):im=im.filter(ImageFilter.MinFilter(3));d+=(np.asarray(im)>0)
 return d
D=Path('${RELIANT_WORKSPACE}');W=D/'work/refinement_v2';M=D/'maps/refinement_v2';N=2048;OUT=4096
R=json.loads((D/'work/reconstruction_v1/regions.json').read_text())['regions']
yy,xx=np.mgrid[:N,:N].astype('float32');X=(xx+.5)*256/N;Y=(yy+.5)*256/N

def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def box(a,b,c,d):return np.minimum.reduce([X-a,c-X,Y-b,d-Y])
def line(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-8),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def save(a,name):
 a=np.clip(a,0,1);im=Image.fromarray(np.uint8(a*255+.5));im=im.resize((OUT,OUT),Image.Resampling.LANCZOS)
 if name.endswith('_normal'):
  n=np.asarray(im).astype('float32')/127.5-1;n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8);im=Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255+.5))
 im.save(M/(name+'.png'))
def normals(h):
 dy,dx=np.gradient(h,256/N);nx=-dx*.85;ny=dy*.85
 scale=np.maximum(1,np.hypot(nx,ny)/2.65);nx/=scale;ny/=scale
 n=np.stack([nx,ny,np.ones_like(h)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);return n*.5+.5
# Traced current metal frames, clockwise in native atlas pixels.
polys2=[[(3,6),(15,6),(15,10),(4,23),(2,22),(2,8)],[(18,12),(26,13),(26,49),(20,57),(10,48),(5,38),(5,29)],[(3,58),(11,58),(26,72),(26,103),(12,128),(3,125)],[(3,132),(15,132),(15,137),(3,148)],[(18,140),(26,141),(26,177),(20,183),(5,167),(5,153)],[(3,184),(11,184),(26,196),(26,229),(12,255),(3,252)],[(48,39),(55,35),(61,36),(68,42),(68,63),(63,66),(51,58),(47,50)],[(75,38),(83,35),(94,40),(94,62),(87,67),(74,55)],[(116,21),(135,21),(143,27),(139,36),(121,37),(116,32)],[(147,21),(165,21),(181,31),(175,36),(151,36),(142,28)],[(185,21),(201,21),(205,26),(203,37),(183,37)],[(115,41),(137,41),(145,47),(140,55),(122,55),(116,50)],[(148,41),(170,41),(180,48),(174,55),(151,55),(142,48)],[(108,150),(160,150),(176,160),(160,176),(109,176),(106,171)],[(177,150),(201,150),(219,160),(207,176),(162,176)],[(209,150),(250,150),(254,155),(254,170),(246,176),(212,176),(224,160)]]
records=[];window_boxes=[]
for i in range(1,4):
 stem=f'orr{i}_hull';r=R[str(i)];rgb=np.asarray(Image.open(M/(stem+'.png')).convert('RGB').resize((N,N),Image.Resampling.LANCZOS)).astype('float32')/255
 h=np.zeros((N,N),'float32');structure=h.copy();flat=h.copy();glass=h.copy();ao=np.ones_like(h);emit=np.zeros_like(rgb)
 for b in r['flat']:flat=np.maximum(flat,smooth(0,.25,box(*b)))
 # Panel grooves follow the restored atlas's original deliberate topology.
 for a,b,c,d in r['lines']:
  mask=smooth(0,.38,line((a,b),(c,d),.58))*(1-flat);h-=1.4*mask;structure=np.maximum(structure,mask*.5)
 for a,b,c,d,rad in r['slots']:
  dist=line((a,b),(c,d),rad);m=smooth(0,.3,dist);h=h*(1-m)-3.8*smooth(0,.85,dist)*m;structure=np.maximum(structure,m);ao*=1-.16*m
 for cx,cy,rad in r['circles']:
  dist=rad-np.hypot(X-cx,Y-cy);m=smooth(0,.3,dist);ring=np.exp(-((dist-.65)/.45)**2);height=-2.4*smooth(0,1,dist)+2.3*ring
  # Main engine disk: radial vanes, hub and concentric rings share the painted fan.
  if i==1 and cx==107:
   cx,cy=107,15;rho=np.hypot(X-cx,Y-cy);ang=np.arctan2(Y-cy,X-cx);dist=12.5-rho;m=smooth(0,.3,dist)
   height=-2.7+2.5*np.exp(-((rho-4.2)/.55)**2)+1.8*np.exp(-((rho-11.5)/.45)**2)+2.0*(.5+.5*np.cos(ang*12))**12*smooth(3.7,4.5,rho)*(1-smooth(11,12,rho))
  h=h*(1-m)+height*m;structure=np.maximum(structure,m);ao*=1-.15*m
 # Fit actual rib phase inside each known radiator; scratches do not become relief.
 ribs=[]
 for a,b,c,d,axis,pitch in r['ribs']:
  m=smooth(0,.4,box(a,b,c,d));ix0,iy0,ix1,iy1=[round(v*N/256) for v in [a,b,c,d]]
  roi=rgb[iy0:iy1,ix0:ix1].mean(-1);profile=roi.mean(0 if axis=='x' else 1);profile=gaussian_filter1d(profile,max(.8,N/256*.16))
  peaks,_=find_peaks(profile,distance=max(2,pitch*N/256*.65),prominence=.025)
  coords=(peaks+.5)*256/N+(a if axis=='x' else b)
  if not len(coords):coords=np.arange((a if axis=='x' else b)+pitch*.5,(c if axis=='x' else d),pitch)
  pos=X if axis=='x' else Y;bar=np.zeros_like(h)
  for center in coords:bar=np.maximum(bar,1-smooth(.16,min(.85,pitch*.28),abs(pos-center)))
  depth=-3.4+4.1*bar;h=h*(1-m)+depth*m;structure=np.maximum(structure,m);ao*=1-m*(.28*(1-bar));ribs.append(dict(box=[a,b,c,d],axis=axis,centres=coords.tolist()))
 if i==2:
  # Multi-level bridge recesses with metal beams, with all windows added afterwards.
  pm=Image.new('L',(N,N));dr=ImageDraw.Draw(pm)
  for pts in polys2:dr.polygon([(round(x*N/256),round(y*N/256)) for x,y in pts],fill=255)
  inside=np.asarray(pm)>0;dist=distance_transform_edt(inside).astype('float32')*256/N;m=inside.astype('float32')
  pocket=-3.4*smooth(0,1.0,dist);h=h*(1-m)+pocket*m;structure=np.maximum(structure,m*.6);ao*=1-.12*smooth(0,.8,dist)
  # Existing pipes within the machinery alcove: curved cross-sections above the recessed deck.
  for a,b,c,d,rad in [(108,159,251,159,.65),(112,169,247,169,.50),(114,158,114,173,.8),(138,158,138,173,.65),(182,157,182,172,.7),(202,158,202,172,.65),(221,159,221,172,.55)]:
   dist=line((a,b),(c,d),rad);m=smooth(-.15,.15,dist);v=np.clip(dist/rad,0,1);h=h*(1-m)+(-1.5+3.5*np.sqrt(np.maximum(0,1-(1-v)**2)))*m
  # Classification is restricted to the authored window banks. Each detected rectangle gets
  # one explicit bounding box, so glass, inset bevel, roughness and emission cannot diverge.
  allowed=np.zeros_like(h)
  for bb in r['window_rois']:allowed=np.maximum(allowed,(box(*bb)>-1).astype('float32'))
  bright=(rgb[:,:,0]>.22)&(rgb[:,:,1]>.10)&(rgb[:,:,0]>rgb[:,:,2]*2.3)&(allowed>.5)
  labs,num=label(bright)
  for sl in find_objects(labs):
   if sl is None:continue
   y,x=sl;area=(y.stop-y.start)*(x.stop-x.start)
   if area<24:continue
   bb=[x.start*256/N,y.start*256/N,x.stop*256/N,y.stop*256/N];a,b,c,d=bb
   if min(c-a,d-b)<.5:continue
   window_boxes.append(bb)
   outer=smooth(0,.18,box(a-.65,b-.65,c+.65,d+.65));lip=smooth(0,.2,box(a-.45,b-.45,c+.45,d+.45));inner=smooth(0,.16,box(a+.10,b+.10,c-.10,d-.10))
   h=h*(1-outer)+outer*(-1.0+1.65*lip-4.8*smooth(-.18,.2,box(a,b,c,d)))
   glass=np.maximum(glass,inner);structure=np.maximum(structure,outer);ao=ao*(1-outer)+outer*(.70+.25*inner)
  emit+=glass[:,:,None]*np.array([.68,.41,.13])
  # Glass has no metal or artificial bright spots; the entire pane glows uniformly.
 for bb in r['white']:
  m=smooth(0,.15,box(*bb))*smooth(.45,.8,rgb.min(-1));emit+=m[:,:,None]*np.array([.29,.30,.26])
 for bb in r['red']:
  m=smooth(0,.15,box(*bb))*smooth(.17,.42,rgb[:,:,0]-rgb[:,:,1]);emit+=m[:,:,None]*np.array([.48,.018,.005])
 paint=smooth(.13,.35,rgb.max(-1)-rgb.min(-1));metal=.48*(1-paint);metal=metal*(1-glass);rough=.72-.12*metal;rough=rough*(1-glass)+.46*glass
 # No relief on painted markings; structure around, not through, the name and caution bands.
 h*=1-flat
 for name,arr in [(stem+'_normal',normals(h)),(stem+'_orm',np.stack([ao,rough,metal],-1)),(stem+'_emissive',emit),(stem+'_height',(h+8)/16),(stem+'_glass',glass)]:save(arr,name)
 np.save(M/(stem+'_height.npy'),h)
 records.append(dict(material=stem,ribs=ribs,height_range=[float(h.min()),float(h.max())],normal_tilt_p95=float(np.percentile(np.degrees(np.arccos(normals(h)[:,:,2]*2-1)),95))))
 print('MATERIAL',stem,flush=True)
# Shared capital gun: explicit ribs, pipe cylinders, ports and panel seams.
for stem in ['orr_cgun','orr_sgun']:
 rgb=np.asarray(Image.open(M/(stem+'_source.png')).convert('RGB').resize((N,N),Image.Resampling.LANCZOS)).astype('float32')/255;save(rgb,stem)
 if stem=='orr_sgun':
  h=np.asarray(Image.open(M/'orr_sgun_height_source.png').convert('L').resize((N,N))).astype('float32')/255*8
  flat=np.asarray(Image.open(M/'orr_sgun_flat_source.png').convert('L').resize((N,N))).astype('float32')/255;h*=1-flat
 else:
  h=np.zeros((N,N),'float32')
  for a,b,c,d,axis,pitch in [(6,14,44,43,'y',6.4),(51,14,90,43,'y',6.2),(102,116,123,154,'y',3),(168,139,214,192,'x',4.5),(168,198,213,253,'x',8.5),(30,228,163,245,'x',2.7)]:
   m=smooth(0,.35,box(a,b,c,d));pos=X-a if axis=='x' else Y-b;rib=1-smooth(.16,min(.7,pitch*.25),abs((pos-pitch/2)%pitch-pitch/2));h=h*(1-m)+(-3+4.4*rib)*m
  for x in [167,190,212]:
   m=smooth(0,.2,line((x,43),(x,121),2.5));dist=np.minimum(abs(X-x)/2.5,1);h=h*(1-m)+(4*np.sqrt(1-dist*dist))*m
  for y in [94,105,116]:
   m=smooth(0,.2,line((160,y),(224,y),2.5));dist=np.minimum(abs(Y-y)/2.5,1);h=h*(1-m)+(3*np.sqrt(1-dist*dist))*m
  for cy in [122,133,145]:
   for cx in [44,56,68,80]:
    m=smooth(0,.5,3.1-np.hypot(X-cx,Y-cy));h-=4*m
  for a,b,c,d in [(2,51,156,51),(18,65,18,154),(30,155,164,155),(30,213,164,213),(165,137,165,253),(217,137,217,253),(50,155,50,213),(70,155,70,213),(105,155,105,213),(150,155,150,213),(230,43,230,116),(230,120,253,120)]:h-=1.6*smooth(0,.3,line((a,b),(c,d),.6))
  m=smooth(0,.4,line((139,12),(174,12),5));h=h*(1-m)+(-2+4*np.sqrt(np.clip(1-((Y-12)/5)**2,0,1)))*m
 save(normals(h),stem+'_normal');save((h+8)/16,stem+'_height');np.save(M/(stem+'_height.npy'),h)
 ao=1-.25*smooth(0,3,-h);metal=.45*(1-smooth(.12,.3,rgb.max(-1)-rgb.min(-1)));rough=.70-.12*metal
 save(np.stack([ao,rough,metal],-1),stem+'_orm')
 print('MATERIAL',stem,flush=True)
(W/'material_regions.json').write_text(json.dumps(dict(policy='Semantic structural geometry, fitted rib centre lines; rectangular pane geometry shared by all material channels',windows=window_boxes,materials=records),indent=2)+'\n')
print('WINDOWS',len(window_boxes),flush=True)
