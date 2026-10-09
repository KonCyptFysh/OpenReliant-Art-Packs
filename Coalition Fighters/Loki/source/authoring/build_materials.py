import os
from pathlib import Path
import bpy,numpy as np,json,math,hashlib
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(str(Path(os.environ['LOKI_WORKSPACE'])));W=D/'work/reconstruction_v1';M=D/'maps';R=D/'review/reconstruction_v1';R.mkdir(parents=True,exist_ok=True);N=1254;OUT=4096
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
reg={'glass': [[(53, 14), (400, 14), (414, 24), (418, 34), (418, 70), (409, 86), (394, 90), (58, 89), (39, 80), (31, 64), (31, 34), (40, 20)], [(452, 14), (504, 14), (517, 26), (524, 40), (523, 62), (513, 80), (500, 88), (452, 88), (438, 75), (437, 29)], [(591, 41), (752, 41), (772, 56), (751, 72), (591, 73), (576, 61), (576, 51)], [(176, 578), (506, 619), (517, 626), (537, 640), (539, 654), (525, 675), (511, 682), (478, 680), (169, 610), (157, 599), (160, 587)]], 'flat': [(175, 239, 528, 342), (810, 255, 1130, 344), (109, 472, 490, 570), (511, 457, 1214, 577), (637, 596, 950, 625), (980, 651, 1232, 836), (877, 1077, 1018, 1177), (0, 1201, 247, 1246), (1138, 1200, 1253, 1246), (43, 695, 70, 773), (224, 754, 272, 829), (539, 715, 589, 777), (538, 597, 614, 639), (853, 678, 948, 717), (580, 1185, 733, 1249), (482, 582, 516, 612), (92, 893, 126, 921), (9, 1161, 52, 1194), (586, 769, 619, 793), (587, 842, 621, 867), (614, 641, 637, 674), (436, 1001, 455, 1051), (507, 1001, 533, 1052), (365, 1090, 391, 1118), (362, 940, 392, 971)], 'vents': [((590, 137), (854, 137), 17, 3), ((589, 206), (854, 206), 17, 3), ((1050, 54), (1222, 54), 18, 2), ((756, 368), (1205, 368), 9, 1), ((756, 402), (1205, 402), 9, 1), ((757, 437), (1206, 437), 9, 1), ((174, 511), (350, 511), 9, 1), ((174, 541), (350, 541), 9, 1), ((633, 797), (885, 797), 11, 1), ((633, 840), (885, 840), 11, 1), ((681, 925), (815, 925), 19, 3), ((680, 1017), (810, 1017), 19, 3), ((224, 1016), (356, 1016), 7, 1), ((224, 1034), (356, 1034), 7, 1), ((224, 1051), (356, 1051), 7, 1), ((1006, 1006), (1160, 902), 12, 1), ((1080, 1063), (1182, 940), 12, 1), ((925, 140), (925, 193), 9, 1), ((960, 140), (960, 193), 9, 1), ((993, 140), (993, 193), 9, 1), ((1028, 140), (1028, 193), 9, 1), ((159, 138), (329, 138), 8, 1)], 'radiators': [([(24, 238), (139, 238), (139, 335), (24, 335)], 'y', [245, 253, 261, 269, 277, 285, 293, 301, 309, 317, 325, 333], 1.0), ([(84, 775), (123, 760), (155, 792), (158, 844), (128, 872), (82, 872), (63, 846), (64, 803)], 'x', [78, 94, 109, 124, 139], 2.1)], 'panels': [[[172, 199], [172, 469]], [[359, 163], [359, 241]], [[183, 199], [559, 199]], [[363, 161], [559, 161]], [[559, 0], [559, 260]], [[674, 0], [674, 88]], [[848, 0], [848, 258]], [[975, 0], [975, 110]], [[654, 267], [654, 466]], [[173, 368], [357, 368], [357, 471]], [[370, 347], [370, 471]], [[2, 343], [170, 343]], [[945, 346], [945, 455]], [[139, 620], [139, 715], [211, 749], [211, 836]], [[34, 696], [34, 881], [77, 933], [142, 933], [142, 910], [208, 837], [517, 837]], [[271, 686], [271, 723]], [[445, 847], [445, 919]], [[517, 713], [517, 1178]], [[523, 881], [599, 881]], [[636, 716], [942, 716]], [[947, 723], [947, 881]], [[873, 881], [873, 1080]], [[564, 1057], [637, 1057]], [[1037, 1080], [1241, 1080]], [[1123, 1039], [1240, 1039]], [[74, 940], [74, 1155]], [[178, 1142], [178, 1201]], [[556, 1154], [556, 1253]], [[524, 1181], [637, 1181]], [[1040, 1193], [1126, 1193]]]}
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
im=bpy.data.images.load(str(M/'loki_hull_glazing_refined_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);paint=smooth(.12,.3,sat);metal=(1-paint)*smooth(.15,.48,lum)*.72;metal=metal*(1-structure)+(.08+.68*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.04*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));rough=np.clip(.81*(1-metal)+.54*metal+.04*wear,.51,.90);rough=rough*(1-structure)+(.87-.33*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.16*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[protected>.01]=(0,0,1);metal[protected>.01]=0;records={}
def save(a,key,colorspace='Non-Color'):
 if '--reuse-unchanged-maps' in __import__('sys').argv and key not in ('normal','metallic') and (M/f'loki_hull_{key}_v1.png').is_file():
  p=M/f'loki_hull_{key}_v1.png';records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[OUT,OUT]};existing=bpy.data.images.load(str(p),check_existing=False);existing.colorspace_settings.name=colorspace;return existing
 b=np.ones((N,N,4),np.float32);b[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Loki '+key,N,N,alpha=False,float_buffer=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(b[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  nb=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(nb);na=nb.reshape(-1,4);nn=na[:,:3]*2-1;nn/=np.maximum(np.linalg.norm(nn,axis=-1,keepdims=True),1e-8);na[:,:3]=nn*.5+.5;im.pixels.foreach_set(na.ravel())
 p=M/f'loki_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
newuv='Loki_Delivery_UV_v1';mat=bpy.data.materials.new('Loki_Worn_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
for key,im in maps.items():
 im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT';links.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
hidden_mat=bpy.data.materials.new('Native caps hidden on intact ship');hidden_mat.use_nodes=True;hn=hidden_mat.node_tree.nodes;hn.clear();hb=hn.new('ShaderNodeBsdfTransparent');ho=hn.new('ShaderNodeOutputMaterial');hidden_mat.node_tree.links.new(hb.outputs[0],ho.inputs[0])
meta=json.loads((D/'source/native_parts.json').read_text());meshes=[];audit=[];root=bpy.data.objects.new('Native coordinates to upright',None);bpy.context.collection.objects.link(root);root.rotation_euler=(-math.pi/2,0,0);root.scale=(.0025,)*3
for desc in meta:
 part=desc['index'];lod=desc['lods'][0];verts=lod['vertices'];normals=lod['normals'];faces=[];uvs=[];hidden=[]
 for f in lod['faces']:
  idx=f['vertices'].copy();pairs=[(u,v) for u,v in f['uv']] # Parser already stores Blender UVs
  norm=Vector(f['normal'])
  if f['kind']==3:idx[1],idx[2]=idx[2],idx[1];pairs[1],pairs[2]=pairs[2],pairs[1]
  pts=[Vector(verts[j]) for j in idx]
  if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(norm)<0:idx[1],idx[2]=idx[2],idx[1];pairs[1],pairs[2]=pairs[2],pairs[1]
  faces.append(idx);uvs.extend(pairs);hidden.append(f['hidden'])
 mesh=bpy.data.meshes.new(desc['name']);mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='Original_Loki_UV')
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
 o.parent=meshes[desc['parent']] if desc['parent']>=0 else root
 track=desc['tracks'][0];keys=track['keys'];axis=Matrix(np.array(desc['orientation']).reshape(3,3).tolist());mount=Vector(desc['mount']);origin=Vector(desc['origin'])
 for t in range(0,401,4):
  l=keys[0];r=keys[-1]
  for k in keys:
   if k['time']<=t:l=k
   if k['time']>=t:r=k;break
  f=np.clip((t-l['time'])/max(r['time']-l['time'],1),0,1);angles=(1-f)*np.array(l['angles'])+f*np.array(r['angles']);offset=Vector((1-f)*np.array(l['offset'])+f*np.array(r['offset']));angles=np.where(np.array(desc['still']),0,angles)
  turn=axis.transposed()@rotation(angles)@axis;o.location=origin-Vector(meta[desc['parent']]['origin'] if desc['parent']>=0 else [0,0,0])+mount-turn@(mount-offset);o.rotation_quaternion=turn.to_quaternion();o.keyframe_insert(data_path='location',frame=t/4+1);o.keyframe_insert(data_path='rotation_quaternion',frame=t/4+1)
 o['animation_source']='Native fighting position keyframes; 400 units at 100 units/sec; source track retained verbatim in SHP'
s=bpy.context.scene;s.frame_start=1;s.frame_end=101;s.render.fps=25;s.timeline_markers.new('FOLDED',frame=1);s.timeline_markers.new('FIGHTING POSITION',frame=101);s.frame_set(1);s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
s.world=bpy.data.worlds.new('Neutral authoring studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.065,.055,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,loc,power,sz in [('Key',(3,5,7),800,5),('Fill',(-4,2,3),450,4),('Rim',(2,-5,5),950,4),('Bottom',(0,0,-5),300,4)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=sz;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc in [('Front',(4,6,3.5)),('Opposite',(-4,6,3.5)),('Belly',(5,7,-5)),('Rear',(-6,-9,5))]:
 data=bpy.data.cameras.new(name);data.lens=60;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
s.frame_set(1);bpy.context.view_layer.update()
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]);root.location-=centre
for cam in [o for o in s.objects if o.type=='CAMERA']:
 s.frame_set(101)
 for attempt in range(100):
  bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in meshes for v in o.data.vertices]
  if all(.06<t.x<.94 and .06<t.y<.94 and t.z>0 for t in q):break
  cam.location*=1.04
 for attempt in range(100):
  prev=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in meshes for v in o.data.vertices]
  if not all(.08<t.x<.92 and .08<t.y<.92 and t.z>0 for t in q):cam.location=prev;break
s.frame_set(1);s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;scene=D/'loki_worn_pbr_v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
assert len(meshes)==7 and sum(len(o.data.polygons) for o in meshes)==526
report=dict(scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),parts=audit,active_uv=newuv,triangles=526,native_geometry_normals_and_original_uvs_preserved=True,uv_repairs=[],maps={'hull':records},structural_height_only=True,generated_art_resolution=[1254,1254],delivery_resolution=[4096,4096],emissives='deferred',runtime_visual_validation='pending_user_review',animation=dict(parts=7,moving_parts=6,stowed_frame=1,deployed_frame=101,native_export='Original animation bytes preserved; Blender timeline is an editable preview'))
(W/'validation.json').write_text(json.dumps(report,indent=2));print('LOKI_MATERIALS_AND_SOURCE_READY',flush=True)
for name,frame in [('Front',1),('Opposite',1),('Belly',101)]:
 s.frame_set(frame);s.camera=bpy.data.objects[name];s.render.filepath=str(R/f'material_{name.lower()}.png');bpy.ops.render.render(write_still=True)
