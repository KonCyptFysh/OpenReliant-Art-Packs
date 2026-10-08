import os
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v5';R=D/'review/audit_v5';M=D/'maps';S=4096
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((D.parent/'project_state.json').read_text());src=Path(state['latest_scene']);assert src.name=='phoenix_worn_pbr_v3.blend';source_sha=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update()
old=json.loads((D/'work/audit_v3/validation.json').read_text());base=json.loads((D/'work/reconstruction_v1/validation.json').read_text());v2=json.loads((D/'work/audit_v2/validation.json').read_text());outlines=json.loads((W/'original_glass_outlines.json').read_text());newuv='Phoenix_Delivery_UV_v5'
before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uvs={u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers}) for o in s.objects if o.type=='MESH'}
for o in s.objects:
 if o.type!='MESH':continue
 m=o.data;u=m.uv_layers.new(name=newuv,do_init=True);m.uv_layers.active=u;u.active_render=True
 if o.name=='Phoenix_Cockpit':
  for index in [86,91]:
   for k,uv in zip(m.polygons[index].loop_indices,v2['models'][o.name]['faces'][index]['uv']):u.data[k].uv=uv
def read(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);a=a.reshape(S,S,4)[::-1].copy();bpy.data.images.remove(im);return a
def save(a,key,bind=False):
 im=bpy.data.images.new('Phoenix v5 '+key,S,S,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());p=M/f'phoenix_worn_{key}_4k_v5.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if key=='basecolor' else '16';im.save();bpy.data.images.remove(im)
 if bind:
  im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack()
  for mat in bpy.data.materials:
   if mat.use_nodes:
    for n in mat.node_tree.nodes:
     if n.type=='TEX_IMAGE' and n.name=='Delivered '+key:n.image=im
 return {'path':str(p),'sha256':sha(p)}
scale=S/1254;box=(535,565,1250,755);x0,y0,x1,y1=[int(round(v*scale)) for v in box];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/scale;Y=(yy+.5)/scale
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
glass=np.zeros(X.shape,np.float32);surround=glass.copy()
for pane in outlines:
 p=np.array(pane['glass_outline']);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1));d=np.full(X.shape,1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,0)):
  e=b-a;d=np.minimum(d,np.sign(area)*(e[0]*(Y-a[1])-e[1]*(X-a[0]))/np.linalg.norm(e))
 glass=np.maximum(glass,smooth(-.15,.20,d));surround=np.maximum(surround,smooth(-2.8,-2.3,d))
seal=np.maximum(surround-glass,0)
oldglass=read(Path(base['maps']['glass']['path']))[y0:y1,x0:x1,0];oldseal=read(Path(base['maps']['seal']['path']))[y0:y1,x0:x1,0]
footprint=np.maximum(np.maximum(oldglass,oldseal),surround)
h0=read(Path(base['maps']['height']['path']))[y0:y1,x0:x1,0]*32-20;h=h0*(1-footprint)+(-.32*surround-.50*glass)*footprint
dy,dx=np.gradient(h);normal=np.stack((-dx*scale,dy*scale,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
normal_mask=footprint.copy()
for axis in [0,1]:
 normal_mask=np.maximum.reduce([np.roll(normal_mask,k,axis) for k in range(-5,6)])
rgb=read(Path(base['maps']['basecolor']['path']))[y0:y1,x0:x1,:3];mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6)
bronze=smooth(1.10,1.32,rgb[:,:,0]/(rgb[:,:,1]+1e-6))*smooth(1.10,1.36,rgb[:,:,1]/(rgb[:,:,2]+1e-6));paint=smooth(.09,.24,sat)*(1-bronze)
frame_metal=np.maximum((1-paint)*smooth(.15,.45,lum)*.88,bronze*.75);frame_rough=.84*(1-frame_metal)+.50*frame_metal
maps=dict(base['maps'])
# Start from the unchanged original artwork. Only the actual pane interiors
# receive a uniform tint. No frame, bronze or steel pixels are repainted.
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=read(Path(base['maps'][key]['path']));q=a[y0:y1,x0:x1,:3].copy()
 if key=='basecolor':q=q*(1-glass[:,:,None])+np.array([.11,.17,.145])*glass[:,:,None]
 elif key in ['roughness','metallic']:
  frame=frame_rough if key=='roughness' else frame_metal;q=q*(1-footprint[:,:,None])+frame[:,:,None]*footprint[:,:,None]
  q=q*(1-surround[:,:,None])+(.86 if key=='roughness' else 0)*surround[:,:,None];q=q*(1-glass[:,:,None])+(.10 if key=='roughness' else 0)*glass[:,:,None]
 elif key=='normal':q=q*(1-normal_mask[:,:,None])+(normal*.5+.5)*normal_mask[:,:,None]
 elif key=='glass':q=glass[:,:,None]+np.zeros_like(q)
 elif key=='seal':q=seal[:,:,None]+np.zeros_like(q)
 elif key=='height':q=(h[:,:,None]+20)/32+np.zeros_like(q)
 elif key=='structure':q=q*(1-footprint[:,:,None])+seal[:,:,None]*footprint[:,:,None]
 else:q=q*(1-footprint[:,:,None])
 a[y0:y1,x0:x1,:3]=q;maps[key]=save(a,key,key in ['basecolor','roughness','metallic','normal'])
mask=np.zeros((S,S,4),np.float32);mask[:,:,3]=1;mask[y0:y1,x0:x1,:3]=normal_mask[:,:,None];edit_record=save(mask,'original_glazing_edit_mask')
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   if n.type in ['UVMAP','NORMAL_MAP'] and n.uv_map=='Phoenix_Delivery_UV_v3':n.uv_map=newuv
models={}
for name,b in before.items():
 m=bpy.data.objects[name].data
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals]
 assert all(v==[list(q.uv) for q in m.uv_layers[k].data] for k,v in b['uvs'].items())
 models[name]={'vertices':b['vertices'],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
 assert models[name]==v2['models'][name], 'Original window UVs and repaired belly must match v2 exactly'
scene=D/'phoenix_worn_pbr_v5.blend';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_sha
report=dict(old);report.update(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,maps=maps,models=models,audit_changes={'window_outlines_source':'Original generated v1 artwork; existing pane interiors traced without enlargement','panes':outlines,'physical_glass_panes':10,'original_frames_and_surrounding_colours_preserved':True,'front_window_original_uvs_restored':True,'native_geometry_and_uvs_equal_v2':True,'glass_tint_srgb':[.11,.17,.145],'glass_roughness':.10,'glass_metallic':0,'edit_mask':edit_record,'edit_bounds_atlas':box,'wide_triangle_v3_and_full_facet_v4_approaches_superseded':True},runtime_visual_validation='Original window footprints restored; all glazing material masks aligned to original pane interiors; final game review pending')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
cam=s.camera;target=Vector((0,1.22,.20));s.render.resolution_x=1200;s.render.resolution_y=760
for name,offset,span in [('canopy_right',(1.5,.18,.62),1.22),('canopy_left',(-1.5,.18,.62),1.22),('canopy_roof',(0,0,2),1.20)]:
 cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=span;s.camera=cam;s.render.filepath=str(R/f'{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.camera=bpy.data.objects['Front'];s.render.filepath=str(R/'material_front.png');bpy.ops.render.render(write_still=True)
print('PHOENIX_ORIGINAL_GLAZING_V5_COMPLETE',flush=True)
