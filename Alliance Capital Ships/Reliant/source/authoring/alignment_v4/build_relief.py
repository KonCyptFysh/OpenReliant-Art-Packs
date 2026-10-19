"""Revision 4: repair REL2 pocket and pipe geometry against current base pixels.
Uses revision 3 as input; other atlases, native data, albedo and emission preserved.
Trace seeds select structural frame ridges. Each edge is then measured in the 4K
image using a narrow, achromatic brightness profile and robust line fitting.
These are structural masks, not a luminance-to-height conversion of the artwork.
"""
from pathlib import Path
import numpy as np, json, shutil
from PIL import Image, ImageDraw
D=Path('${RELIANT_WORKSPACE}');W=D/'work/alignment_v4';M=D/'maps/alignment_v4';PREV=D/'maps/alignment_v3';M.mkdir(exist_ok=True)
for p in PREV.iterdir():
 if not (M/p.name).exists():shutil.copy2(p,M/p.name)
# Reuse only the geometric rasterizer from the latest source, not its old geometry.
src=(D/'work/alignment_v3/build_relief.py').read_text();ns={};exec(src[src.index('def smooth'):src.index('# Hull 1:')],dict(Path=Path,np=np,json=json,Image=Image,ImageDraw=ImageDraw,D=D,W=W,OLD=PREV,M=M,N=2048,K=2),ns)
# Methods resolve helpers from the shared global namespace.
ns['Relief'].__init__.__globals__.update(ns);Relief=ns['Relief'];smooth=ns['smooth'];a=Relief(2)
rgb=np.asarray(Image.open(PREV/'orr2_hull.png').convert('RGB')).astype(np.float32)
grey=rgb.mean(-1);chroma=rgb.max(-1)-rgb.min(-1)
score=grey*np.clip(1-chroma/24,0,1)
seeds=[
[(9.5,39),(21,25),(54,25),(66,39),(66,51),(26,91),(17,91),(9.5,84)],
[(9.5,126),(75,60.5),(88.5,60.5),(106,79),(106,215.5),(93.5,228.5),(83.5,228.5),(9.5,154)],
[(9.5,236),(31,216.5),(47,216.5),(106,274),(106,352),(36,421),(22,421),(9.5,408.5)],
[(9.5,465),(75,403),(87.5,403),(106,421.5),(106,490),(88,508),(31,508),(9.5,487)],
[(9.5,541),(21,528),(54,528),(66,541),(66,553),(26,594),(17,594),(9.5,587)],
[(9.5,629),(75,563),(88,563),(106,582),(106,718),(93,732),(83,732),(9.5,658)],
[(9.5,739),(31,719),(47,719),(106,776),(106,854),(36,924),(22,924),(9.5,911)],
[(9.5,969),(75,906),(87,906),(106,925),(106,994),(88,1013),(31,1013),(9.5,990)],
[(187.5,157),(203,142.5),(244,142.5),(273,168),(273,229),(265,237),(254,237),(187.5,172)],
[(188.5,209),(196,201),(204,201),(241,238),(241,246),(229,257.5),(198.5,257.5),(188.5,247)],
[(295,157),(310,142.5),(350,142.5),(378.5,168),(378.5,229),(370,237),(360,237),(295,172)],
[(296,210),(303.5,201),(311.5,201),(348.5,238),(348.5,246),(336.5,257.5),(306,257.5),(296,247)],
[(465,103),(482,86),(551,86),(578,111),(578,123),(559,141),(482,141),(465,124)],
[(587.5,102),(603,86),(708,86),(723,101),(723,112),(689,141),(620,141),(587.5,111)],
[(768,86),(802,86),(818,103),(818,112),(790,141),(737,141),(727,133),(727,126)],
[(465,178),(482,162),(550,162),(578,187),(578,199),(559,217),(482,217),(465,199)],
[(587.5,178),(603,162),(708,162),(723,177),(723,185),(689,217),(620,217),(587.5,186)],
[(428,635),(465,598),(650,598),(665,615),(665,630),(600,698),(448,698),(428,679)],
[(654,663),(718,598),(775,598),(822,649),(822,674),(799,698),(670,698),(654,682)],
[(819,614),(833,600),(991,600),(1015,622),(1015,660),(978,698),(889,698),(819,629)]
]
# Ridge sampling uses absolute 4K coordinates; one atlas unit = four pixels.
fitlog=[]
def fit_poly(points,lock_diagonal=False):
 points=np.array(points,float); lines=[]
 for p,q in zip(points,np.roll(points,-1,axis=0)):
  v=q-p
  if lock_diagonal and abs(v[0])>.01 and abs(v[1])>.01:
   center=(p+q)/2;length=np.linalg.norm(v);v=np.sign(v)*length/np.sqrt(2);p=center-v/2;q=center+v/2
  length=np.linalg.norm(v);tangent=v/length;normal=np.array([-tangent[1],tangent[0]])
  t=np.linspace(.17,.83,max(16,int(length*2)));ss=np.linspace(-3.25,3.25,53)
  coords=p+t[:,None]*v; samples=coords[:,None,:]+ss[None,:,None]*normal
  xi=np.clip((samples[:,:,0]*4).astype(int),0,4095);yi=np.clip((samples[:,:,1]*4).astype(int),0,4095);val=score[yi,xi]
  # Local brightest ridge, then subpixel centroid around the peak (not its shadows).
  peaks=val.argmax(1);win=abs(np.arange(len(ss))[None,:]-peaks[:,None])<=3
  weight=(np.maximum(val-val.min(1)[:,None],0)**3)*win;offs=(weight*ss).sum(1)/np.maximum(weight.sum(1),1e-9)
  keep=np.ones(len(t),bool)
  for _ in range(4):
   co=np.polyfit(t[keep]*length,offs[keep],1);resid=offs-np.polyval(co,t*length);keep=abs(resid-np.median(resid))<max(.38,2.5*np.median(abs(resid-np.median(resid))))
  if lock_diagonal or abs(v[0])<.01 or abs(v[1])<.01:co=np.array([0,np.median(offs[keep])])
  nn=normal-co[0]*tangent;nn/=np.linalg.norm(nn);c=float(np.dot(nn,p+normal*co[1]));lines.append((nn,c))
  fitlog.append(dict(seed=[p.tolist(),q.tolist()],samples=int(keep.sum()),median_residual=float(np.median(abs(resid[keep]))),max_offset=float(abs(offs[keep]).max())))
 result=[]
 for j,(nn,c) in enumerate(lines):
  prev,pc=lines[j-1];result.append(np.linalg.solve(np.array([prev,nn]),np.array([pc,c])).tolist())
 return result
polys=[fit_poly(p,8<=j<=11) for j,p in enumerate(seeds)]
for p in polys:a.polygon([tuple(q) for q in p],-10,3.4)
pocket_height=a.h.copy()
# Pipes: measured full painted widths, rounded cross-sections and their real endpoints.
# Continuous pipes run behind braces; the pocket mask clips them at the frame.
pipes=[
# main horizontal manifold and two lower runs
[(433,640),(1014,640),6.0,7.0],
[(432,675),(501,675),3.5,4.0],[(663,676),(773,676),3.5,4.0],[(906,676),(991,676),2.6,3.0],
# first pocket, including the large union and lower uprights
[(467,644),(467,683),5.5,6.0],[(521,647),(521,684),4.5,5.0],[(577,644),(577,695),5.5,6.0],
[(548,610),(548,637),4.5,5.0],[(577,612),(577,637),4.5,5.0],[(624,619),(624,640),4.0,4.5],
# middle pocket
[(678,667),(678,693),3.5,4.0],[(726,645),(726,696),5.5,6.0],[(785,643),(785,696),5.0,5.5],
[(725,606),(725,637),4.0,4.5],[(754,611),(754,638),4.0,4.5],
# right pocket. Do not add a guessed horizontal pipe through the dark backing.
[(873,645),(873,680),4.5,5.0],[(901,644),(901,695),5.0,5.5],
[(859,605),(859,632),3.3,4.0],[(888,610),(888,636),3.5,4.0]
]
# Construct independently; combining with max avoids the old h<0 intersection holes.
pipefield=np.zeros_like(a.h)
for p,q,r,rise in pipes:
 p=np.array(p);q=np.array(q);v=q-p;length=np.linalg.norm(v);axis=v/length
 def op(x,y,h):
  along=(x-p[0])*axis[0]+(y-p[1])*axis[1];d=abs((x-p[0])*axis[1]-(y-p[1])*axis[0]);u=np.clip(d/r,0,1)
  profile=np.cos(u*np.pi/2)**2
  cap=smooth(-r*.4,r*.4,along)*(1-smooth(length-r*.4,length+r*.4,along))
  return np.maximum(h,rise*.65*profile*cap)
 old=a.h;a.h=pipefield;a.apply((min(p[0],q[0])-r,min(p[1],q[1])-r,max(p[0],q[0])+r,max(p[1],q[1])+r),op);pipefield=a.h;a.h=old
 a.records.append(dict(kind='measured_pipe',a=p.tolist(),b=q.tolist(),radius=r,rise=rise))
 a.draw.line([tuple(p),tuple(q)],fill=(30,210,255),width=1)
a.h=pocket_height+pipefield*smooth(2,7,-pocket_height)
# Preserve the unrelated panel-joint paths from revision 3.
for rec in json.loads((D/'work/alignment_v3/geometry-2.json').read_text()):
 if rec['kind']=='groove':a.line(tuple(rec['a']),tuple(rec['b']),rec['width'],rec['depth'])
# Glass bounds remain shared with colour/emission. Depth is relative to its backing,
# so inset depth is consistent on both framed cells and flat strips.
windows=json.loads((D/'work/refinement_v2/material_regions.json').read_text())['windows']
for bb in windows:
 x0,y0,x1,y1=np.array(bb)*4
 backing=float(pocket_height[int((y0+y1)):int((y0+y1))+1,int((x0+x1)):int((x0+x1))+1].mean())
 depth=backing-4.5 if backing<-1 else -19
 def win(x,y,h):
  dist=np.minimum.reduce([x-x0,x1-x,y-y0,y1-y]);m=smooth(-1.3,.7,dist);return h*(1-m)+depth*m
 a.apply((x0-2,y0-2,x1+2,y1+2),win)
a.save()
# Keep roughness and metallic at their current full-resolution values.
orm=np.array(Image.open(M/'orr2_hull_orm.png'));oldorm=np.asarray(Image.open(PREV/'orr2_hull_orm.png'));orm[:,:,1:]=oldorm[:,:,1:];Image.fromarray(orm).save(M/'orr2_hull_orm.png')
# Save exact source paths and quantitative trace evidence.
(W/'measured-geometry.json').write_text(json.dumps(dict(coordinates='1024 atlas units, measured from 4096 base',pockets=polys,pipes=pipes,edge_fits=fitlog),indent=2)+'\n')
# Full resolution overlay for inspection; show outer ramp and completion edges.
over=Image.open(PREV/'orr2_hull.png').convert('RGB');dr=ImageDraw.Draw(over)
for p in polys:
 pts=[tuple(v*4 for v in q) for q in p];dr.line(pts+[pts[0]],fill=(255,65,65),width=2)
for p,q,r,rise in pipes:dr.line([tuple(v*4 for v in p),tuple(v*4 for v in q)],fill=(35,230,240),width=2)
over.save(W/'measured-trace-4k.png')
for name,bb in [('bank-upper',(0,10,114,515)),('bank-lower',(0,520,114,1024)),('small',(184,136,390,270)),('horizontal',(458,78,824,224)),('pipes',(425,590,1023,704))]:over.crop(tuple(v*4 for v in bb)).save(W/(name+'-trace.png'))
print('V4_REL2_MAPS_READY',flush=True)
