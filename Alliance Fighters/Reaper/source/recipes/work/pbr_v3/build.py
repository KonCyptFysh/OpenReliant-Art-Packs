import bpy,numpy as np,json,hashlib,ast,re
from pathlib import Path
D=Path('authoring://Reaper/worn');W=D/'work/pbr_v3';M=D/'maps/pbr_v3'
bpy.ops.wm.open_mainfile(filepath=str(D/'reaper_worn_pbr_v2.blend'));s=bpy.context.scene;objects=[o for o in s.objects if o.type=='MESH']
def sig():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in objects},sort_keys=True).encode()).hexdigest()
before=sig();mat=objects[0].material_slots[0].material;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Worn physical surface'];uv=n['Original layout UV'];N=4096;S=1600/N;yy,xx=np.mgrid[:N,:N].astype(np.float32);X=(xx+.5)*S;Y=(yy+.5)*S;del xx,yy
# Explicit semantic masks, independent of brightness/weathering.
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def poly(points):
 pts=np.array(points);d=np.full(X.shape,1e6,np.float32);area=np.sum(pts[:,0]*np.roll(pts[:,1],-1)-pts[:,1]*np.roll(pts[:,0],-1))
 for a,b in zip(pts,np.roll(pts,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
def capsule(a,b,r):
 a=np.array(a);v=np.array(b)-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);return r-np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
def load(path):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);return a.reshape(N,N,4)[::-1].copy()
records={}
def save(data,kind):
 a=np.ones((N,N,4),np.float32);a[:,:,:3]=data[:,:,None] if data.ndim==2 else data
 im=bpy.data.images.new('Reaper v3 '+kind,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());im.filepath_raw=str(M/f'reaper_{kind}_4k_v3.png');im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();im.pack();records[kind]={'path':im.filepath_raw,'sha256':hashlib.sha256(Path(im.filepath_raw).read_bytes()).hexdigest()};return im
def tex(im,name):
 q=n.new('ShaderNodeTexImage');q.name=q.label=name;q.image=im;l.new(uv.outputs[0],q.inputs[0]);return q
text=(D/'work/glass_touchup_v1/build.py').read_text();front=np.array([]);polys=ast.literal_eval(re.search(r'polys=(\[.*\])',text).group(1));polys=[(np.array(p)*1600/1254).tolist() for p in polys]
polys += [[(642,704),(742,704),(742,746),(733,754),(652,754),(642,743)],[(782,704),(983,704),(983,745),(973,754),(794,754),(782,744)],[(1018,704),(1068,704),(1068,742),(1061,749),(1025,749),(1018,741)]]
d=np.full(X.shape,-1e6,np.float32)
for p in polys:d=np.maximum(d,poly(p))
glass=smooth(-3,-1,d);colour_mask=smooth(-1,2,d);seal=smooth(-9,-6,d)*(1-glass)
# Restrict the imagegen edit strictly to existing pane interiors in the shader.
g=tex(save(glass,'glass'),'Continuous pane mask v3');repair=tex(save(colour_mask,'glass_colour_mask'),'Glass repair blend v3');oldcolour=bs.inputs['Base Color'].links[0].from_socket;gen=bpy.data.images.load(str(W/'glass_repair_imagegen.png'));gen.colorspace_settings.name='sRGB';gen.pack();gt=tex(gen,'Imagegen glass repair only');mix=n.new('ShaderNodeMixRGB');mix.name='Repaired glass only - original frames preserved';l.new(repair.outputs[0],mix.inputs[0]);l.new(oldcolour,mix.inputs[1]);l.new(gt.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
# Explicit manufactured recesses/ribs. Scratch luminance never drives this height.
h=np.zeros(X.shape,np.float32);structure=np.zeros_like(h);sign=np.zeros_like(h)
features=[]
def apply_roi(points,pad,func):
 global X,Y
 fullX,fullY=X,Y;pts=np.array(points);lo=np.maximum(0,np.floor((pts.min(0)-pad)/S).astype(int));hi=np.minimum(N,np.ceil((pts.max(0)+pad)/S).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];X=fullX[sl];Y=fullY[sl];out=func();X,Y=fullX,fullY;return sl,out
def vent(a,b,r,rails=1,depth=4):
 def calc():
  dd=capsule(a,b,r);inside=smooth(0,3,dd);v=np.array(b)-a;v=v/np.linalg.norm(v);cross=-(X-a[0])*v[1]+(Y-a[1])*v[0];pitch=2*r/(rails+1);hh=-depth*inside
  for i in range(rails):hh+=(depth+1)*(1-smooth(pitch*.16,pitch*.34,np.abs(cross-(i-(rails-1)/2)*pitch)))*smooth(3,6,dd)
  return hh,smooth(-2,0,dd)
 sl,(hh,mm)=apply_roi([a,b],r+4,calc);h[sl]=h[sl]*(1-mm)+hh*mm;structure[sl]=np.maximum(structure[sl],mm);features.append({'type':'vent','a':a,'b':b,'radius':r,'rails':rails})
for a,b,r,rails in [((752,74),(970,74),16,1),((746,463),(999,463),21,1),((1224,611),(1463,611),21,1),((837,854),(1072,854),20,1),((878,930),(1070,930),19,1),((405,565),(497,565),20,1),((402,648),(496,648),19,1),((945,1235),(1238,1235),45,3),((1040,1463),(1310,1463),29,2),((462,855),(462,930),13,0),((298,1358),(298,1399),12,0),((385,1358),(385,1399),12,0),((472,1358),(472,1399),12,0)]:vent(a,b,r,rails)
# The large vertical bank and smaller engine radiator have continuous fin surfaces.
for box,axis,start,period,count,width in [((638,1038,736,1450),0,653,24,4,7),((249,514,314,613),1,526,24,4,7),((938,1547,1077,1599),1,1554,10,5,2.5)]:
 x0,y0,x1,y1=box
 def calc():
  dd=poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)]);u=X if axis==0 else Y;fin=np.zeros_like(X)
  for i in range(count):fin=np.maximum(fin,1-smooth(width*.6,width,np.abs(u-start-i*period)))
  return (-5+6*fin)*smooth(0,3,dd),smooth(-2,0,dd)
 sl,(hh,mm)=apply_roi([(x0,y0),(x1,y1)],4,calc);h[sl]=h[sl]*(1-mm)+hh*mm;structure[sl]=np.maximum(structure[sl],mm)
# Square nose ports remain recessed, not luminance-derived pits.
for cy in [337,368,400,431]:
 for cx in [251,281,312]:vent((cx,cy-4),(cx,cy+4),8,0,3)
# Major connected panel gaps, following actual atlas boundaries.
lines=[((681,0),(681,700)),((1015,0),(1015,699)),((1119,130),(1119,1073)),((1221,0),(1221,391)),((1347,703),(1347,1600)),((590,132),(590,700)),((194,0),(194,211)),((562,308),(562,798)),((324,310),(324,798)),((21,651),(21,1088)),((106,756),(106,1300)),((289,800),(289,1301)),((403,802),(403,1183)),((559,800),(559,1599)),((180,1085),(180,1599)),((753,1073),(753,1180)),((1015,994),(1015,1180)),((1227,1076),(1227,1180)),((1392,929),(1392,1018)),((1478,1021),(1478,1320)),((680,130),(1577,130)),((682,202),(1545,202)),((683,258),(1120,258)),((684,334),(1011,334)),((687,393),(1569,393)),((686,417),(1008,417)),((684,519),(1569,519)),((685,548),(1119,548)),((561,699),(1599,699)),((324,437),(558,437)),((321,484),(558,484)),((21,800),(560,800)),((105,969),(560,969)),((293,1183),(560,1183)),((181,1303),(559,1303)),((561,805),(1120,805)),((562,995),(1347,995)),((756,1072),(1478,1072)),((1350,859),(1599,859)),((1350,928),(1599,928)),((1121,1020),(1599,1020)),((750,1289),(1391,1289)),((750,1347),(1387,1347)),((923,1407),(1375,1407)),((927,1526),(1390,1526))]
for a,b in lines:
 sl,dd=apply_roi([a,b],5,lambda:capsule(a,b,2.5));mm=smooth(-1,0,dd);hh=-2.4*smooth(0,1.7,dd);allow=(1-structure[sl])*(1-glass[sl]);h[sl]+=hh*allow;structure[sl]=np.maximum(structure[sl],mm*allow)
# Paint-only warning labels and hazard stripes: neutral normals and dielectric response.
boxes=[(211,136,301,166),(421,337,526,405),(437,471,529,502),(438,1027,489,1129),(1112,271,1210,301),(1130,208,1536,239),(1130,545,1551,568),(1127,666,1552,691),(22,228,180,248),(697,18,1007,34),(697,114,1008,133),(702,562,985,573),(700,654,980,672),(697,574,710,650),(984,574,999,650),(47,820,82,920),(121,446,171,540)]
triangles=[[(943,160),(980,160),(960,183)],[(1032,17),(1060,17),(1046,41)],[(1032,114),(1060,114),(1046,95)],[(369,359),(396,381),(369,410)],[(1357,268),(1376,286),(1357,302)],[(1041,466),(1094,466),(1068,494)],[(1200,446),(1216,461),(1200,477)],[(1496,446),(1512,433),(1512,477)],[(1389,883),(1421,883),(1406,907)],[(1461,883),(1495,883),(1478,907)],[(1425,1084),(1456,1106),(1425,1136)],[(1425,1184),(1456,1206),(1425,1236)],[(127,1140),(150,1120),(150,1164)],[(127,1241),(150,1222),(150,1264)]]
for p in [[(a,b),(c,b),(c,d),(a,d)] for a,b,c,d in boxes]+triangles:
 sl,dd=apply_roi(p,3,lambda:poly(p));sign[sl]=np.maximum(sign[sl],smooth(-1,0,dd))
h*=1-np.maximum(glass,sign);dy,dx=np.gradient(h,S);v=np.stack((-dx,dy,np.ones_like(dx)),-1);v/=np.linalg.norm(v,axis=-1,keepdims=True)
old=load(D/'maps/pbr_v2/reaper_normal_4k_v2.png')[:,:,:3]*2-1
# Preserve faint surface wear; never let it overwhelm structural levels or glass.
micro=.065*(1-structure)*(1-np.maximum(glass,sign));v[:,:,:2]+=old[:,:,:2]*micro[:,:,None];v/=np.linalg.norm(v,axis=-1,keepdims=True);v=v*(1-np.maximum(glass,sign)[:,:,None])+np.array([0,0,1])*np.maximum(glass,sign)[:,:,None]
normal=save(v*.5+.5,'normal');save((h+8)/12,'height');save(structure,'structure_mask');save(sign,'paint_graphics_mask');save(seal,'seal_mask');del old,v,h,dx,dy
# Use explicit domains over the existing approved paint/metal wear maps.
paint=np.zeros_like(glass)
paint_polys=[[(1228,136),(1540,136),(1540,195),(1228,195)],[(1230,259),(1550,259),(1550,386),(1230,386)],[(1023,398),(1560,398),(1560,517),(1023,517)],[(1128,574),(1558,574),(1558,660),(1128,660)],[(770,809),(1114,809),(1114,985),(817,985)],[(1133,735),(1340,735),(1340,1067),(1133,1067)],[(1311,1080),(1468,1080),(1468,1314),(1400,1368),(1326,1329)]]
for pp in paint_polys:
 sl,dd=apply_roi(pp,2,lambda:poly(pp));paint[sl]=np.maximum(paint[sl],smooth(0,2,dd))
raw=np.empty(N*N*4,np.float32);n['Base colour'].image.pixels.foreach_get(raw);rgb=raw.reshape(N,N,4)[::-1,:,:3];mx=rgb.max(-1);mn=rgb.min(-1);sat=(mx-mn)/(mx+1e-6);chips=(1-smooth(.09,.19,sat))*smooth(.25,.46,mx);save(paint,'paint_domain_mask');del raw,rgb,mx,mn,sat
statistics={}
for kind,socket in [('metallic','Metallic'),('roughness','Roughness'),('specular','Specular IOR Level'),('coat','Coat Weight')]:
 a=load(D/f'maps/pbr_v2/reaper_{kind}_4k_v2.png')[:,:,0]
 if kind=='metallic':a=a*(1-paint)+chips*.86*paint;a=a*(1-structure)+.72*structure;a=a*(1-sign);a=a*(1-glass-seal)
 elif kind=='roughness':a=np.clip(a,.38,.92);a=a*(1-paint)+(.8-chips*.27)*paint;a=a*(1-structure)+(.50+.06*np.sin(X*.028)*np.sin(Y*.033))*structure;a=a*(1-sign)+.78*sign;a=a*(1-glass-seal)+(.28+.035*(.5+.5*np.sin(X*.035)*np.sin(Y*.045)))*glass+.62*seal
 elif kind=='specular':a=a*(1-glass-seal)+.45*glass+.27*seal
 else:a=.10*glass
 im=save(a,kind);tx=tex(im,'Delivered v3 '+kind);l.new(tx.outputs[0],bs.inputs[socket]);statistics[kind]={'glass_median':float(np.median(a[glass>.99])),'sign_median':float(np.median(a[sign>.99]))}
tx=tex(normal,'Delivered v3 normal');nm=n.new('ShaderNodeNormalMap');nm.name='Clean structural normal v3';nm.uv_map=uv.uv_map;nm.inputs['Strength'].default_value=1;l.new(tx.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
mat.name='Reaper_Worn_PBR_v3_AtlasDomains'
audit=[]
for o in objects:
 assert o.data.uv_layers.get(uv.uv_map)
 for p in o.data.polygons:assert p.material_index<len(o.material_slots) and o.material_slots[p.material_index].material==mat
 audit.append({'part':o.name,'faces':len(o.data.polygons),'material':mat.name,'uv':uv.uv_map})
assert sig()==before
s['pbr_status']='v3 repaired glass interiors; continuous semantic masks; authored panel recesses and radiator fins; paint-only warning graphics. Engine not tested.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'reaper_worn_pbr_v3.blend'))
(W/'validation.json').write_text(json.dumps({'source_scene':str(D/'reaper_worn_pbr_v2.blend'),'geometry_uv_normals_transforms_signature':before,'geometry_uv_normals_transforms_unchanged':True,'material_assignments':audit,'material_statistics':statistics,'maps':records,'glass_panes':len(polys),'engine_validation':'not_tested','basecolour_edit':'imagegen repair blended only inside continuous pane masks; original frame artwork preserved'},indent=2));(W/'regions.json').write_text(json.dumps({'glass':polys,'vents':features,'panel_lines':lines,'sign_boxes':boxes,'sign_triangles':triangles},indent=2));print('BUILD_DONE',flush=True)
