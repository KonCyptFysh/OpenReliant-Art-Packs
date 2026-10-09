import os
from pathlib import Path
import bpy,numpy as np,json,hashlib,shutil,math
D=Path(str(Path(os.environ['LOKI_WORKSPACE'])));P=D/'work/reconstruction_v1';W=D/'work/window_recess_v1';M=D/'maps';V=D/'review/window_recess_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=json.loads((D.parent/'project_state.json').read_text());scene=Path(state['latest_scene']);prior=json.loads((P/'validation.json').read_text());assert sha(scene)==prior['scene_sha256']
W.mkdir(parents=True,exist_ok=True);V.mkdir(parents=True,exist_ok=True);B=W/'before';B.mkdir(exist_ok=True)
for p in [scene,P/'validation.json',P/'repository_snapshot.json',D.parent/'project_state.json']:shutil.copy2(p,B/p.name)
for name in ['normal','height']:shutil.copy2(prior['maps']['hull'][name]['path'],B/Path(prior['maps']['hull'][name]['path']).name)
bpy.ops.wm.open_mainfile(filepath=str(scene));bpy.context.preferences.filepaths.save_version=0
# Preserve the complete current geometry, UVs, hierarchy, custom normals and keyed poses.
def signature():
 objects=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name);data=[]
 for o in objects:
  m=o.data;data.append(dict(name=o.name,parent=o.parent.name if o.parent else None,vertices=[list(v.co) for v in m.vertices],faces=[(list(p.vertices),p.material_index) for p in m.polygons],normals=[list(n.vector) for n in m.corner_normals],uv={u.name:[list(q.uv) for q in u.data] for u in m.uv_layers}))
 for frame in [1,25,51,75,101]:
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();data.append({o.name:[list(row) for row in o.matrix_world] for o in objects})
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before_sig=signature();N=1254;OUT=4096;ratio=OUT/N;yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
reg=json.loads((P/'regions.json').read_text())['regions']['glass']
def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def poly(p):
 p=np.asarray(p);d=np.full((N,N),1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
signed=np.maximum.reduce([poly(p) for p in reg])
# The rim is at zero; the pane is below it. All slope lies in the existing frame/seal,
# reaching a constant flat depth at the glass edge. No raised rim is added.
depth=2.0;width=6.0;h=-depth*smooth(-width,0,signed)
# A short symmetric filter rounds the traced corners without shifting the window outline.
for axis in (0,1):h=(np.roll(h,2,axis)+4*np.roll(h,1,axis)+6*h+4*np.roll(h,-1,axis)+np.roll(h,-2,axis))/16
# Force a flat pane and bound the editable region to eight original-atlas pixels around the frame.
h[signed>=2]=-depth;h[signed<=-8]=0
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
normal[(signed>=2)|(signed<=-8)]=(0,0,1)

def resize(array):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=array if array.ndim==3 else array[:,:,None]
 im=bpy.data.images.new('Temporary recess data',N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 buf=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(buf);out=buf.reshape(OUT,OUT,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return out

def read_image(path):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';buf=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(buf);array=buf.reshape(OUT,OUT,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return array

def save_image(array,key):
 rgba=np.ones((OUT,OUT,4),np.float32);rgba[:,:,:3]=array if array.ndim==3 else array[:,:,None];im=bpy.data.images.new('Loki recessed glass '+key,OUT,OUT,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());p=M/f'loki_hull_{key}_v1_1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);return dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT])
# Keep every unrelated normal texel byte-for-byte, and only replace the bevel band.
old=read_image(prior['maps']['hull']['normal']['path']);nn=resize(normal*.5+.5)*2-1;nn/=np.maximum(np.linalg.norm(nn,axis=-1,keepdims=True),1e-8)
region=resize(((signed>-9)&(signed<3)).astype(np.float32))[:,:,0]>.001
edited=old.copy();edited[region]=(nn*.5+.5)[region]
height=read_image(prior['maps']['hull']['height']['path'])[:,:,0];delta=resize(h)[:,:,0];height+=delta/8
normal_record=save_image(edited,'normal');height_record=save_image(height,'height');mask_record=save_image(region.astype(np.float32),'window_recess_mask')
# Read-back validates normalization and exact scope independently of scene shading.
result=read_image(normal_record['path']);assert np.max(np.abs(result[~region]-old[~region]))<1/65536
lens=np.linalg.norm(result*2-1,axis=-1);assert float(np.max(np.abs(lens-1)))<.02
pane=resize((signed>=3).astype(np.float32))[:,:,0]>.999;assert np.max(np.abs(result[pane]-[128/255,128/255,1]))<1/65536
# Analytical edge samples: bevel normals point into the opening on both opposing edges.
assert normal[45,27,0]>.1 and normal[45,421,0]<-.1
assert normal[10,200,1]<-.1 and normal[94,200,1]>.1
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.name=='Delivered normal':
   im=bpy.data.images.load(normal_record['path'],check_existing=False);im.colorspace_settings.name='Non-Color';im.pack();node.image=im
assert signature()==before_sig
s=bpy.context.scene;s.frame_set(1);s.camera=bpy.data.objects['Front'];bpy.ops.wm.save_as_mainfile(filepath=str(scene))
r=prior.copy();r.update(scene=str(scene),scene_sha256=sha(scene),asset_revision='1.1',window_recess=dict(height_at_rim=0,height_at_pane=-depth,bevel_width_master_pixels=width,affected_windows=len(reg),glass_interior_flat=True,geometry_uv_animation_signature=before_sig,unrelated_normal_texels_unchanged=True),runtime_visual_validation='pending_user_review')
r['maps']['hull'].update(normal=normal_record,height=height_record,window_recess_mask=mask_record)
(W/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
(W/'recess-regions.json').write_text(json.dumps(dict(coordinate_resolution=N,window_polygons=reg,depth=depth,width=width,profile='Negative smoothstep from frame to inset plane; inward bevel normals',normal_max_unit_error=float(np.max(np.abs(lens-1))),unrelated_texels_unchanged=True),indent=2)+'\n')
print('LOKI_RECESSED_WINDOWS_VERIFIED',flush=True)
# Authoring close-ups use existing cameras. Native-game captures are left to user review.
from mathutils import Vector
body=bpy.data.objects['Loki Body'];target=body.matrix_world@Vector((0,-75,235))
for name in ['Front','Opposite']:
 s.camera=bpy.data.objects[name];cam=s.camera;old_loc=cam.location.copy();old_rot=cam.rotation_euler.copy();old_lens=cam.data.lens
 cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=115
 s.render.filepath=str(V/f'windows_{name.lower()}.png');bpy.ops.render.render(write_still=True)
 cam.location=old_loc;cam.rotation_euler=old_rot;cam.data.lens=old_lens
