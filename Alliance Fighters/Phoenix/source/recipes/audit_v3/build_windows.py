import os
import bpy, json, hashlib, numpy as np
from pathlib import Path
from mathutils import Vector
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v3';R=D/'review/audit_v3';M=D/'maps'
for p in [W,R]:p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((D.parent/'project_state.json').read_text());src=Path(state['latest_scene']);source_sha=sha(src)
assert src.name=='phoenix_worn_pbr_v2.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update()
before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uvs={u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers}) for o in s.objects if o.type=='MESH'}
old=json.loads((D/'work/audit_v2/validation.json').read_text());newuv='Phoenix_Delivery_UV_v3'
# Canonical front-side triangle: tip, rear upper and rear lower corners.
tri=np.array([[518.25,752.82],[690.63,677.87],[704.36,728.15]],np.float32)
for o in s.objects:
 if o.type!='MESH':continue
 m=o.data;u=m.uv_layers.new(name=newuv,do_init=True);m.uv_layers.active=u;u.active_render=True
 if o.name=='Phoenix_Cockpit':
  for index,lookup in [(86,{40:0,49:1,47:2}),(91,{32:0,48:1,34:2})]:
   for loop in m.polygons[index].loop_indices:
    q=tri[lookup[m.loops[loop].vertex_index]];u.data[loop].uv=(float(q[0]/1254),float(1-q[1]/1254))
ob=bpy.data.objects['Phoenix_Cockpit'];world=np.array([list(ob.matrix_world@ob.data.vertices[i].co) for i in [40,49,47]])
area2=np.linalg.norm(np.cross(world[1]-world[0],world[2]-world[0]));alt=np.array([area2/np.linalg.norm(world[(i+1)%3]-world[(i+2)%3]) for i in range(3)])
S=4096;scale=S/1254;box=(510,665,738,759);x0,y0,x1,y1=[int(round(v*scale)) for v in box];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/scale;Y=(yy+.5)/scale
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def signed_poly(points):
 p=np.array(points);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
inv=np.linalg.inv(np.vstack([tri.T,np.ones(3)]));bary=np.stack([X,Y,np.ones_like(X)],-1)@inv.T;distance=np.min(bary*alt,axis=-1)
# One physical inset controls all optical and material boundaries. The seal
# remains inside the mesh triangle, with a constant-width bronze surround.
glass=smooth(.0062,.00665,distance);surround=smooth(.0036,.00405,distance);seal=np.maximum(surround-glass,0)
old_outline=[(550,728),(705,676),(733,676),(733,728),(560,756)]
fill=smooth(-3,0,signed_poly(old_outline));edit=np.maximum(fill,surround)
assert np.all(glass[distance<=0]==0) and np.all(seal[distance<=0]==0)
def read(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);a=a.reshape(S,S,4)[::-1].copy();bpy.data.images.remove(im);return a
def save(a,key,bind=False):
 im=bpy.data.images.new('Phoenix v3 '+key,S,S,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());p=M/f'phoenix_worn_{key}_4k_v3.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if key=='basecolor' else '16';im.save();bpy.data.images.remove(im)
 if bind:
  im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack()
  for mat in bpy.data.materials:
   if mat.use_nodes:
    for n in mat.node_tree.nodes:
     if n.type=='TEX_IMAGE' and n.name=='Delivered '+key:n.image=im
 return {'path':str(p),'sha256':sha(p)}
maps=dict(old['maps']);locality={}
# Reuse an existing quiet bronze section for the former painted window rim.
# Its matching colour/roughness/metallic values keep the original worn finish.
sx=((X-510)/(738-510)*116+696)*scale;sy=((Y-665)/(759-665)*61+210)*scale
sx=np.clip(sx.astype(int),0,S-1);sy=np.clip(sy.astype(int),0,S-1)
h=-.32*surround-.50*glass;dy,dx=np.gradient(h);normal=np.stack((-dx*scale,dy*scale,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=read(Path(old['maps'][key]['path']));q=a[y0:y1,x0:x1,:3].copy();previous=q.copy();sample=a[sy,sx,:3]
 if key=='basecolor':
  q=q*(1-fill[:,:,None])+sample*fill[:,:,None];q=q*(1-surround[:,:,None])+np.array([.023,.029,.023])*surround[:,:,None];q=q*(1-glass[:,:,None])+np.array([.11,.17,.145])*glass[:,:,None]
 elif key in ['roughness','metallic']:
  q=q*(1-fill[:,:,None])+sample*fill[:,:,None];q=q*(1-surround[:,:,None])+(0.86 if key=='roughness' else 0)*surround[:,:,None];q=q*(1-glass[:,:,None])+(.10 if key=='roughness' else 0)*glass[:,:,None]
 elif key=='normal':q=q*(1-edit[:,:,None])+(normal*.5+.5)*edit[:,:,None]
 elif key=='glass':q=q*(1-edit[:,:,None])+glass[:,:,None]*edit[:,:,None]
 elif key=='seal':q=q*(1-edit[:,:,None])+seal[:,:,None]*edit[:,:,None]
 elif key=='height':q=q*(1-edit[:,:,None])+((h+20)/32)[:,:,None]*edit[:,:,None]
 elif key=='structure':q=q*(1-edit[:,:,None])+seal[:,:,None]*edit[:,:,None]
 else:q=q*(1-edit[:,:,None])
 assert np.array_equal(q[edit==0],previous[edit==0])
 a[y0:y1,x0:x1,:3]=q;maps[key]=save(a,key,key in ['basecolor','roughness','metallic','normal']);locality[key]={'outside_edit_mask_unchanged_before_encoding':True}
mask=np.zeros((S,S,4),np.float32);mask[:,:,3]=1;mask[y0:y1,x0:x1,:3]=edit[:,:,None];edit_record=save(mask,'window_edit_mask')
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   if n.type in ['UVMAP','NORMAL_MAP'] and n.uv_map=='Phoenix_Delivery_UV_v2':n.uv_map=newuv
models={}
for name,b in before.items():
 m=bpy.data.objects[name].data
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals]
 assert all(v==[list(q.uv) for q in m.uv_layers[k].data] for k,v in b['uvs'].items())
 for p in m.polygons:
  if name!='Phoenix_Cockpit' or p.index not in [86,91]:assert [list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices]==[b['uvs']['Phoenix_Delivery_UV_v2'][i] for i in p.loop_indices]
 models[name]={'vertices':b['vertices'],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
scene=D/'phoenix_worn_pbr_v3.blend';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_sha
report=dict(old);report.update(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,maps=maps,models=models,audit_changes={'triangular_window_faces':[86,91],'triangle_atlas_pixels':tri.tolist(),'glass_inset_world_units':.0062,'seal_inset_world_units':.0036,'glass_and_seal_inside_mesh_triangle':True,'glass_tint_srgb':[.11,.17,.145],'glass_roughness':.10,'glass_metallic':0,'map_locality':locality,'edit_mask':edit_record,'edit_bounds_atlas':box,'geometry_normals_previous_uv_layers_and_belly_repair_preserved':True},runtime_visual_validation='User requested triangular window and material boundary correction; v3 final visual review pending')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Close views of both matching windows, followed by overall previews.
cam=s.camera;target=Vector((0,1.47,.18));s.render.resolution_x=1200;s.render.resolution_y=700
for side,x in [('right',1.3),('left',-1.3)]:
 cam.location=target+Vector((x,.34,.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.68;s.camera=cam;s.render.filepath=str(R/f'window_{side}.png');bpy.ops.render.render(write_still=True)
for name in ['Front','Opposite']:
 bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.camera=bpy.data.objects[name];s.render.filepath=str(R/f'material_{name.lower()}.png');bpy.ops.render.render(write_still=True)
print('PHOENIX_WINDOW_V3_COMPLETE',flush=True)
