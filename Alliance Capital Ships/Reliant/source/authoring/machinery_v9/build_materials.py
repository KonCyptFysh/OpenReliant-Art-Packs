"""Reauthor the three REL2 service bays from shared component geometry.

The old interior colour, normal, height and AO are replaced together. Polygon
frames remain from revision 8. Every pipe, collar and fastener uses the same
coverage and relief profile for colour and material maps, avoiding traced ghosts.
Fresh generated material art supplies wear only, never structural geometry.
"""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageFilter
D=Path('${RELIANT_WORKSPACE}')
W=D/'work/machinery_v9';M=D/'maps/machinery_v9';O=D/'maps/opaque_glass_v8';M.mkdir(exist_ok=True)
for p in O.iterdir():
    if not (M/p.name).exists():shutil.copy2(p,M/p.name)
# Atlas units below are 1024-space; outputs remain 4096 pixels.
box=(420,590,1024,710);a,b,c,d=[v*4 for v in box];H=d-b;N=c-a
y,x=np.mgrid[b:d,a:c].astype(np.float32);x=(x+.5)/4;y=(y+.5)/4
def smooth(lo,hi,v):
    t=np.clip((v-lo)/(hi-lo),0,1);return t*t*(3-2*t)
records=json.loads((D/'work/frame_relief_v6/measured-bevels.json').read_text())[17:20]
coverage=np.zeros((H,N),np.float32);edge_distance=np.zeros_like(coverage)
for rec in records:
    pts=np.array(rec['points']);inside=np.zeros((H,N),bool);distance=np.full((H,N),1e6,np.float32);width=np.zeros_like(distance)
    for i,((u,v),(w,z)) in enumerate(zip(pts,np.roll(pts,-1,axis=0))):
        vx,vy=w-u,z-v;t=np.clip(((x-u)*vx+(y-v)*vy)/(vx*vx+vy*vy),0,1)
        dd=np.hypot(x-u-t*vx,y-v-t*vy);near=dd<distance;distance[near]=dd[near];width[near]=rec['edges'][i]['width']
        if z!=v:inside^=((v>y)!=(z>y))&(x<(w-u)*(y-v)/(z-v)+u)
    signed=np.where(inside,distance,-distance)
    # Preserve the complete measured border ramp; a half-pixel blend starts only
    # on the recessed backing, beyond the existing frame's painted transition.
    cov=smooth(width/2+.15,width/2+.40,signed)
    coverage=np.maximum(coverage,cov);edge_distance=np.maximum(edge_distance,np.maximum(0,signed-width/2))
mask=coverage>0;interior=coverage>.999
source=Image.open(W/'worn-metal-source.png').convert('RGB')
# Tile a full-resolution quiet material swatch, without stretching small scratches.
src=np.asarray(source).astype(np.float32)/255
yy,xx=np.mgrid[:H,:N];weartex=src[(yy+157)%src.shape[0],(xx+307)%src.shape[1]]
lum=weartex@np.array([.2126,.7152,.0722],np.float32)
variation=np.clip((lum-.24)*1.3,-.10,.20)
chips=smooth(.32,.52,lum)
backing=-2.2
height=np.full((H,N),backing,np.float32)
colour=np.stack([.073+.10*variation,.080+.10*variation,.074+.09*variation],-1)
rough=np.clip(.79-.12*chips,.60,.85);metal=np.full((H,N),.08,np.float32)
occupied=np.zeros((H,N),np.float32);owners=np.zeros((H,N),np.uint16);components=[]
def put(name,cov,z,rgb,rg,mt):
    global height,colour,rough,metal,occupied
    idx=len(components)+1;components.append(dict(id=idx,name=name))
    z=np.broadcast_to(z,(H,N));take=(cov>0)&(z>=height-1e-5);alpha=np.where(take,cov,0)
    tone=np.array(rgb,np.float32)[None,None,:]*(1+variation[...,None]*.90)
    # Small real paint chips share coordinates across albedo, roughness and metal.
    tone=tone+chips[...,None]*.10
    colour=colour*(1-alpha[...,None])+tone*alpha[...,None]
    rough=rough*(1-alpha)+np.clip(rg-.09*chips,.22,.90)*alpha
    metal=metal*(1-alpha)+np.clip(mt+.10*chips,0,1)*alpha
    height=height*(1-alpha)+z*alpha
    owners[alpha>.5]=idx;occupied=np.maximum(occupied,cov)
def rect(name,cx,cy,w,h,z,rgb=(.23,.245,.23),rg=.62,mt=.32,bevel=.65):
    edge=np.minimum(w/2-abs(x-cx),h/2-abs(y-cy));cov=smooth(-.12,.12,edge)
    shape=backing+(z-backing)*smooth(0,bevel,edge)
    put(name,cov,shape,rgb,rg,mt)
    components[-1].update(kind='beveled_rectangle',center=[cx,cy],size=[w,h],top=z,bevel=bevel)
def disc(name,cx,cy,r,z,rgb=(.42,.44,.41),rg=.39,mt=.65):
    dist=np.hypot(x-cx,y-cy);cov=smooth(-.12,.12,r-dist)
    shape=backing+(z-backing)*smooth(0,.35,r-dist)
    put(name,cov,shape,rgb,rg,mt);components[-1].update(kind='fastener',center=[cx,cy],radius=r,top=z)
def tube(name,p,q,r,zbase,depth,rgb=(.35,.375,.35),rg=.46,mt=.52):
    p=np.array(p);q=np.array(q);v=q-p;length=np.linalg.norm(v);v=v/length
    along=(x-p[0])*v[0]+(y-p[1])*v[1];across=(x-p[0])*(-v[1])+(y-p[1])*v[0]
    radial=abs(across);edge=np.minimum.reduce([r-radial,along,length-along]);cov=smooth(-.12,.12,edge)
    section=np.sqrt(np.maximum(0,1-(radial/r)**2))
    top=zbase+depth*section
    top=backing+(top-backing)*smooth(0,.35,np.minimum(along,length-along))
    put(name,cov,top,rgb,rg,mt)
    components[-1].update(kind='cylindrical_conduit',start=p.tolist(),end=q.tolist(),radius=r,base=zbase,depth=depth)

# A single coherent service route continues behind the diagonal frame members.
# Small secondary lines and branches sit behind the larger main conduit.
for cx in [473,540,602,721,770,870,941,991]:
    rect('main_pipe_mount',cx,642,8.0,23.0,-1.35,rg=.69)
    for cy in [633.2,650.8]:disc('mount_fastener',cx,cy,1.0,-.65)
for cx in [487,579,741,784,906,953]:
    rect('branch_foot',cx,688,8,7,-1.4,rgb=(.20,.22,.205),rg=.67)
    for dx in [-2.5,2.5]:disc('branch_foot_bolt',cx+dx,688,.7,-.8)
    tube('return_branch',(cx,641),(cx,690),2.4,-1.6,2.9,rgb=(.285,.315,.30),rg=.51,mt=.42)
    tube('branch_lower_collar',(cx,682),(cx,686),3.2,-1.1,3.1,rgb=(.32,.35,.33),rg=.43,mt=.59)
tube('secondary_service_line',(421,675.5),(1020,675.5),2.25,-1.3,2.7,rgb=(.27,.30,.285),rg=.52,mt=.46)
for cx in [455,519,589,680,758,800,913,975]:
    tube('secondary_coupling',(cx-1.4,675.5),(cx+1.4,675.5),3.05,-.9,2.9,rgb=(.34,.36,.335),rg=.44,mt=.58)
for cx,cy in [(520,614),(607,617),(736,610),(863,613),(972,619)]:
    rect('upper_feed_wall_socket',cx,cy+1,7.5,7,-1.2,rgb=(.22,.24,.22),rg=.66)
    for dx in [-2.6,2.6]:disc('feed_socket_fastener',cx+dx,cy+1,.6,-.7)
    tube('upper_feed',(cx,cy),(cx,643),2.2,-1.6,2.7,rgb=(.285,.31,.29),rg=.51,mt=.46)
    tube('upper_feed_ferrule',(cx,cy+1),(cx,cy+4),2.9,-1.2,2.9,rgb=(.35,.37,.34),rg=.43,mt=.60)
tube('primary_service_conduit',(420,642),(1024,642),4.5,-.65,4.4)
for cx in [473,540,602,721,770,870,941,991]:
    # Wide retaining sleeve plus thin raised rims, all concentric with the tube.
    tube('retaining_sleeve',(cx-2.6,642),(cx+2.6,642),5.2,-.50,4.9,rgb=(.255,.28,.26),rg=.52,mt=.50)
    for dx in [-2.1,2.1]:tube('sleeve_rim',(cx+dx-.45,642),(cx+dx+.45,642),5.5,-.45,5.0,rgb=(.40,.425,.39),rg=.38,mt=.68)
# Two compact service housings retain the original red identification accents.
for cx,cy,w,h in [(636,625,9,13),(557,662,12,15)]:
    rect('service_box_back',cx,cy,w+2,h+2,-.7,rgb=(.24,.265,.25),rg=.62)
    rect('service_box_lid',cx,cy,w,h,.7,rgb=(.18,.20,.185),rg=.63,bevel=.8)
    rect('red_service_label',cx,cy,2.4,5,.82,rgb=(.32,.023,.015),rg=.74,mt=.02,bevel=.25)
    for dy in [-h/2+2,h/2-2]:disc('lid_fastener',cx,cy+dy,.55,1.05)

# Shared component coverage drives contact occlusion; no directional shadows are
# painted into the colour. The normal response supplies the cylindrical lighting.
blur=np.asarray(Image.fromarray(np.uint8(occupied*255+.5)).filter(ImageFilter.GaussianBlur(4.5))).astype(np.float32)/255
ao=np.clip(.94-.23*blur*(1-occupied)-.17*(1-smooth(0,4,edge_distance)),.55,1)
ao=np.where(occupied>.8,.94,ao)
oldh=np.load(O/'orr2_hull_height.npy');allh=oldh.copy()
part=oldh[b:d,a:c]*4;newh=part*(1-coverage)+height*coverage;allh[b:d,a:c]=newh/4
names=['orr2_hull.png','orr2_hull_orm.png','orr2_hull_normal.png']
base=np.array(Image.open(O/names[0]));orm=np.array(Image.open(O/names[1]));normal=np.array(Image.open(O/names[2]))
def install(dest,new):
    patch=dest[b:d,a:c];new=np.uint8(np.clip(new,0,1)*255+.5)
    mix=np.uint8(patch.astype(np.float32)*(1-coverage[...,None])+new*coverage[...,None]+.5)
    patch[mask]=mix[mask]
install(base,colour);install(orm,np.stack([ao,rough,metal],-1))
dy,dx=np.gradient(allh[b-2:d+2,a-2:c]*4,.25)
nx=-dx*.85;ny=dy*.85;scale=np.maximum(1,np.hypot(nx,ny)/3.2)
v=np.stack([nx/scale,ny/scale,np.ones_like(nx)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
newnormal=np.uint8(np.clip(v*.5+.5,0,1)*255+.5)[2:-2,2:]
# Normals are changed only inside the same bay masks. The untouched border is
# outside the full bevel, and its source frame normals are retained byte-for-byte.
normal[b:d,a:c][mask]=newnormal[mask]
for name,arr in zip(names,[base,orm,normal]):Image.fromarray(arr).save(M/name)
np.save(M/'orr2_hull_height.npy',allh)
hi=np.array(Image.open(O/'orr2_hull_height.png'));hp=hi[b:d,a:c];nh=np.uint8(np.clip((allh[b:d,a:c]+8)/16,0,1)*255+.5);hp[mask]=nh[mask];Image.fromarray(hi).save(M/'orr2_hull_height.png')
fullmask=np.zeros((4096,4096),np.uint8);fullmask[b:d,a:c]=np.uint8(mask)*255;Image.fromarray(fullmask).save(W/'bay-edit-mask.png')
Image.fromarray(owners).save(W/'component-ids.png')
Image.fromarray(base).crop((a,b,c,d)).save(W/'new-panel-colour.png')
Image.fromarray(normal).crop((a,b,c,d)).save(W/'new-panel-normal.png')
(W/'component-layout.json').write_text(json.dumps(dict(revision=9,coordinates='1024 atlas units',bays=[17,18,19],source_mode='built-in ImageGen material swatch plus authored component profiles',components=components,frame_preserved=True,old_interior_channels_replaced=['base_colour','height','normal','ambient_occlusion','roughness','metallic']),indent=2)+'\n')
print('THREE MACHINERY BAYS REAUTHORED:',len(components),'components;',int(mask.sum()),'pixels',flush=True)
