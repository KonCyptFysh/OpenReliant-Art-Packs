import os
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v6';R=D/'review/audit_v6';M=D/'maps';S=4096
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((D.parent/'project_state.json').read_text());src=Path(state['latest_scene']);assert src.name=='phoenix_worn_pbr_v5.blend';source_sha=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update()
old=json.loads((D/'work/audit_v5/validation.json').read_text());base=json.loads((D/'work/reconstruction_v1/validation.json').read_text());paths=json.loads((W/'frame_paths.json').read_text());newuv='Phoenix_Delivery_UV_v6'
before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uvs={u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers}) for o in s.objects if o.type=='MESH'}
for o in s.objects:
 if o.type=='MESH':
  u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True

def read(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);a=a.reshape(S,S,4)[::-1].copy();bpy.data.images.remove(im);return a

def save(a,key,bind=False):
 im=bpy.data.images.new('Phoenix v6 '+key,S,S,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());p=M/f'phoenix_worn_{key}_4k_v6.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if key=='basecolor' else '16';im.save();bpy.data.images.remove(im)
 if bind:
  im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack()
  for mat in bpy.data.materials:
   if mat.use_nodes:
    for n in mat.node_tree.nodes:
     if n.type=='TEX_IMAGE' and n.name=='Delivered '+key:n.image=im
 return {'path':str(p),'sha256':sha(p)}

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def flatten(cmds):
 pts=[]
 for cmd in cmds:
  if cmd[0] in ('M','L'):pts.append(np.array(cmd[1:],dtype=float))
  else:
   start=pts[-1].copy();ctrl=np.array(cmd[1:3]);end=np.array(cmd[3:]);
   for t in np.linspace(0,1,17)[1:]:pts.append((1-t)**2*start+2*(1-t)*t*ctrl+t*t*end)
 if np.linalg.norm(pts[0]-pts[-1])<1e-6:pts.pop()
 return np.array(pts)
scale=S/1254;box=(535,565,1250,755);x0,y0,x1,y1=[int(round(v*scale)) for v in box];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/scale;Y=(yy+.5)/scale
distance=np.full(X.shape,-100.,np.float32);outlines=[]
for name,cmds in paths['paths'].items():
 p=flatten(cmds);outlines.append({'name':name,'glass_outline':p.tolist()});bounds=[p[:,0].min()-10,p[:,1].min()-10,p[:,0].max()+10,p[:,1].max()+10];selected=(X>=bounds[0])&(X<=bounds[2])&(Y>=bounds[1])&(Y<=bounds[3]);qx=X[selected];qy=Y[selected];inside=np.zeros(qx.shape,bool);dd=np.full(qx.shape,1e10)
 for a,b in zip(p,np.roll(p,-1,0)):
  e=b-a;ee=e@e
  if ee<1e-12:continue
  t=np.clip(((qx-a[0])*e[0]+(qy-a[1])*e[1])/ee,0,1);dd=np.minimum(dd,(qx-a[0]-t*e[0])**2+(qy-a[1]-t*e[1])**2)
  if abs(e[1])>1e-12:inside^=((a[1]>qy)!=(b[1]>qy))&(qx<a[0]+(qy-a[1])*e[0]/e[1])
 distance[selected]=np.maximum(distance[selected],np.sqrt(dd)*np.where(inside,1,-1))
glass=smooth(-.28,.28,distance);surround=smooth(-2.8,-2.2,distance);seal=np.maximum(surround-glass,0)
oldglass=read(Path(old['maps']['glass']['path']))[y0:y1,x0:x1,0];oldseal=read(Path(old['maps']['seal']['path']))[y0:y1,x0:x1,0]
footprint=np.maximum(np.maximum(oldglass,oldseal),surround)
# Neutral normals across both pane and gasket, with a wide soft transition
# confined to the outside of the gasket. This removes the former one-pixel
# height-derived ridges while keeping every native corner normal unchanged.
normal_mask=np.maximum(smooth(-7.,-3.0,distance),np.maximum(oldglass,oldseal))
previous_normal=read(Path(old['maps']['normal']['path']))[y0:y1,x0:x1,:3]*2-1
norm=np.linalg.norm(previous_normal,axis=2);angles=np.rad2deg(np.arccos(np.clip(previous_normal[:,:,2]/norm,-1,1)));edge=(oldglass>.01)&(oldglass<.999);diagnosis={'previous_glass_normal_max_degrees':float(angles[oldglass>.99].max()),'previous_edge_normal_max_degrees':float(angles[edge].max()),'new_glass_normal':'exactly planar tangent normal across full pane and gasket','new_glass_roughness':.16}
print('REFLECTION_DIAGNOSIS',json.dumps(diagnosis),flush=True)
maps=dict(old['maps'])
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=read(Path(old['maps'][key]['path']));q=a[y0:y1,x0:x1,:3].copy()
 if key=='basecolor':
  original=read(Path(base['maps'][key]['path']))[y0:y1,x0:x1,:3];q=original*(1-glass[:,:,None])+np.array([.11,.17,.145])*glass[:,:,None]
 elif key in ['roughness','metallic']:
  # A matte nonmetallic gasket has the same outline as the optical mask.
  q=q*(1-footprint[:,:,None])+(.86 if key=='roughness' else 0)*footprint[:,:,None]
  q=q*(1-glass[:,:,None])+(.16 if key=='roughness' else 0)*glass[:,:,None]
 elif key=='normal':
  q=q*(1-normal_mask[:,:,None])+np.array([.5,.5,1])*normal_mask[:,:,None]
 elif key=='glass':q=glass[:,:,None]+np.zeros_like(q)
 elif key=='seal':q=seal[:,:,None]+np.zeros_like(q)
 elif key=='height':q=q*(1-normal_mask[:,:,None])+((20-.32)/32)*normal_mask[:,:,None]
 elif key=='structure':q=q*(1-footprint[:,:,None])+seal[:,:,None]*footprint[:,:,None]
 else:q=q*(1-footprint[:,:,None])
 a[y0:y1,x0:x1,:3]=q;maps[key]=save(a,key,key in ['basecolor','roughness','metallic','normal'])
mask=np.zeros((S,S,4),np.float32);mask[:,:,3]=1;mask[y0:y1,x0:x1,:3]=normal_mask[:,:,None];edit_record=save(mask,'frame_glazing_edit_mask')
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   if n.type in ['UVMAP','NORMAL_MAP'] and n.uv_map=='Phoenix_Delivery_UV_v5':n.uv_map=newuv
models={}
for name,b in before.items():
 m=bpy.data.objects[name].data
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals]
 assert all(v==[list(q.uv) for q in m.uv_layers[k].data] for k,v in b['uvs'].items())
 models[name]={'vertices':b['vertices'],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
 assert models[name]==old['models'][name]
scene=D/'phoenix_worn_pbr_v6.blend';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_sha
report=dict(old);report.update(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,maps=maps,models=models,audit_changes={'window_outlines_source':'Manually traced original inner frame boundaries with smooth quadratic corners, including dark glass','panes':outlines,'physical_glass_panes':10,'original_frames_and_surrounding_colours_preserved':True,'native_geometry_and_uvs_equal_v5':True,'glass_tint_srgb':[.11,.17,.145],'glass_roughness':.16,'glass_metallic':0,'reflection_diagnosis':diagnosis,'edit_mask':edit_record,'edit_bounds_atlas':box},runtime_visual_validation='Frame-fitted glass and flat pane normals; final game review pending')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
cam=s.camera;target=Vector((0,1.22,.20));s.render.resolution_x=1200;s.render.resolution_y=760
for name,offset,span in [('canopy_right',(1.5,.18,.62),1.22),('canopy_left',(-1.5,.18,.62),1.22),('canopy_roof',(0,0,2),1.20),('canopy_grazing',(1.5,-.42,.25),1.22)]:
 cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=span;s.camera=cam;s.render.filepath=str(R/f'{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.camera=bpy.data.objects['Front'];s.render.filepath=str(R/'material_front.png');bpy.ops.render.render(write_still=True)
print('PHOENIX_FRAME_GLAZING_V6_COMPLETE',flush=True)
