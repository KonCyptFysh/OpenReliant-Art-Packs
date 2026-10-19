"""Assemble generated opaque glazing inside the revision-5 glass apertures.
Revision-6 structural relief and revision-7 native UVs are the starting point.
Only pane interiors change; the accepted steel bezels and seals remain exact.
"""
from pathlib import Path
import json, shutil, hashlib
import numpy as np
from PIL import Image, ImageFilter

D=Path('${RELIANT_WORKSPACE}')
W=D/'work/opaque_glass_v8'; M=D/'maps/opaque_glass_v8'; PREV=D/'maps/frame_relief_v6'
M.mkdir(exist_ok=True)
for p in PREV.iterdir():
    if not (M/p.name).exists(): shutil.copy2(p,M/p.name)
records=json.loads((D/'work/windows_v5/window-material-regions.json').read_text())['windows']
art=Image.open(W/'opaque-glass-art-source.png').convert('RGB')
# Same glass crop as the original artwork. Frames are never copied from the new image.
glass_art=art.crop((108,204,2064,506))
names=['orr2_hull.png','orr2_hull_emissive.png','orr2_hull_orm.png','orr2_hull_normal.png']
arrays={n:np.array(Image.open(PREV/n).convert('RGB')) for n in names}
base,emit,orm,normal=[arrays[n] for n in names]
h=np.load(PREV/'orr2_hull_height.npy').copy()*4
mask=np.zeros(h.shape,np.uint8)
def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
metrics=[]
for rec in records:
    i=rec['id']; rng=np.random.default_rng(8800+i)
    a,b,c,d=rec['outer_frame']; width,height=c-a,d-b
    vertical=rec['vertical_atlas']; cw,ch=(height,width) if vertical else (width,height)
    iw,ih=cw-14,ch-14
    gh=glass_art.height; gw=min(glass_art.width,round(gh*iw/ih))
    start=int(rng.integers(0,max(1,glass_art.width-gw+1)))
    g=glass_art.crop((start,0,start+gw,gh)).resize((iw,ih),Image.Resampling.LANCZOS)
    # Edge padding keeps the actual aperture registered with its seven-pixel inset.
    patch=Image.fromarray(np.pad(np.array(g),((7,7),(7,7),(0,0)),mode='edge'))
    orient=rec['orientation']
    if vertical: patch=patch.transpose(Image.Transpose.ROTATE_90 if orient['sign']>0 else Image.Transpose.ROTATE_270)
    elif orient['sign']<0: patch=patch.transpose(Image.Transpose.ROTATE_180)
    pixels=np.asarray(patch).astype(np.float32)/255
    lumin=pixels@np.array([.2126,.7152,.0722],np.float32)
    yy,xx=np.mgrid[:height,:width].astype(np.float32)
    dist=np.minimum.reduce([xx+.5,width-xx-.5,yy+.5,height-yy-.5])
    gm=smooth(6.7,7.7,dist); changed=gm>0
    sm=np.asarray(Image.fromarray(np.uint8(lumin*255+.5)).filter(ImageFilter.GaussianBlur(1.1))).astype(np.float32)/255
    fine=np.clip(abs(lumin-sm)*7,0,1)
    edgegrime=(1-smooth(7,12,dist))*gm
    # Neutral opaque glazing remains subdued when power is off. Source surface
    # marks subtly influence its finish, with no room imagery in any channel.
    albedo=(.10+.13*lumin)[...,None]*np.array([1,.94,.82],np.float32)
    q=base[b:d,a:c]; replacement=np.uint8(np.clip(albedo,0,1)*255+.5)
    q[changed]=replacement[changed]
    # Warm ivory-amber transmitted light, with modest pane-to-pane variation.
    # Brightness belongs to emission and therefore follows existing power faults.
    value=(.40+.32*lumin)*(.94+.10*rng.random())
    tint=np.array([1,.79,.50],np.float32)
    e=value[...,None]*tint*gm[...,None]
    emit[b:d,a:c][changed]=np.uint8(np.clip(e,0,1)*255+.5)[changed]
    op=orm[b:d,a:c]
    op[...,1][changed]=np.uint8(np.clip(.34+.10*fine+.12*edgegrime,0,1)*255+.5)[changed]
    op[...,2][changed]=0
    # Original recess and bezel shape, with only fine glass-film relief replaced.
    field=rec['backing_height']+.65*smooth(0,1.5,dist)-1.85*smooth(4.3,6.3,dist)-.75*smooth(6.5,7.5,dist)-.012*fine*gm
    h[b:d,a:c][changed]=field[changed]
    mask[b:d,a:c][changed]=255
    metrics.append(dict(id=i,source_crop=[start,0,start+gw,gh],mean_emission_rgb=emit[b:d,a:c][gm>.99].mean(axis=0).tolist()))
# Compute each aperture locally to retain every unrelated normal byte.
for rec in records:
    a,b,c,d=rec['outer_frame']; hp=h[b-2:d+2,a-2:c+2]
    dy,dx=np.gradient(hp,.25); nx=-dx*.85; ny=dy*.85
    scale=np.maximum(1,np.hypot(nx,ny)/2.2)
    v=np.stack([nx/scale,ny/scale,np.ones_like(hp)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
    n=np.uint8(np.clip(v*.5+.5,0,1)*255+.5)[2:-2,2:-2]
    use=mask[b:d,a:c]>0; normal[b:d,a:c][use]=n[use]
for name,arr in arrays.items(): Image.fromarray(arr).save(M/name)
np.save(M/'orr2_hull_height.npy',h/4)
oldheight=np.array(Image.open(PREV/'orr2_hull_height.png'))
newheight=np.uint8(np.clip((h/4+8)/16,0,1)*255+.5)
oldheight[mask>0]=newheight[mask>0];Image.fromarray(oldheight).save(M/'orr2_hull_height.png')
Image.fromarray(mask).save(W/'glass-edit-mask.png')
(W/'material-assembly.json').write_text(json.dumps(dict(revision=8,window_count=len(records),source_mode='built-in ImageGen with registered material assembly',source_sha256=hashlib.sha256((W/'opaque-glass-art-source.png').read_bytes()).hexdigest(),window_layout_source=str(D/'work/windows_v5/window-material-regions.json'),frames_and_gaskets_retained=True,panes=metrics),indent=2)+'\n')
print('64 OPAQUE GLASS PANES ASSEMBLED; FRAMES PRESERVED',flush=True)
