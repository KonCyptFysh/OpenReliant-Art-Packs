"""Structural PBR data authored independently of colour highlights and wear."""
import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];M=D/'maps';W=D/'work/reconstruction_v1';N=1254;OUT=2048
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGB'
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
def box(a,b,c,d):return np.minimum(np.minimum(X-a,c-X),np.minimum(Y-b,d-Y))
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-9),0,1)
 return r-np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
def apply(d,z,f=0):
 global h,structure,fins
 m=smooth(-.3,.5,d);h=h*(1-m)+z*m;structure=np.maximum(structure,m);fins=np.maximum(fins,f)
# Individual atlas openings: cavity floors and fin crests are separate masks.
vent_boxes=[(22,108,72,201,4,'v'),(104,151,134,362,20,'h'),(164,149,215,225,7,'h'),(321,137,346,425,9,'h'),(359,136,397,396,2,'v'),(208,344,256,629,28,'h'),(279,343,306,630,28,'h'),(8,449,136,572,7,'h'),(8,574,120,633,4,'h'),(381,658,458,707,5,'v'),(474,587,497,644,4,'h'),(480,548,541,571,5,'h'),(807,752,855,838,7,'h'),(335,890,357,1004,10,'h'),(381,890,402,1004,10,'h'),(848,934,907,982,4,'v'),(865,1120,913,1190,6,'h'),(1118,655,1164,689,5,'h'),(1104,297,1168,316,4,'h'),(1104,349,1169,434,3,'h'),(872,612,902,630,3,'h')]
for a,b,c,d,count,axis in vent_boxes:
 dst=box(a,b,c,d);f=np.zeros_like(h);start=a if axis=='v' else b;length=c-a if axis=='v' else d-b;coord=X if axis=='v' else Y;pitch=length/count
 for i in range(count):f=np.maximum(f,1-smooth(pitch*.20,pitch*.39,np.abs(coord-(start+(i+.5)*pitch))))
 f*=smooth(1.4,3,dst);apply(dst,-3.7*smooth(0,2.5,dst)+4.35*f,f)
long_slots=[((455,44),(910,44),12),((590,155),(590,362),11),((189,341),(189,416),8),((188,444),(188,528),8),((187,554),(187,638),8),((508,194),(508,351),7),((516,386),(516,455),7),((691,636),(691,674),6),((1008,634),(1008,696),6),((404,784),(702,784),5),((402,804),(702,804),4),((184,1009),(281,1009),4),((877,1008),(911,1008),8),((652,973),(791,973),4),((1167,1105),(1167,1195),9),((1190,1105),(1190,1195),9)]
for a,b,r in long_slots:
 dst=capsule(a,b,r);crest=smooth(1,5,dst)*.45;apply(dst,-2.7*smooth(0,2.5,dst)+crest,crest)
# Circular sockets read as recessed nozzle mouths. Central dark floor stays flat.
circles=[(x,y,23) for x,y in [(1029,749),(1108,749),(1186,749),(988,795),(1067,795),(1147,795),(1223,795),(1028,840),(1108,840),(1186,840)]]
circles += [(990,934,21),(1055,934,21),(989,993,21),(1054,993,21)]
circles += [(x,844,12) for x in [416,470,524,579,631,686]]
circles += [(432,y,12) for y in [180,231,285,340,396]]
circles += [(485,y,7) for y in [197,228,259,290,321]]
circles += [(x,930,7) for x in [649,678,707,735,763,792]]
circles += [(120,109,11),(272,250,15),(229,249,7),(491,743,12),(1200,44,26)]
for cx,cy,r in circles:
 rr=np.sqrt((X-cx)**2+(Y-cy)**2);dst=r+3-rr;rim=(1-smooth(1,3,np.abs(rr-r)))*.65;apply(dst,-4.1*(1-smooth(r-3,r,rr))+rim,rim)
# Rounded housings and cooling tubes; their shape is deliberately not extracted from lighting.
for a,b,r in [((104,744),(104,831),14),((200,746),(200,831),14),((398,497),(398,541),9),((426,497),(426,541),9),((1194,921),(1194,929),14),((1148,985),(1148,990),15),((1212,985),(1212,990),15)]:
 dst=capsule(a,b,r);f=smooth(0,r,dst);apply(dst,1.8*f,f)
# Panel seams are bounded paths. Colour graphics do not contribute to this height data.
paths=[[(170,1),(170,86)],[(410,1),(410,88)],[(786,1),(786,89)],[(879,1),(879,91)],[(1057,1),(1057,88)],[(4,91),(1253,91)],[(155,96),(155,461)],[(80,91),(80,221)],[(83,136),(156,136)],[(305,96),(305,323)],[(305,323),(157,323)],[(313,102),(414,102),(464,143)],[(472,94),(472,455)],[(548,94),(548,390)],[(626,92),(626,449)],[(708,96),(708,273)],[(785,95),(785,576)],[(863,95),(863,576)],[(941,96),(941,715)],[(1018,95),(1018,580)],[(1097,217),(1097,713)],[(1175,96),(1175,714)],[(629,255),(709,255)],[(706,201),(1016,201)],[(788,273),(1018,273)],[(866,414),(939,414)],[(786,575),(1097,575)],[(624,450),(707,450)],[(629,568),(861,568)],[(549,459),(624,459)],[(470,465),(547,465)],[(547,529),(622,529)],[(628,596),(706,596)],[(469,577),(545,577)],[(312,654),(463,654)],[(160,654),(310,654)],[(3,715),(1253,715)],[(317,718),(317,858)],[(81,720),(81,857)],[(2,777),(81,777)],[(524,716),(524,767)],[(383,770),(718,770)],[(722,722),(722,870)],[(794,722),(794,870)],[(876,722),(876,1037)],[(940,716),(940,1042)],[(0,863),(790,863)],[(4,868),(4,995)],[(84,866),(84,993)],[(219,869),(219,995)],[(318,863),(318,1030)],[(409,883),(409,1253)],[(608,885),(608,1253)],[(627,895),(810,895)],[(629,990),(810,990)],[(946,1043),(946,1253)],[(0,1030),(714,1030)],[(3,1060),(97,1060)],[(3,1141),(491,1141)],[(93,1060),(93,1254)],[(266,1031),(266,1253)],[(493,1047),(493,1253)],[(580,1044),(580,1254)],[(100,1206),(263,1206)],[(715,1055),(945,1055)]]
for path in paths:
 for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.2,capsule(a,b,1.5)))
# Flat stencils and insignia remain unchanged paint, including legacy hazard colours.
flatboxes=[(179,3,401,83),(711,296,739,556),(630,290,701,414),(479,472,542,536),(1024,221,1092,266),(1180,580,1243,616),(719,1040,939,1050),(860,1072,915,1100),(862,1217,914,1237),(498,1145,569,1231),(1041,1093,1081,1192),(949,1235,1253,1253)]
for q in flatboxes:flat=np.maximum(flat,smooth(0,1,box(*q)))
pan*=1-structure;pan*=1-flat;h-=2.3*pan;h*=1-flat
im=bpy.data.images.load(str(M/'ordnance_basecolor_generated_v1.png'));im.colorspace_settings.name='Non-Color';assert list(im.size)==[N,N];a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);rgb=a.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
lum=rgb.mean(-1);sat=(rgb.max(-1)-rgb.min(-1))/(rgb.max(-1)+1e-7);paint=smooth(.12,.30,sat);metal=.86*(1-paint)*smooth(.10,.42,lum);metal=metal*(1-structure)+(.12+.78*fins)*structure;metal*=1-flat;metal=metal*(1-pan)+.03*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.15,np.abs(lum-local));rough=np.clip(.73-.26*metal+.05*wear,.38,.85);rough=rough*(1-structure)+(.83-.41*fins)*structure;rough=rough*(1-pan)+.84*pan;rough=rough*(1-flat)+.72*flat
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
records={}
def save(a,key,colorspace='Non-Color'):
 buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Ordnance '+key,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  pixels=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(pixels);pixels=pixels.reshape(OUT,OUT,4);vectors=pixels[:,:,:3]*2-1;vectors/=np.linalg.norm(vectors,axis=-1,keepdims=True);pixels[:,:,:3]=vectors*.5+.5;im.pixels.foreach_set(pixels.ravel())
 p=M/('ordnance_'+key+'_2k_v1.png');im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};return p
for key,a in [('basecolor',rgb),('normal',normal*.5+.5),('roughness',rough),('metallic',metal),('orm',np.stack((np.ones_like(h),rough,metal),-1)),('height',(h+8)/16),('structure',structure),('fins',fins),('panels',pan),('paint',paint),('flat_graphics',flat)]:save(a,key)
(W/'material_regions.json').write_text(json.dumps(dict(vent_boxes=vent_boxes,long_slots=long_slots,sockets=circles,panel_paths=paths,flat_graphics=flatboxes,coordinate_size=N),indent=2))
(W/'material_validation.json').write_text(json.dumps(dict(maps=records,dimensions=[OUT,OUT],generated_colour_dimensions=[N,N],structural_height_only=True,flat_print_height_max=float(np.max(np.abs(h[flat>.999]))),normal_y='OpenGL tangent +Y, same as engine',ao='white, no baked cavity AO',emissives='deferred',paint_roughness=float(np.median(rough[(paint>.9)&(structure<.01)])),steel_roughness=float(np.median(rough[(metal>.7)&(structure<.01)]))),indent=2));print('ORDNANCE_MATERIALS_COMPLETE',flush=True)
