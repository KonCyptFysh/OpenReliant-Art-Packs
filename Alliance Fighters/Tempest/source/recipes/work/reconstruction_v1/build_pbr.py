import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path('authoring://Tempest/worn');W=D/'work/reconstruction_v1';M=D/'maps';bpy.ops.wm.open_mainfile(filepath=str(D/'tempest_worn_texture_v1.blend'));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];base=obs[0].active_material.node_tree.nodes['Base colour'].image
def signature():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest()
bpy.context.view_layer.update();original_signature=signature();N=4096;S=1254/N;yy,xx=np.mgrid[:N,:N].astype(np.float32);X=(xx+.5)*S;Y=(yy+.5)*S;del xx,yy
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
 im=bpy.data.images.new('Tempest v1 '+kind,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());im.filepath_raw=str(M/f'tempest_worn_{kind}_4k_v1.png');im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();im.pack();records[kind]={'path':im.filepath_raw,'sha256':hashlib.sha256(Path(im.filepath_raw).read_bytes()).hexdigest()};return im
h=np.zeros_like(X);glass=np.zeros_like(X);sign=np.zeros_like(X);structure=np.zeros_like(X);finmask=np.zeros_like(X)
glass_polys=[[(251,91),(257,84),(451,84),(458,91),(458,145),(451,151),(251,151)],[(496,89),(622,89),(632,97),(631,107),(496,139)],[(644,389),(669,389),(669,778),(644,778)]]
for p in glass_polys:
 sl,d=roi(p,3,lambda:poly(p));glass[sl]=np.maximum(glass[sl],smooth(-1,1,d))
# Flat printed safety graphics. The surrounding physical frames remain structural.
boxes=[(58,191,138,232),(45,583,94,659),(720,146,738,213),(737,659,755,714),(916,792,948,859),(516,1136,577,1178),(343,581,387,637)]
triangles=[[(257,207),(287,207),(272,189)],[(345,207),(377,207),(361,189)],[(1060,71),(1090,71),(1074,52)],[(708,360),(740,360),(723,379)],[(51,718),(88,718),(71,699)],[(730,754),(761,754),(745,736)],[(349,1096),(390,1096),(371,1077)]]
for p in [[(a,b),(c,b),(c,d),(a,d)] for a,b,c,d in boxes]+triangles:
 sl,d=roi(p,2,lambda:poly(p));sign[sl]=np.maximum(sign[sl],smooth(-.5,.8,d))
sl,d=roi([(308,436)],85,lambda:85-np.sqrt((X-308)**2+(Y-436)**2));sign[sl]=np.maximum(sign[sl],smooth(0,1,d))
features=[]
def vent(a,b,r,rails=0,depth=3.3):
 def calc():
  d=capsule(a,b,r);inside=smooth(0,2,d);v=np.array(b)-a;v=v/np.linalg.norm(v);cross=-(X-a[0])*v[1]+(Y-a[1])*v[0];pitch=2*r/(rails+1);z=-depth*inside;f=np.zeros_like(X)
  for i in range(rails):f=np.maximum(f,1-smooth(pitch*.12,pitch*.38,np.abs(cross-(i-(rails-1)/2)*pitch)))
  f*=smooth(1.5,4,d);z+=(depth+.4)*f;return z,smooth(-1,0,d),f
 sl,(z,mask,f)=roi([a,b],r+3,calc);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask);finmask[sl]=np.maximum(finmask[sl],f);features.append({'a':a,'b':b,'radius':r,'rails':rails,'depth':depth})
for a,b,r,k in [((820,230),(820,531),10,1),((922,132),(922,213),17,2),((1012,706),(1012,978),13,3),((343,1037),(632,1037),12,1),((489,1096),(638,1096),12,1),((173,602),(173,642),11,1),((237,601),(237,642),11,1),((299,602),(299,642),11,1)]:vent(a,b,r,k)
# Seven continuous fins in each half of the wing radiator. Matching centres preserve alignment.
banks=[{'polygon':[(309,902),(422,902),(422,944),(273,944)],'axis':1,'centres':[905,911,916,922,928,933,939],'half_width':2.0}, {'polygon':[(438,902),(663,902),(669,910),(669,938),(663,944),(438,944)],'axis':1,'centres':[905,911,916,922,928,933,939],'half_width':2.0}, {'polygon':[(1143,32),(1229,32),(1237,39),(1237,79),(1229,89),(1143,89),(1135,79),(1135,39)],'axis':1,'centres':[38,57,77],'half_width':5}]
for bank in banks:
 p=bank['polygon']
 def calc():
  d=poly(p);u=X if bank['axis']==0 else Y;f=np.zeros_like(X)
  for centre in bank['centres']:
   q=np.clip(np.abs(u-centre)/bank['half_width'],0,1);f=np.maximum(f,np.cos(q*np.pi/2)**2)
  f*=smooth(.4,2.2,d);return -3.3*smooth(0,1.8,d)+3.8*f,smooth(-1,0,d),f
 sl,(z,mask,f)=roi(p,3,calc);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask);finmask[sl]=np.maximum(finmask[sl],f)
# Circular recessed fittings, their rims and straight centre ribs.
sockets=[(112,456,37,1),(543,374,23,1),(543,502,23,1),(1166,269,36,1),(44,1037,19,0)]
for cx,cy,r,rails in sockets:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);inside=smooth(0,2,r-rr);z=-2.8*inside;rim=(1-smooth(1,3,np.abs(rr-(r-4))))*inside;bar=(1-smooth(1.5,4,np.abs(X-cx)))*smooth(4,7,r-rr) if rails else (1-smooth(1.5,4,np.abs(Y-cy)))*smooth(4,7,r-rr);return z+3.1*np.maximum(rim,bar),inside,np.maximum(rim,bar)
 sl,(z,mask,f)=roi([(cx,cy)],r+3,calc);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask);finmask[sl]=np.maximum(finmask[sl],f)
# Mechanical fan faces have radial fins rather than texture-noise pits.
fans=[(1149,538,28,32),(1149,609,29,32),(1167,820,25,16),(1163,958,32,4)]
for cx,cy,r,count in fans:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);a=np.arctan2(Y-cy,X-cx);mask=smooth(0,2,r-rr);ann=smooth(r*.3,r*.45,rr)*(1-smooth(r*.86,r,rr));rib=(.5+.5*np.cos(a*count))**3;z=(-1.3+.65*rib*ann)*mask+.9*(1-smooth(r*.17,r*.28,rr));return z,mask,rib*ann
 sl,(z,mask,f)=roi([(cx,cy)],r+3,calc);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask);finmask[sl]=np.maximum(finmask[sl],f)
# Cross grille near the lower-left atlas corner; smooth ribs over a single dark recess.
p=[(333,1160),(397,1160),(420,1183),(420,1210),(397,1226),(333,1226),(314,1207),(314,1185)]
def cross_grille():
 d=poly(p);mask=smooth(0,2,d);ribs=np.maximum.reduce([1-smooth(2,4,np.abs(X-352)),1-smooth(2,4,np.abs(X-383)),1-smooth(2,4,np.abs(Y-1190))])*smooth(1,4,d);return -3*mask+3.8*ribs,mask,ribs
sl,(z,mask,f)=roi(p,3,cross_grille);h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask);finmask[sl]=np.maximum(finmask[sl],f)
lines=[((233,20),(681,20)),((28,35),(28,238)),((233,30),(233,239)),((31,165),(639,165)),((407,165),(407,239)),((31,239),(638,239)),((431,240),(431,283)),((0,286),(638,286)),((28,410),(130,302)),((28,416),(28,549)),((137,286),(137,301)),((138,303),(375,303)),((187,307),(187,552)),((378,304),(411,339)),((411,339),(411,551)),((0,554),(411,554)),((25,562),(25,876)),((114,563),(114,908)),((34,660),(110,660)),((28,733),(111,733)),((28,749),(111,749)),((143,714),(156,699)),((157,699),(230,699)),((230,699),(246,715)),((246,715),(246,758)),((246,764),(140,875)),((140,765),(242,765)),((142,718),(142,866)),((121,916),(414,653)),((412,651),(412,557)),((0,981),(125,981)),((68,919),(68,981)),((112,918),(149,946)),((110,1092),(339,869)),((0,1191),(66,1191)),((67,1183),(116,1231)),((116,1231),(678,1231)),((341,766),(341,837)),((342,841),(682,841)),((430,848),(430,1110)),((284,995),(284,1071)),((236,962),(237,1033)),((289,966),(674,966)),((682,875),(682,1117)),((439,1111),(670,1111)),((469,1113),(469,1213)),((492,1228),(564,1228)),((1028,112),(1254,112)),((1028,168),(1254,168)),((1070,188),(1070,357)),((1093,188),(1093,357)),((1072,249),(1127,249)),((1095,360),(1245,360)),((1008,288),(1008,488)),((1008,488),(1123,488)),((1228,414),(1228,470)),((1228,477),(1254,477)),((857,625),(1092,625)),((1094,625),(1126,662)),((1126,662),(1229,662)),((1229,662),(1229,702)),((863,792),(899,792)),((783,756),(900,756)),((759,849),(810,849)),((810,590),(810,928)),((810,928),(832,946)),((832,946),(872,946)),((760,937),(801,977)),((688,970),(758,970)),((755,978),(755,1117)),((794,1097),(1254,1097)),((879,1103),(879,1229)),((767,1145),(1254,1145)),((768,1188),(1254,1188)),((1011,1016),(1254,1016)),((1143,1060),(1254,1060))]
for a,b in lines:
 sl,d=roi([a,b],4,lambda:capsule(a,b,1.6));allow=(1-structure[sl])*(1-glass[sl]);h[sl]+=-2.6*smooth(0,1.25,d)*allow
for cx,cy,r in [(450,214,12),(934,686,13),(934,739,12)]:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2)/r;return np.sqrt(np.maximum(0,1-rr**2))*.8*(1-smooth(.85,1,rr))
 sl,z=roi([(cx,cy)],r+2,calc);h[sl]+=z
h*=1-glass;h*=1-sign;dy,dx=np.gradient(h,S);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal_im=save(normal*.5+.5,'normal');save((h+5)/8,'height');save(glass,'glass');save(sign,'flat_graphics');save(structure,'structure_mask');save(finmask,'fin_mask');del normal,dx,dy
# Muted blue-grey paint remains dielectric. Neutral exposed steel gets a graded metal response.
im=bpy.data.images.load(str(M/'tempest_worn_basecolor_4k_v1.png'));im.colorspace_settings.name='Non-Color';a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);rgb=a.reshape(N,N,4)[::-1,:,:3];mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6)
metal=(1-smooth(.08,.25,sat))*smooth(.25,.62,lum)*.88;metal=metal*(1-structure)+(.18+.6*finmask)*structure;metal*=1-np.maximum(glass,sign)
local=(np.roll(lum,5,0)+np.roll(lum,-5,0)+np.roll(lum,5,1)+np.roll(lum,-5,1))*.25;wear=smooth(.007,.07,np.abs(lum-local));variation=np.sin(X*.063)*np.sin(Y*.053)
rough=np.clip(.82*(1-metal)+.48*metal+.045*variation+.1*wear,.43,.95);rough=rough*(1-structure)+(.58-.1*finmask+.02*variation)*structure;rough=rough*(1-sign)+.8*sign;rough=rough*(1-glass)+(.245+.065*wear)*glass;spec=.30*(1-glass)+.46*glass
mi=save(metal,'metallic');ri=save(rough,'roughness');spi=save(spec,'specular');co=save(glass*.12,'coat');stats={'glass_roughness_median':float(np.median(rough[glass>.99])),'glass_metallic_max':float(metal[glass>.9999].max()),'paint_roughness_median':float(np.median(rough[(metal<.1)&(glass<.1)&(structure<.1)]))}
mat=bpy.data.materials.new('Tempest_Worn_PBR_v1');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();uv=n.new('ShaderNodeUVMap');uv.name='Atlas UV';uv.uv_map='Tempest_Atlas_UV_v1';bs=n.new('ShaderNodeBsdfPrincipled');bs.name='Worn physical surface';bs.inputs['IOR'].default_value=1.46;out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0])
for name,image,socket in [('basecolor',base,'Base Color'),('metallic',mi,'Metallic'),('roughness',ri,'Roughness'),('specular',spi,'Specular IOR Level'),('coat',co,'Coat Weight'),('normal',normal_im,'Normal')]:
 q=n.new('ShaderNodeTexImage');q.name='Delivered '+name;q.image=image;l.new(uv.outputs[0],q.inputs[0])
 if name=='normal':
  nm=n.new('ShaderNodeNormalMap');nm.uv_map=uv.uv_map;nm.inputs['Strength'].default_value=1;l.new(q.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs[socket])
 else:l.new(q.outputs[0],bs.inputs[socket])
hidden_mat=bpy.data.materials['Native caps hidden on intact ship']
for o in obs:
 hidden=list(o['native_hidden_faces']);o.data.materials.clear();o.data.materials.append(mat);o.data.materials.append(hidden_mat)
 for idx in hidden:o.data.polygons[idx].material_index=1
assert signature()==original_signature
s['pbr_status']='Tempest first worn review: native seven-part geometry, structural-only normals, smoked glass and flat markings.';s.cycles.samples=24;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'tempest_worn_pbr_v1.blend'));records['basecolor']={'path':str(M/'tempest_worn_basecolor_4k_v1.png'),'sha256':hashlib.sha256((M/'tempest_worn_basecolor_4k_v1.png').read_bytes()).hexdigest()}
(W/'validation.json').write_text(json.dumps({'geometry_uv_native_normals_preserved':True,'geometry_signature':original_signature,'maps':records,'material_statistics':stats,'parts':len(obs),'stored_LOD0_triangles':700,'intact_visible_LOD0_triangles':608,'native_hidden_caps_and_wires_retained_but_transparent':True,'glass_regions':len(glass_polys),'engine_validation':'not_tested'},indent=2));(W/'regions.json').write_text(json.dumps({'glass':glass_polys,'vents':features,'radiators':banks,'sockets':sockets,'fans':fans,'panel_lines':lines,'flat_boxes':boxes,'flat_triangles':triangles,'coordinate_system':'1254-square, top-down'},indent=2));print('PBR_COMPLETE',flush=True)
