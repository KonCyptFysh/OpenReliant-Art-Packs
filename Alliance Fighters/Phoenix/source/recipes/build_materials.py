import os
import bpy,numpy as np,json,hashlib,math
from pathlib import Path
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
src=D/'phoenix_source_review.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];source_sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.context.view_layer.update()
before={o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'n':[list(n.vector) for n in o.data.corner_normals],'uv':{u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers}} for o in obs}
# Repair the handful of collapsed original islands by reusing quiet matching material areas.
# These are material-only underside/tip walls; canopy, livery and broad faces keep their UVs.
repairs=[];newuv='Phoenix_Delivery_UV_v1'
for o in obs:
 m=o.data;u=m.uv_layers.new(name=newuv,do_init=True);m.uv_layers.active=u;u.active_render=True
 groups=[]
 if o.name=='Phoenix_Body':groups=[([238],(525,966,575,1025)),([309],(525,966,575,1025)),([241,242],(525,966,575,1025)),([312,313],(525,966,575,1025)),([357,358],(627,828,705,873)),([377,378],(627,828,705,873))]
 for ids,box in groups:
  vert_ids=sorted({v for i in ids for v in m.polygons[i].vertices});pts=np.array([list(o.matrix_world@m.vertices[i].co) for i in vert_ids]);mean=pts.mean(0);_,_,vh=np.linalg.svd(pts-mean);q=(pts-mean)@vh[:2].T;lo=q.min(0);hi=q.max(0);a,b,c,d=box;scale=min((c-a)/(hi[0]-lo[0]),(d-b)/(hi[1]-lo[1]));mapped=(q-(lo+hi)/2)*scale+np.array([(a+c)/2,(b+d)/2]);lookup={i:v for i,v in zip(vert_ids,mapped)}
  for i in ids:
   p=m.polygons[i]
   for k in p.loop_indices:
    x,y=lookup[m.loops[k].vertex_index];u.data[k].uv=(x/N,1-y/N)
  repairs.append({'part':o.name,'faces':ids,'reuse_box_atlas_pixels':box,'projection':'isotropic local plane; no new texture section'})
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);return r-np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
def poly(p):
 p=np.array(p);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
def roi(points,pad,fn):
 global X,Y
 ox,oy=X,Y;p=np.array(points);lo=np.maximum(0,np.floor(p.min(0)-pad).astype(int));hi=np.minimum(N,np.ceil(p.max(0)+pad).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];X=ox[sl];Y=oy[sl];result=fn();X,Y=ox,oy;return sl,result
glass_polys=[[(560,601),(688,601),(697,610),(693,622),(558,622),(553,614)],[(741,598),(892,598),(902,608),(898,625),(737,625),(729,615)],[(929,602),(1045,602),(1050,612),(1045,626),(928,626),(923,616)],[(1084,589),(1100,580),(1221,580),(1233,588),(1233,634),(1222,642),(1100,635),(1080,622)],[(589,721),(715,697),(722,700),(723,712),(592,741)],[(752,690),(893,669),(900,674),(899,693),(754,713),(745,708)],[(929,665),(1048,657),(1053,662),(1050,674),(929,686),(924,680)]]
flat_boxes=[(0,27,278,58),(362,8,450,320),(461,178,492,233),(552,153,576,234),(758,382,814,422),(995,339,1179,436),(1027,785,1246,902),(1219,158,1253,192),(1146,29,1253,60),(796,738,883,772),(908,801,969,871),(1013,730,1253,762),(127,795,151,1000),(158,914,198,970),(590,1055,713,1093),(147,372,232,519),(11,673,64,798),(752,1164,1181,1245)]
vents=[((0,81),(132,81),10,1,'long'),((0,110),(132,110),10,1,'long'),((1184,83),(1253,83),9,1,'long'),((1182,111),(1253,111),9,1,'long'),((1000,991),(1180,991),10,1,'long'),((260,778),(260,944),11,1,'long'),((309,710),(309,903),10,1,'long'),((103,859),(103,956),10,1,'long'),((0,1006),(120,1006),8,1,'long'),((0,1030),(120,1030),8,1,'long')]
panels=[[(0,153),(335,153)],[(170,298),(170,609)],[(170,374),(337,374),(337,159)],[(0,482),(253,482)],[(115,615),(252,615)],[(480,3),(538,62),(538,482)],[(510,328),(510,482)],[(589,0),(589,49)],[(0,1169),(308,1169)],[(17,1221),(396,1221)],[(213,815),(213,1169)],[(205,869),(255,869)],[(726,748),(726,1249)],[(728,983),(969,983)],[(728,1073),(969,1073)],[(832,984),(832,1073)],[(924,976),(924,1073)],[(789,722),(789,983)],[(515,808),(783,808)],[(581,810),(581,1120)],[(581,894),(784,894)],[(516,942),(780,942)],[(584,982),(725,982)],[(673,0),(673,286)],[(832,0),(832,114)],[(730,51),(1028,51)],[(973,197),(1253,197)],[(1054,201),(1054,291)],[(658,378),(738,378),(788,430),(877,430)],[(968,330),(1254,330)],[(968,762),(1253,762)],[(968,901),(1253,901)],[(978,1042),(1108,1042),(1108,1153)],[(1109,1066),(1253,1066)]]
reg={'glass':glass_polys,'flat_caution_and_insignia_boxes':flat_boxes,'vents':vents,'panel_paths':panels,'panel_depth':5.5,'vent_floor':-9,'radiator_floor':-11,'fin_top':.65};(W/'regions.json').write_text(json.dumps(reg,indent=2))
h=np.zeros((N,N),np.float32);glass=h.copy();seal=h.copy();flat=h.copy();structure=h.copy();fin=h.copy();pan=h.copy()
def apply(sl,z,mask,f=None):
 h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask)
 if f is not None:fin[sl]=np.maximum(fin[sl],f)
for p in glass_polys:
 sl,d=roi(p,7,lambda:poly(p));g=smooth(0,1.2,d);glass[sl]=np.maximum(glass[sl],g);seal[sl]=np.maximum(seal[sl],smooth(-5,-3,d)*(1-g))
for a,b,c,d in flat_boxes:
 p=[(a,b),(c,b),(c,d),(a,d)];sl,dst=roi(p,2,lambda:poly(p));flat[sl]=np.maximum(flat[sl],smooth(0,1,dst))
for a,b,r,count,axis in vents:
 def calc():
  d=capsule(a,b,r);v=np.subtract(b,a);length=np.linalg.norm(v);v=v/length;across=-(X-a[0])*v[1]+(Y-a[1])*v[0];along=(X-a[0])*v[0]+(Y-a[1])*v[1];f=np.zeros_like(X)
  pitch=(2*r/(count+1)) if axis=='long' else length/(count+1)
  for i in range(count):f=np.maximum(f,1-smooth(pitch*.12,pitch*.36,np.abs((across if axis=='long' else along)-((i-(count-1)/2)*pitch if axis=='long' else (i+1)*pitch))))
  f*=smooth(1.8,3.7,d);return -9*smooth(0,2.4,d)+9.65*f,smooth(-.6,0,d),f
 sl,(z,mask,f)=roi([a,b],r+2,calc);apply(sl,z,mask,f)
# Fin stacks are constructed independently of the chipped diffuse paint.
grilles=[([(827,55),(1030,55),(1030,114),(827,114)],19.5,831),([(929,524),(1253,499),(1253,558),(929,558)],20,934),([(303,988),(474,822),(478,928),(305,1077)],23,305),([(579,1130),(704,1130),(704,1192),(579,1192)],14,582),([(580,1220),(704,1220),(704,1253),(580,1253)],14,582)]
for p,pitch,start in grilles:
 def grille():
  d=poly(p);f=(1-smooth(pitch*.12,pitch*.31,np.abs((X-start+pitch/2)%pitch-pitch/2)))*smooth(1.7,3.2,d)
  return -8*smooth(0,2,d)+8.9*f,smooth(-.5,0,d),f
 sl,(z,mask,f)=roi(p,2,grille);apply(sl,z,mask,f)
# Recessed machined ports with a raised rim; their centres are not inflated buttons.
for cx,cy,r in [(622,83,23),(622,143,23),(622,205,23),(690,329,32),(771,329,32),(456,652,44),(293,205,24)]:
 def port():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);inside=1-smooth(r-4,r,rr);rim=1-smooth(1,3,np.abs(rr-(r-3)));return -4*inside+4.5*rim,1-smooth(r,r+1,rr),rim
 sl,(z,mask,f)=roi([(cx,cy)],r+2,port);apply(sl,z,mask,f)
for path in panels:
 for a,b in zip(path,path[1:]):
  sl,d=roi([a,b],3,lambda:capsule(a,b,1.85));f=smooth(0,1.4,d);pan[sl]=np.maximum(pan[sl],f)
pan*=1-np.maximum(structure,np.maximum(glass,np.maximum(seal,flat)));h-=5.5*pan;h=h*(1-seal)-.4*seal;h=h*(1-glass)-.55*glass;h*=1-flat
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';im.scale(N,N);a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(N,N,4)[::-1,:,:3].copy()
rgb=load(M/'phoenix_worn_basecolor_generated_v1.png');mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);bronze=smooth(1.10,1.32,rgb[:,:,0]/(rgb[:,:,1]+1e-6))*smooth(1.10,1.36,rgb[:,:,1]/(rgb[:,:,2]+1e-6));paint=smooth(.09,.24,sat)*(1-bronze);metal=np.maximum((1-paint)*smooth(.15,.45,lum)*.88,bronze*.75);metal=metal*(1-structure)+(.08+.78*fin)*structure;metal*=1-np.maximum(flat,np.maximum(glass,seal));metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));variation=np.sin(X*.034)*np.sin(Y*.026)
rough=np.clip(.84*(1-metal)+.48*metal+.065*wear+.018*variation,.44,.94);rough=rough*(1-structure)+(.9-.43*fin+.02*variation)*structure;rough=rough*(1-pan)+.90*pan;rough=rough*(1-flat)+.83*flat;rough=rough*(1-seal)+.9*seal;rough=rough*(1-glass)+(.14+.022*wear)*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);records={}
def save(a,key,colorspace='Non-Color'):
 buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Phoenix '+key,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());im.scale(OUT,OUT);p=M/f'phoenix_worn_{key}_4k_v1.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='16' if key!='basecolor' else '8';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+20)/32),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fin),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
mat=bpy.data.materials.new('Phoenix_Worn_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
for key,im in maps.items():
 im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;links.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
models={};aspects=[]
for o in obs:
 m=o.data;m.materials[0]=mat;b=before[o.name];assert b['v']==[list(v.co) for v in m.vertices] and b['f']==[list(p.vertices) for p in m.polygons] and b['n']==[list(n.vector) for n in m.corner_normals]
 for name,values in b['uv'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 models[o.name]={'vertices':[list(v.co) for v in m.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
 for p in m.polygons:
  if p.material_index==1:continue
  pts=np.array([list(o.matrix_world@m.vertices[i].co) for i in p.vertices]);e=pts[1:]-pts[0];n=np.cross(*e);n/=max(np.linalg.norm(n),1e-9);t=e[0]/np.linalg.norm(e[0]);local=e@np.stack((t,np.cross(n,t)),axis=1);q=np.array([list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices]);sing=np.linalg.svd(np.linalg.solve(local,q[1:]-q[0]),compute_uv=False);aspects.append(float(sing[0]/max(sing[1],1e-12)))
assert max(aspects)<4.1;scene=D/'phoenix_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
report=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),active_uv=newuv,parts=3,stored_triangles=494,visible_triangles=478,original_geometry_normals_and_uvs_preserved=True,uv_repairs=repairs,max_visible_uv_anisotropy=max(aspects),maps=records,models=models,structural_height_only=True,emissives='deferred',runtime_visual_validation='left to user as requested',statistics={'glass_roughness_median':float(np.median(rough[glass>.99])),'glass_metallic_max':float(metal[glass>.99].max()),'height_min':float(h.min()),'height_max':float(h.max()),'steel_roughness_median':float(np.median(rough[(metal>.7)&(structure<.1)]))});(W/'validation.json').write_text(json.dumps(report,indent=2));print('PHOENIX_PBR_COMPLETE',report['statistics'],flush=True)

for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
