from pathlib import Path
import bpy,numpy as np,json,hashlib,math
from bpy_extras.object_utils import world_to_camera_view

D=Path(__file__).resolve().parents[2];W=D/'recipes/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
src=D/'crusader_source_review.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];source_sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.context.view_layer.update()
before={o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'n':[list(n.vector) for n in o.data.corner_normals],'uv':{u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers}} for o in obs}
newuv='Crusader_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
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
glass_polys=[[(21,184),(33,177),(78,249),(43,260)],[(49,294),(80,282),(118,402),(85,415)],[(94,438),(116,431),(108,466)],[(152,335),(191,335),(191,389),(152,389)],[(152,399),(191,399),(191,480),(152,480)],[(233,389),(301,423),(301,453),(233,476)],[(880,436),(939,436),(940,500)]]
flat_boxes=[(593,936,889,1119),(887,662,1126,933),(606,376,746,469),(755,465,854,525),(650,631,717,667),(718,672,858,726),(90,645,148,728),(179,645,267,675),(745,230,1090,346),(391,1127,638,1240)]
vents=[((125,118),(313,118),14,1,'long'),((52,580),(52,710),16,1,'long'),((1008,462),(1008,627),15,1,'long'),((1082,462),(1082,627),15,1,'long'),((1028,985),(1195,985),18,5,'long'),((1028,1069),(1195,1069),18,5,'long')]
panels=[[(0,78),(298,78)],[(57,196),(283,196)],[(194,161),(194,297)],[(112,230),(282,230)],[(321,37),(321,318)],[(321,235),(574,235)],[(429,152),(429,376)],[(505,242),(505,377)],[(586,510),(628,510)],[(632,484),(632,576)],[(580,606),(580,941)],[(537,679),(713,679)],[(590,818),(888,818)],[(590,859),(734,859)],[(590,903),(734,903)],[(738,692),(738,672)],[(809,573),(885,573)],[(770,197),(1125,197)],[(935,373),(935,419)],[(0,502),(136,502)],[(19,750),(78,750)],[(79,543),(79,803)],[(152,633),(152,794)],[(19,863),(181,863)],[(19,903),(181,903)],[(77,956),(116,956)],[(20,1106),(76,1106)],[(154,1218),(264,1218)],[(341,1126),(377,1126)],[(343,1219),(375,1219)],[(481,1070),(529,1070)],[(484,994),(529,994)],[(225,902),(731,902)],[(407,929),(407,954)],[(412,997),(412,1041)],[(540,759),(717,759)],[(363,764),(453,764)],[(358,805),(455,805)],[(1130,822),(1253,822)],[(1130,884),(1253,884)],[(1130,777),(1253,777)],[(1130,560),(1253,560)],[(894,1133),(1244,1133)],[(974,1126),(974,1253)],[(637,1180),(970,1180)],[(731,1122),(731,1253)],[(354,0),(354,58)],[(537,0),(537,20)],[(664,30),(664,149)]]
grilles=[([(418,386),(589,386),(589,460),(418,460)],21,446,'x'),([(754,250),(1074,250),(1074,279),(754,279)],7,253,'y'),([(754,307),(1074,307),(1074,328),(754,328)],7,309,'y')]
reg=dict(coordinate_resolution=N,glass=glass_polys,flat_graphics_boxes=flat_boxes,vents=vents,grilles=grilles,panel_paths=panels,normal_source='Manually placed structural shapes, never diffuse luminance',glass_response='Nonmetallic; roughness 0.14; flat normal inside existing frames',vent_depth=4,panel_depth=1.6)
(W/'regions.json').write_text(json.dumps(reg,indent=2)+'\n')
h=np.zeros((N,N),np.float32);glass=h.copy();seal=h.copy();flat=h.copy();structure=h.copy();fin=h.copy();pan=h.copy()
def apply(sl,z,mask,f=None):
 h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask)
 if f is not None:fin[sl]=np.maximum(fin[sl],f)
for p in glass_polys:
 sl,d=roi(p,5,lambda:poly(p));g=smooth(0,1.5,d);glass[sl]=np.maximum(glass[sl],g);seal[sl]=np.maximum(seal[sl],smooth(-3.5,-1.5,d)*(1-g))
for a,b,c,d in flat_boxes:
 p=[(a,b),(c,b),(c,d),(a,d)];sl,dst=roi(p,2,lambda:poly(p));flat[sl]=np.maximum(flat[sl],smooth(0,1,dst))
for a,b,r,count,axis in vents:
 def calc():
  d=capsule(a,b,r);v=np.subtract(b,a);length=np.linalg.norm(v);v=v/length;across=-(X-a[0])*v[1]+(Y-a[1])*v[0];along=(X-a[0])*v[0]+(Y-a[1])*v[1];f=np.zeros_like(X)
  if count>1:
   pitch=2*r/(count+1)
   for i in range(count):f=np.maximum(f,1-smooth(pitch*.13,pitch*.38,np.abs(across-(i-(count-1)/2)*pitch)))
  f*=smooth(2,4,d);return -4*smooth(0,3,d)+4.25*f,smooth(0,1,d),f
 sl,(z,mask,f)=roi([a,b],r+2,calc);apply(sl,z,mask,f)
for p,pitch,start,axis in grilles:
 def grille():
  d=poly(p);coord=X if axis=='x' else Y;f=(1-smooth(pitch*.12,pitch*.32,np.abs((coord-start+pitch/2)%pitch-pitch/2)))*smooth(2,4,d)
  return -3.5*smooth(0,3,d)+3.75*f,smooth(0,1,d),f
 sl,(z,mask,f)=roi(p,2,grille);apply(sl,z,mask,f)
# Recessed circular vents with horizontal fin rows, confined inside the black opening.
for cx,cy,r in [(1198,684,39)]:
 def round_vent():
  d=r-np.hypot(X-cx,Y-cy);f=(1-smooth(1,2.2,np.abs((Y-cy+5)%10-5)))*smooth(3,6,d);return -4*smooth(0,3,d)+4.3*f,smooth(0,1,d),f
 sl,(z,mask,f)=roi([(cx,cy)],r+2,round_vent);apply(sl,z,mask,f)
# Fasteners are small machined recesses; painted labels and insignia remain flat.
for cx,cy,r in [(373,191,24),(372,284,24),(794,426,21),(123,582,20),(220,582,20),(760,767,23),(835,766,23),(407,532,29),(677,532,29)]:
 def port():
  rr=np.hypot(X-cx,Y-cy);inside=1-smooth(r-4,r,rr);rim=1-smooth(.7,2.5,np.abs(rr-(r-3)));return -1.6*inside+1.9*rim,1-smooth(r,r+1,rr),rim
 sl,(z,mask,f)=roi([(cx,cy)],r+2,port);apply(sl,z,mask,f)
for path in panels:
 for a,b in zip(path,path[1:]):
  sl,d=roi([a,b],3,lambda:capsule(a,b,1.7));pan[sl]=np.maximum(pan[sl],smooth(0,1.5,d))
pan*=1-np.maximum(structure,np.maximum(glass,np.maximum(seal,flat)));h-=1.6*pan;h=h*(1-seal)-.3*seal;h=h*(1-glass)-.4*glass;h*=1-flat
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(N,N,4)[::-1,:,:3].copy()
rgb=load(M/'crusader_worn_basecolor_generated_v1.png');mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);paint=smooth(.12,.3,sat);metal=(1-paint)*smooth(.15,.48,lum)*.86;metal=metal*(1-structure)+(.08+.74*fin)*structure;metal*=1-np.maximum(flat,np.maximum(glass,seal));metal=metal*(1-pan)+.04*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));variation=np.sin(X*.034)*np.sin(Y*.026)
rough=np.clip(.8*(1-metal)+.5*metal+.05*wear+.012*variation,.47,.9);rough=rough*(1-structure)+(.9-.38*fin)*structure;rough=rough*(1-pan)+.89*pan;rough=rough*(1-flat)+.81*flat;rough=rough*(1-seal)+.87*seal;rough=rough*(1-glass)+.14*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);records={}
def save(a,key,colorspace='Non-Color'):
 buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Crusader '+key,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());im.scale(OUT,OUT);p=M/f'crusader_worn_{key}_4k_v1.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='16' if key!='basecolor' else '8';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+8)/12),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fin),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
mat=bpy.data.materials.new('Crusader_Worn_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
assert max(aspects)<4.1
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for attempt in range(100):
  prior=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if not all(.07<t.x<.93 and .07<t.y<.93 and t.z>0 for t in q):cam.location=prior;break
scene=D/'crusader_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.image_settings.color_depth='8';s.cycles.samples=32;s.render.resolution_x=1440;s.render.resolution_y=1080;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
report=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),active_uv=newuv,parts=3,stored_triangles=382,visible_triangles=350,original_geometry_normals_and_uvs_preserved=True,uv_repairs=[],max_visible_uv_anisotropy=max(aspects),maps=records,models=models,structural_height_only=True,emissives='deferred',runtime_visual_validation='pending_user_review',statistics={'glass_roughness_median':float(np.median(rough[glass>.99])),'glass_metallic_max':float(metal[glass>.99].max()),'height_min':float(h.min()),'height_max':float(h.max())});(W/'validation.json').write_text(json.dumps(report,indent=2));print('CRUSADER_PBR_COMPLETE',report['statistics'],flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
