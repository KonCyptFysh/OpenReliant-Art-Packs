import os
from pathlib import Path
import bpy,numpy as np,json,math,hashlib
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(str(Path(os.environ['KAMOV_WORKSPACE'])));W=D/'work/reconstruction_v1';M=D/'maps';R=D/'review/reconstruction_v1';N=1254;OUT=4096
bpy.ops.wm.read_factory_settings(use_empty=True)
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def poly(p):
 p=np.array(p);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
reg={
 'glass': [[(266,764),(365,764),(387,787),(389,844),(367,867),(266,867),(244,842),(244,786)],[(115,785),(163,786),(213,835),(203,836),(116,795)],[(373,937),(428,886),(439,895),(439,947),(429,956),(373,956)]],
 'flat':[(607,21,741,144),(138,463,282,594),(0,809,68,952),(948,359,1043,423),(947,430,980,572),(871,94,1223,110),(870,171,1236,189),(872,228,1240,249),(874,306,1239,328),(235,369,325,411),(108,879,187,919),(875,378,904,457),(607,352,779,398),(607,558,779,600),(148,356,223,434),(975,684,1173,829),(579,1013,779,1215),(305,1044,351,1134),(439,1076,489,1149)],
 'vents':[((236,235),(330,235),19,3),((705,849),(868,849),15,1),((706,915),(868,915),15,1),((992,1143),(1037,1143),15,1),((992,1209),(1037,1209),13,1)],
 'radiators':[([(438,335),(496,335),(496,757),(438,757)],'x',[448,470,490],2.1), ([(502,804),(565,778),(568,801),(568,909),(555,923),(510,920),(502,907)],'y',list(range(808,916,20)),2.5), ([(958,859),(1191,859),(1191,1050),(958,1050)],'y',list(range(874,1046,20)),2.5), ([(956,604),(1188,604),(1188,650),(956,650)],'y',[615,640],2.1), ([(79,0),(109,0),(109,75),(79,75)],'x',[84,99],1.3), ([(80,1157),(110,1157),(110,1254),(80,1254)],'x',[86,102],1.4)],
 'panels': [[(197,0),(197,147)],[(220,0),(220,147)],[(273,0),(273,147)],[(196,85),(273,85)],[(286,0),(286,147)],[(433,0),(433,147)],[(510,0),(510,144)],[(555,14),(555,144)],[(594,0),(594,326)],[(749,0),(749,243)],[(597,150),(869,150)],[(598,243),(870,243)],[(374,179),(597,179)],[(370,244),(596,244)],[(371,291),(596,291)],[(474,184),(474,325)],[(604,354),(873,354)],[(710,355),(710,553)],[(606,400),(871,400)],[(606,552),(850,552)],[(652,408),(652,550)],[(270,433),(270,591)],[(117,505),(286,505)],[(121,594),(383,594)],[(124,689),(382,689)],[(103,787),(103,1020)],[(198,845),(198,1023)],[(28,944),(195,944)],[(669,656),(795,656)],[(801,657),(889,657)],[(668,703),(887,703)],[(669,751),(887,751)],[(793,650),(793,801)],[(946,331),(946,853)],[(984,333),(984,571)],[(990,433),(1253,433)],[(1047,445),(1047,567)],[(991,538),(1253,538)],[(371,1009),(742,1009)],[(432,1010),(432,1219)],[(509,1026),(509,1220)],[(177,1025),(177,1253)],[(275,1027),(275,1253)],[(122,1150),(272,1150)]]}
(W/'regions.json').write_text(json.dumps(dict(coordinate_resolution=N,regions=reg,normal_source='Traced structural shapes only; glazing and graphics flat'),indent=2))
h=np.zeros((N,N),np.float32);glass=h.copy();seal=h.copy();flat=h.copy();structure=h.copy();fins=h.copy();pan=h.copy()
for p in reg['glass']:
 d=poly(p);glass=np.maximum(glass,smooth(0,1.2,d));seal=np.maximum(seal,smooth(-3,-1,d))
for a,b,c,d in reg['flat']:flat=np.maximum(flat,smooth(0,2,poly([(a,b),(c,b),(c,d),(a,d)])))
for a,b,r,count in reg['vents']:
 d=capsule(a,b,r);v=np.subtract(b,a);v=v/np.linalg.norm(v);across=-(X-a[0])*v[1]+(Y-a[1])*v[0];f=np.zeros_like(X)
 if count>1:
  pitch=2*r/(count+1)
  for i in range(count):f=np.maximum(f,1-smooth(pitch*.12,pitch*.35,np.abs(across-(i-(count-1)/2)*pitch)))
 else:f=1-smooth(2,5,np.abs(across))
 f*=smooth(3,5,d);mask=smooth(0,1.5,d);z=-1.2*smooth(0,4,d)+1.5*f;h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,f)
for points,axis,positions,width in reg['radiators']:
 d=poly(points);mask=smooth(0,2,d);f=np.zeros_like(X)
 for position in positions:f=np.maximum(f,1-smooth(width,width+3,np.abs((X if axis=='x' else Y)-position)))
 f*=smooth(3,5,d);z=-.6*smooth(0,3,d)+1.05*f;h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,f)
for path in reg['panels']:
 for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.2,capsule(a,b,1.45)))
protected=np.maximum(flat,seal);pan*=1-np.maximum(protected,structure);h-=.40*pan;h*=1-protected
im=bpy.data.images.load(str(M/'kamov_hull_generated_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);paint=smooth(.12,.3,sat);metal=(1-paint)*smooth(.15,.48,lum)*.72;metal=metal*(1-structure)+(.08+.68*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.04*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));rough=np.clip(.81*(1-metal)+.54*metal+.04*wear,.51,.90);rough=rough*(1-structure)+(.87-.33*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.16*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[seal>.01]=(0,0,1);records={}
def save(a,key,colorspace='Non-Color'):
 b=np.ones((N,N,4),np.float32);b[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Kamov '+key,N,N,alpha=False,float_buffer=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(b[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  nb=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(nb);na=nb.reshape(-1,4);nn=na[:,:3]*2-1;nn/=np.maximum(np.linalg.norm(nn,axis=-1,keepdims=True),1e-8);na[:,:3]=nn*.5+.5;im.pixels.foreach_set(na.ravel())
 p=M/f'kamov_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
newuv='Kamov_Delivery_UV_v1';mat=bpy.data.materials.new('Kamov_Worn_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
for key,im in maps.items():
 im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT';links.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
hidden_mat=bpy.data.materials.new('Native caps hidden on intact ship');hidden_mat.use_nodes=True;hn=hidden_mat.node_tree.nodes;hn.clear();hb=hn.new('ShaderNodeBsdfTransparent');ho=hn.new('ShaderNodeOutputMaterial');hidden_mat.node_tree.links.new(hb.outputs[0],ho.inputs[0])
meta=json.loads((D/'source/native_parts.json').read_text());meshes=[];audit=[];root=bpy.data.objects.new('Native coordinates to upright',None);bpy.context.collection.objects.link(root);root.rotation_euler=(-math.pi/2,0,0);root.scale=(.0025,)*3
for desc in meta:
 part=desc['index'];lod=desc['lods'][0];verts=lod['vertices'];normals=lod['normals'];faces=[];uvs=[];hidden=[]
 for f in lod['faces']:
  idx=f['vertices'].copy();pairs=[(u,v) for u,v in f['uv']] # Parser already stores Blender UVs;norm=Vector(f['normal'])
  if f['kind']==3:idx[1],idx[2]=idx[2],idx[1];pairs[1],pairs[2]=pairs[2],pairs[1]
  pts=[Vector(verts[j]) for j in idx]
  if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(norm)<0:idx[1],idx[2]=idx[2],idx[1];pairs[1],pairs[2]=pairs[2],pairs[1]
  faces.append(idx);uvs.extend(pairs);hidden.append(f['hidden'])
 mesh=bpy.data.meshes.new(desc['name']);mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='Original_Kamov_UV')
 for q,v in zip(uv.data,uvs):q.uv=v
 mesh.uv_layers.new(name=newuv,do_init=True);mesh.uv_layers.active=mesh.uv_layers[newuv];mesh.uv_layers.active.active_render=True
 mesh.materials.append(mat);mesh.materials.append(hidden_mat)
 for p,hide in zip(mesh.polygons,hidden):p.use_smooth=True;p.material_index=int(hide)
 mesh.normals_split_custom_set([normals[l.vertex_index] for l in mesh.loops]);o=bpy.data.objects.new(desc['name'],mesh);o['native_part_index']=part;o['native_origin']=desc['origin'];o['native_mount']=desc['mount'];o['native_orientation']=desc['orientation'];o['native_material_indices']=[f['material'] for f in lod['faces']];bpy.context.collection.objects.link(o);o.parent=root;o.location=desc['origin'];o.rotation_mode='QUATERNION';meshes.append(o);audit.append(dict(index=part,name=o.name,vertices=len(verts),faces=len(faces),visible_faces=len(faces)-sum(hidden)))
bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);root.location=-(lo+hi)/2
# Reproduce native angle/offset interpolation and mount-axis pose; no animation export roundtrip.
def rotation(angles):
 p,y,r=angles;sp,cp=math.sin(p),math.cos(p);sy,cy=math.sin(y),math.cos(y);sr,cr=math.sin(r),math.cos(r)
 return Matrix(((cr*cy,-sr*cy,sy),(sr*cp+cr*sy*sp,cr*cp-sr*sy*sp,-cy*sp),(sr*sp-cr*sy*cp,cr*sp+sr*sy*cp,cy*cp)))
for o,desc in zip(meshes,meta):
 assert desc['parent']==-1
 track=desc['tracks'][0];keys=track['keys'];axis=Matrix(np.array(desc['orientation']).reshape(3,3).tolist());mount=Vector(desc['mount']);origin=Vector(desc['origin'])
 for t in range(0,401,4):
  l=keys[0];r=keys[-1]
  for k in keys:
   if k['time']<=t:l=k
   if k['time']>=t:r=k;break
  f=np.clip((t-l['time'])/max(r['time']-l['time'],1),0,1);angles=(1-f)*np.array(l['angles'])+f*np.array(r['angles']);offset=Vector((1-f)*np.array(l['offset'])+f*np.array(r['offset']));angles=np.where(np.array(desc['still']),0,angles)
  turn=axis.transposed()@rotation(angles)@axis;o.location=origin+mount-turn@(mount-offset);o.rotation_quaternion=turn.to_quaternion();o.keyframe_insert(data_path='location',frame=t/4+1);o.keyframe_insert(data_path='rotation_quaternion',frame=t/4+1)
 o['animation_source']='Native deploy keyframes; 400 units at 100 units/sec; source track retained verbatim in SHP'
s=bpy.context.scene;s.frame_start=1;s.frame_end=101;s.render.fps=25;s.timeline_markers.new('STOWED',frame=1);s.timeline_markers.new('DEPLOYED',frame=101);s.frame_set(1);s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
s.world=bpy.data.worlds.new('Neutral authoring studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.065,.055,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,loc,power,sz in [('Key',(3,5,7),800,5),('Fill',(-4,2,3),450,4),('Rim',(2,-5,5),950,4),('Bottom',(0,0,-5),300,4)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=sz;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc in [('Front',(4,6,3.5)),('Opposite',(-4,6,3.5)),('Belly',(5,7,-5)),('Rear',(-6,-9,5))]:
 data=bpy.data.cameras.new(name);data.lens=60;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for cam in [o for o in s.objects if o.type=='CAMERA']:
 s.frame_set(101)
 for attempt in range(100):
  bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in meshes for v in o.data.vertices]
  if all(.06<t.x<.94 and .06<t.y<.94 and t.z>0 for t in q):break
  cam.location*=1.04
 for attempt in range(100):
  prev=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in meshes for v in o.data.vertices]
  if not all(.08<t.x<.92 and .08<t.y<.92 and t.z>0 for t in q):cam.location=prev;break
s.frame_set(1);s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;scene=D/'kamov_worn_pbr_v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
assert len(meshes)==16 and sum(len(o.data.polygons) for o in meshes)==670
report=dict(scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),parts=audit,active_uv=newuv,triangles=670,native_geometry_normals_and_original_uvs_preserved=True,uv_repairs=[],maps={'hull':records},structural_height_only=True,generated_art_resolution=[1254,1254],delivery_resolution=[4096,4096],emissives='deferred',runtime_visual_validation='pending_user_review',animation=dict(parts=16,moving_parts=12,stowed_frame=1,deployed_frame=101,native_export='Original animation bytes preserved; Blender timeline is an editable preview'))
(W/'validation.json').write_text(json.dumps(report,indent=2));print('KAMOV_MATERIALS_AND_SOURCE_READY',flush=True)
for name,frame in [('Front',1),('Opposite',1),('Belly',101)]:
 s.frame_set(frame);s.camera=bpy.data.objects[name];s.render.filepath=str(R/f'material_{name.lower()}.png');bpy.ops.render.render(write_still=True)
