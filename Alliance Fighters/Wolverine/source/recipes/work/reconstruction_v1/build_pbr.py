import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path('authoring://Wolverine/worn');W=D/'work/reconstruction_v1';M=D/'maps';bpy.ops.wm.open_mainfile(filepath=str(D/'wolverine_worn_texture_v1.blend'));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];base=obs[0].active_material.node_tree.nodes['Base colour'].image
def signature():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest()
bpy.context.view_layer.update();original_signature=signature()
N=4096;S=1254/N;yy,xx=np.mgrid[:N,:N].astype(np.float32);X=(xx+.5)*S;Y=(yy+.5)*S;del xx,yy

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def poly(points):
 p=np.array(points);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
def capsule(a,b,r):
 a=np.array(a);v=np.array(b)-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);return r-np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
def roi(points,pad,func):
 global X,Y
 ox,oy=X,Y;p=np.array(points);lo=np.maximum(0,np.floor((p.min(0)-pad)/S).astype(int));hi=np.minimum(N,np.ceil((p.max(0)+pad)/S).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];X=ox[sl];Y=oy[sl];v=func();X,Y=ox,oy;return sl,v
records={}
def save(data,kind):
 a=np.ones((N,N,4),np.float32);a[:,:,:3]=data[:,:,None] if data.ndim==2 else data
 im=bpy.data.images.new('Wolverine v1 '+kind,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());im.filepath_raw=str(M/f'wolverine_worn_{kind}_4k_v1.png');im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();im.pack();records[kind]={'path':im.filepath_raw,'sha256':hashlib.sha256(Path(im.filepath_raw).read_bytes()).hexdigest()};return im
h=np.zeros_like(X);glass=np.zeros_like(X);sign=np.zeros_like(X);structure=np.zeros_like(X)
# Explicit continuous glass domains, excluding original framing and seals.
glass_polys=[[(501,103),(526,103),(530,111),(530,152),(523,160),(501,160)],[(502,183),(545,183),(551,192),(551,257),(540,266),(502,256)],[(279,427),(306,408),(319,413),(299,446)],[(323,456),(338,415),(360,415),(376,456)],[(376,408),(414,428),(392,447)],[(409,663),(473,663),(483,674),(483,700),(473,710),(409,710),(404,704),(404,670)],[(510,666),(645,666),(651,673),(650,699),(641,704),(510,703),(505,696),(505,674)],[(699,666),(923,666),(928,674),(927,698),(922,703),(699,703)],[(502,780),(635,737),(643,741),(647,757),(642,763),(510,800),(501,796)],[(500,817),(646,794),(654,803),(655,831),(650,837),(503,834),(498,828)],[(17,908),(129,908),(135,915),(135,973),(128,980),(17,980),(13,974),(13,915)],[(211,1005),(289,970),(343,1007),(334,1027),(270,1056),(213,1022)],[(331,954),(420,931),(429,937),(434,973),(428,980),(370,999),(332,966)],[(169,1072),(211,1050),(233,1067),(225,1080),(185,1082)],[(73,1103),(102,1103),(109,1112),(109,1145),(102,1152),(73,1152)],[(71,1171),(95,1171),(130,1210),(130,1230),(117,1238),(71,1238)]]
for p in glass_polys:
 sl,d=roi(p,3,lambda:poly(p));glass[sl]=np.maximum(glass[sl],smooth(-1,1,d))
# Paint-only warning signs and insignia. Panel frames remain physical.
boxes=[(1155,251,1231,299),(792,336,813,377),(472,580,546,620),(1109,667,1123,718),(399,1025,463,1054),(680,22,757,44),(679,274,757,297),(170,438,249,513),(548,961,643,1079),(906,234,1016,342),(4,103,151,211),(1136,103,1254,207),(507,1097,752,1115)]
triangles=[[(685,0),(751,0),(718,28)],[(687,281),(748,281),(719,260)],[(862,195),(903,195),(884,175)],[(932,195),(972,195),(952,176)],[(576,591),(655,591),(619,625)],[(1030,668),(1056,692),(1030,716)],[(334,1039),(373,1039),(351,1063)],[(6,275),(26,251),(26,298)]]
for p in [[(a,b),(c,b),(c,d),(a,d)] for a,b,c,d in boxes]+triangles:
 sl,d=roi(p,2,lambda:poly(p));sign[sl]=np.maximum(sign[sl],smooth(-.5,.8,d))
# Rounded recesses, with explicit smooth continuous rail profiles.
features=[]
def vent(a,b,r,rails=0,depth=3.5):
 def calc():
  d=capsule(a,b,r);inside=smooth(0,2,d);v=np.array(b)-a;v=v/np.linalg.norm(v);cross=-(X-a[0])*v[1]+(Y-a[1])*v[0];pitch=2*r/(rails+1);z=-depth*inside
  for i in range(rails):z+=(depth+.6)*(1-smooth(pitch*.12,pitch*.37,np.abs(cross-(i-(rails-1)/2)*pitch)))*smooth(2,5,d)
  return z,smooth(-1,0,d)
 sl,(z,mask)=roi([a,b],r+3,calc);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask);features.append({'a':a,'b':b,'radius':r,'rails':rails})
for a,b,r,k in [((853,83),(973,83),17,1),((853,149),(973,149),17,1),((40,435),(99,435),22,2),((832,521),(1120,521),15,1),((755,601),(935,601),18,2),((846,974),(1160,974),14,2),((1074,1197),(1209,1197),19,3),((217,624),(217,819),12,1),((151,397),(151,414),10,0)]:vent(a,b,r,k)
# Radiator banks use rounded raised fins over deep constant channels; no colour-derived pitting.
banks=[([(214,61),(320,61),(326,71),(326,242),(317,250),(215,250),(207,241),(207,73)],0,220,20,6,5.5), ([(30,615),(154,518),(180,539),(180,869),(30,869)],0,42,21,7,6), ([(273,529),(376,603),(376,868),(273,868)],0,282,21,5,6), ([(1141,619),(1227,619),(1227,768),(1141,768)],0,1148,14,6,5), ([(185,326),(347,326),(357,335),(357,350),(186,350)],0,196,20,8,6), ([(841,1077),(997,1077),(1007,1088),(997,1108),(843,1108)],0,851,19,8,6), ([(188,391),(250,391),(250,428),(188,428)],1,399,10,3,3)]
for p,axis,start,pitch,count,width in banks:
 def calc():
  d=poly(p);u=X if axis==0 else Y;fin=np.zeros_like(X)
  for j in range(count):
   q=np.clip(np.abs(u-start-j*pitch)/width,0,1);fin=np.maximum(fin,np.cos(q*np.pi/2)**2)
  return (-4+5*fin)*smooth(0,2.5,d),smooth(-1,0,d)
 sl,(z,mask)=roi(p,3,calc);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask)
# Panel gaps following the original atlas. They can cross paint but never cross glass or fins.
lines=[((0,54),(153,54)),((57,62),(57,334)),((0,214),(149,214)),((0,331),(115,331)),((153,0),(153,296)),((193,0),(193,54)),((480,0),(480,388)),((544,0),(544,280)),((665,0),(665,326)),((763,0),(763,328)),((575,236),(663,236)),((575,326),(664,326)),((809,216),(1124,216)),((1024,63),(1024,235)),((1127,62),(1127,390)),((753,390),(753,642)),((601,390),(601,569)),((637,439),(1181,439)),((1183,392),(1183,567)),((635,527),(798,527)),((998,578),(998,934)),((1075,577),(1075,809)),((991,860),(1254,860)),((679,759),(997,759)),((677,859),(677,942)),((791,859),(791,1118)),((678,940),(1254,940)),((499,946),(499,1116)),((499,1089),(750,1089)),((686,1008),(1254,1008)),((790,1015),(790,1070)),((1056,834),(1254,834)),((678,1118),(678,1254)),((755,1118),(755,1254)),((267,1083),(497,1083)),((265,1083),(265,1254)),((117,1026),(117,1069)),((58,1010),(58,1091)),((4,1109),(56,1109)),((127,1090),(127,1151)),((529,861),(529,942)),((579,715),(579,742))]
for a,b in lines:
 sl,d=roi([a,b],5,lambda:capsule(a,b,2));allow=(1-structure[sl])*(1-glass[sl]);h[sl]+=-2.6*smooth(0,1.5,d)*allow
# Service domes and recessed sockets; no arbitrary scratches in height.
for cx,cy,r in [(616,95,20),(617,181,20),(1068,901,17),(1132,901,17),(1208,901,17),(83,1061,11)]:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2)/r;return np.sqrt(np.maximum(0,1-rr**2))*.9*(1-smooth(.85,1,rr))
 sl,z=roi([(cx,cy)],r+2,calc);h[sl]+=z
h*=1-glass;dy,dx=np.gradient(h,S);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal_im=save(normal*.5+.5,'normal');save((h+5)/8,'height');save(glass,'glass');save(sign,'flat_graphics');save(structure,'structure_mask');del normal,dx,dy
# Material domains are explicit for glass/labels, with pigment-based painted versus bare-metal areas.
im=bpy.data.images.load(str(D/'maps/wolverine_worn_basecolor_4k_v1.png'));im.colorspace_settings.name='Non-Color';a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);rgb=a.reshape(N,N,4)[::-1,:,:3];mx=rgb.max(-1);mn=rgb.min(-1);sat=(mx-mn)/(mx+1e-6);metal=(1-smooth(.13,.30,sat))*smooth(.09,.32,mx)*.88;metal*=1-np.maximum(glass,sign)
lum=rgb.mean(-1);local=(np.roll(lum,5,0)+np.roll(lum,-5,0)+np.roll(lum,5,1)+np.roll(lum,-5,1))*.25;wear=smooth(.005,.08,np.abs(lum-local));variation=np.sin(X*.077)*np.sin(Y*.063)
rough=np.clip(.82*(1-metal)+.51*metal+.055*variation+.11*wear,.43,.94);rough=rough*(1-structure)+(.52+.035*variation)*structure;rough=rough*(1-sign)+.8*sign;rough=rough*(1-glass)+(.28+.045*wear)*glass;spec=.30*(1-glass)+.46*glass
mi=save(metal,'metallic');ri=save(rough,'roughness');spi=save(spec,'specular');co=save(glass*.12,'coat');stats={'glass_roughness_median':float(np.median(rough[glass>.99])),'glass_metallic_max':float(metal[glass>.99].max()),'paint_roughness_median':float(np.median(rough[(metal<.1)&(glass<.1)&(structure<.1)]))}
mat=bpy.data.materials.new('Wolverine_Worn_PBR_v1');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();uv=n.new('ShaderNodeUVMap');uv.name='Atlas UV';uv.uv_map='Wolverine_Atlas_UV_v1';bs=n.new('ShaderNodeBsdfPrincipled');bs.name='Worn physical surface';bs.inputs['IOR'].default_value=1.46;out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0])
for name,image,socket in [('basecolor',base,'Base Color'),('metallic',mi,'Metallic'),('roughness',ri,'Roughness'),('specular',spi,'Specular IOR Level'),('coat',co,'Coat Weight'),('normal',normal_im,'Normal')]:
 q=n.new('ShaderNodeTexImage');q.name='Delivered '+name;q.image=image;l.new(uv.outputs[0],q.inputs[0])
 if name=='normal':
  nm=n.new('ShaderNodeNormalMap');nm.uv_map=uv.uv_map;nm.inputs['Strength'].default_value=1;l.new(q.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs[socket])
 else:l.new(q.outputs[0],bs.inputs[socket])
for o in obs:o.data.materials.clear();o.data.materials.append(mat)
sig=hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest();assert sig==original_signature
s['pbr_status']='First Wolverine worn PBR restoration; clean structure-only normals, continuous glass and flat markings; engine not yet tested.';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'wolverine_worn_pbr_v1.blend'));records['basecolor']={'path':str(D/'maps/wolverine_worn_basecolor_4k_v1.png'),'sha256':hashlib.sha256((D/'maps/wolverine_worn_basecolor_4k_v1.png').read_bytes()).hexdigest()}
(W/'validation.json').write_text(json.dumps({'geometry_uv_native_normals_preserved':True,'geometry_signature':sig,'maps':records,'material_statistics':stats,'parts':len(obs),'glass_regions':len(glass_polys),'engine_validation':'not_tested'},indent=2));(W/'regions.json').write_text(json.dumps({'glass':glass_polys,'vents':features,'radiators':banks,'panel_lines':lines,'flat_boxes':boxes,'flat_triangles':triangles},indent=2));print('PBR_COMPLETE',flush=True)
