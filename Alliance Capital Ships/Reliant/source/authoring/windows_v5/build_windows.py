"""Reliant window material assembly. Art: retained built-in ImageGen source.
Nine-slice installation into the 64 existing rectangles. One coordinate definition
controls the colour insert, metal bezel, gasket, glass, relief and emission.
No diffuse brightness is interpreted as structural height. Native meshes untouched.
"""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
D=Path('${RELIANT_WORKSPACE}');W=D/'work/windows_v5';M=D/'maps/windows_v5';PREV=D/'maps/alignment_v4';M.mkdir(exist_ok=True)
for p in PREV.iterdir():
 if not (M/p.name).exists():shutil.copy2(p,M/p.name)
N=4096
art=Image.open(W/'window-art-source.png').convert('RGB')
# Source bezel's outside bounds and glass aperture, measured from the retained image.
source=art.crop((32,126,2140,582));sx=[0,76,2032,2108];sy=[0,78,380,456]
glass_art=source.crop((sx[1],sy[1],sx[2],sy[2]))
windows=json.loads((D/'work/refinement_v2/material_regions.json').read_text())['windows']
orientations=json.loads((W/'window-orientation.json').read_text())
polys=json.loads((D/'work/alignment_v4/measured-geometry.json').read_text())['pockets']
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def inside(p,xy):
 x,y=xy;ans=False
 for (u,v),(w,z) in zip(p,p[1:]+p[:1]):
  if z!=v and ((v>y)!=(z>y)) and x<(w-u)*(y-v)/(z-v)+u:ans=not ans
 return ans
# All old pixels outside the exact window patches are retained byte-for-byte.
base=np.array(Image.open(PREV/'orr2_hull.png').convert('RGB'))
emit=np.array(Image.open(PREV/'orr2_hull_emissive.png').convert('RGB'))
orm=np.array(Image.open(PREV/'orr2_hull_orm.png').convert('RGB'))
normal=np.array(Image.open(PREV/'orr2_hull_normal.png').convert('RGB'))
h=np.asarray(Image.fromarray(np.load(PREV/'orr2_hull_height.npy')*4).resize((N,N),Image.Resampling.BICUBIC)).copy()
glassmask=np.zeros((N,N),np.uint8);framemask=glassmask.copy();editmask=glassmask.copy();normalmask=glassmask.copy();record=[]
# Clear all previous recesses before writing any new frame so nearby windows
# cannot erase one another's already-authored bevels.
for bb in windows:
 x0,y0,x1,y1=np.rint(np.array(bb)*16).astype(int)
 center=((x0+x1)/8,(y0+y1)/8);backing=-10 if any(inside(p,center) for p in polys) else 0
 h[y0-8:y1+8,x0-8:x1+8]=backing
# Deterministic source sampling keeps each window's interior distinct without
# changing its count or external rectangular silhouette.
for index,bb in enumerate(windows):
 rng=np.random.default_rng(5900+index)
 x0,y0,x1,y1=np.rint(np.array(bb)*16).astype(int);a,b,c,d=x0-4,y0-4,x1+4,y1+4
 assert min(a,b)>=0 and max(c,d)<=N
 width,height=c-a,d-b;orientation=orientations[index];vertical=orientation["axis"]==0;cw,ch=(height,width) if vertical else (width,height)
 border=7;inner_w,inner_h=cw-2*border,ch-2*border
 patch=Image.new('RGB',(cw,ch));tx=[0,border,cw-border,cw];ty=[0,border,ch-border,ch]
 for row in range(3):
  for col in range(3):
   if row==1 and col==1:continue
   crop=source.crop((sx[col],sy[row],sx[col+1],sy[row+1]));patch.paste(crop.resize((tx[col+1]-tx[col],ty[row+1]-ty[row]),Image.Resampling.LANCZOS),(tx[col],ty[row]))
 # Crop a different part of the same real glazed/interior texture for each opening.
 gh=glass_art.height;gw=min(glass_art.width,round(gh*inner_w/inner_h));start=int(rng.integers(0,max(1,glass_art.width-gw+1)))
 g=glass_art.crop((start,0,start+gw,gh)).resize((inner_w,inner_h),Image.Resampling.LANCZOS)
 if index%3==1:g=g.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 patch.paste(g,(border,border))
 if vertical:patch=patch.transpose(Image.Transpose.ROTATE_90 if orientation["sign"]>0 else Image.Transpose.ROTATE_270)
 elif orientation["sign"]<0:patch=patch.transpose(Image.Transpose.ROTATE_180)
 pixels=np.asarray(patch).astype(np.float32)/255
 yy,xx=np.mgrid[:height,:width].astype(np.float32);dist=np.minimum.reduce([xx+.5,width-xx-.5,yy+.5,height-yy-.5])
 gm=smooth(6.7,7.7,dist);frame=1-smooth(4.4,5.2,dist);gasket=smooth(4.8,5.4,dist)*(1-smooth(6.4,7.2,dist))
 # Dark neutral bronze albedo. The cabin light is in the emissive map, not baked
 # into an orange albedo block. Dirt/scratches from the generated glass remain visible.
 baseglass=pixels*.40+np.array([.018,.024,.027],np.float32)
 colour=pixels*(1-gm[...,None])+baseglass*gm[...,None]
 base[b:d,a:c]=np.uint8(np.clip(colour,0,1)*255+.5)
 lumin=pixels@np.array([.2126,.7152,.0722],np.float32)
 # Emission varies with visible cabin illumination, bounded to avoid clipping.
 # Source dirt and shadows attenuate it; neither frame nor gasket is emissive.
 intensity=(.016+.38*np.clip(lumin/.64,0,1)**1.65)*(0.85+.30*rng.random())
 e=intensity[...,None]*np.array([1.0,.69,.39])*gm[...,None]
 emit[b-4:d+4,a-4:c+4]=0
 emit[b:d,a:c]=np.uint8(np.clip(e,0,1)*255+.5)
 # PBR: dielectric glazing, rough seals, worn painted steel with exposed chips.
 # Fine texture detail changes glass roughness, never its macro shape.
 sm=np.asarray(Image.fromarray(np.uint8(lumin*255)).filter(ImageFilter.GaussianBlur(1.1))).astype(np.float32)/255
 fine=np.clip(abs(lumin-sm)*7,0,1)
 edgegrime=(1-smooth(7,11,dist))*gm
 glassrough=np.clip(.19+.13*(1-lumin)+.16*fine+.14*edgegrime,.19,.65)
 rough=.67*frame+.87*gasket+glassrough*gm
 gap=np.clip(1-frame-gasket-gm,0,1);rough+=.63*gap
 wear=smooth(.32,.62,lumin)*frame
 metal=(.30+.40*wear)*frame
 ao=np.clip(.97-.28*gasket-.15*edgegrime,.62,1)
 orm[b:d,a:c]=np.uint8(np.clip(np.stack([ao,rough,metal],-1),0,1)*255+.5)
 center=((x0+x1)/8,(y0+y1)/8);backing=-10 if any(inside(p,center) for p in polys) else 0
 # Remove the complete old glass bevel first, leaving the surrounding relief intact.
 pad=4
 # Profile in 1024-atlas height units: modest proud bezel, inner chamfer, recessed glass.
 field=backing+.65*smooth(0,1.5,dist)-1.85*smooth(4.3,6.3,dist)-.75*smooth(6.5,7.5,dist)
 # Sub-pixel scratch relief affects the surface film only, not interior scenery.
 field-=.018*fine*gm
 h[b:d,a:c]=field
 glassmask[b:d,a:c]=np.uint8(gm*255+.5);framemask[b:d,a:c]=np.uint8(frame*255+.5);editmask[b-pad:d+pad,a-pad:c+pad]=255;normalmask[b-pad-2:d+pad+2,a-pad-2:c+pad+2]=255
 record.append(dict(id=index,previous_glass=[int(x0),int(y0),int(x1),int(y1)],outer_frame=[int(a),int(b),int(c),int(d)],glass_inset_pixels=border,vertical_atlas=bool(vertical),orientation=orientation,source_glass_crop=[start,0,start+gw,gh],backing_height=backing))
# Smooth analytical profiles generate normals. Copy only the changed neighbourhoods.
dy,dx=np.gradient(h,.25);nx=-dx*.85;ny=dy*.85;scale=np.maximum(1,np.hypot(nx,ny)/2.2);v=np.stack([nx/scale,ny/scale,np.ones_like(h)],-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
n=np.uint8(np.clip(v*.5+.5,0,1)*255+.5);normal[normalmask>0]=n[normalmask>0]
for arr,name in [(base,'orr2_hull'),(emit,'orr2_hull_emissive'),(orm,'orr2_hull_orm'),(normal,'orr2_hull_normal'),(glassmask,'orr2_hull_glass'),(framemask,'orr2_hull_window_frame')]:Image.fromarray(arr).save(M/(name+'.png'))
np.save(M/'orr2_hull_height.npy',h/4);Image.fromarray(np.uint8(np.clip((h/4+8)/16,0,1)*255+.5)).save(M/'orr2_hull_height.png')
Image.fromarray(editmask).save(W/'window-edit-mask.png');Image.fromarray(normalmask).save(W/'window-normal-edit-mask.png')
# Semantic masks are only source assets; runtime still has one canonical atlas set.
(W/'window-material-regions.json').write_text(json.dumps(dict(revision=5,source_image='window-art-source.png',source_sha256=hashlib.sha256((W/'window-art-source.png').read_bytes()).hexdigest(),source_mode='built-in imagegen',height_resolution=4096,window_count=len(record),windows=record),indent=2)+'\n')
Image.fromarray(base).crop((0,900,456,1700)).rotate(270,expand=True).resize((1200,684)).save(W/'bridge-window-art-preview.png')
Image.fromarray(base).crop((1840,600,2920,896)).resize((1350,370)).save(W/'forward-window-art-preview.png')
print('WINDOW_MATERIALS_READY',len(record),flush=True)
