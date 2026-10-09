import os
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/glass_gun_v4';R=D/'review/glass_gun_v4';M=D/'maps'
W.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();hashdata=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
src=D/'basilisk_worn_pbr_v3.blend';source_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
previous=json.loads((D/'work/nose_seam_v3/validation.json').read_text());maps=previous['maps']['hull'].copy();SIZE=4096;SCALE=SIZE/1254
meshes=[o for o in s.objects if o.type=='MESH'];before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],matrix=[list(a) for a in o.matrix_world],uvs={u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers},materials=[p.material_index for p in o.data.polygons]) for o in meshes}
paths={
'side_rear':[['M',839,35],['L',886,35],['Q',890,35,890,40],['L',890,67],['Q',890,71,885,71],['L',839,71],['Q',835,71,835,67],['L',835,40],['Q',835,35,839,35]],
'side_forward':[['M',925.2,54],['Q',925.2,51.3,928,50.2],['Q',930.1,48.9,932.7,50.4],['Q',968,66.4,990,83.5],['Q',1000,94,1005.5,103.2],['Q',1007,105.8,1004.8,105.8],['L',944.5,105.8],['Q',943.5,105.7,942.5,104.7],['L',926.5,90.4],['Q',925.2,89,925.2,86.5],['L',925.2,54]],
'roof_rear':[['M',847,350],['L',880,350],['Q',887,350,887,357],['L',887,398],['Q',887,404,880,404],['L',847,404],['Q',842,404,842,399],['L',842,357],['Q',842,350,847,350]],
'roof_forward':[['M',852,443],['L',876,443],['Q',887,443,887,454],['L',887,547],['Q',887,558,876,558],['L',852,558],['Q',842,558,842,547],['L',842,454],['Q',842,443,852,443]]}
(W/'glass_paths.json').write_text(json.dumps(dict(coordinate_resolution=1254,paths=paths,source='Existing amber pane inner borders, traced from current v2 base colour; artwork unchanged'),indent=2)+'\n')
def read(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(h,w,4)[::-1].copy()
def save(a,name,key,bind=False):
 h,w=a.shape[:2];v=np.ones((h,w,4),np.float32);v[:,:,:3]=a[:,:,:3] if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Basilisk '+name+' '+key+' v4',w,h,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(v[::-1]).ravel());path=M/f'basilisk_{name}_{key}_v4.png';im.filepath_raw=str(path);im.file_format='PNG';im.save();bpy.data.images.remove(im)
 rec=dict(path=str(path),sha256=sha(path),dimensions=[w,h]);im=None
 if bind:
  im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack()
 return rec,im

def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def flatten(cmds):
 pts=[]
 for cmd in cmds:
  if cmd[0] in ['M','L']:pts.append(np.array(cmd[1:],float))
  else:
   a=pts[-1].copy();b=np.array(cmd[1:3]);c=np.array(cmd[3:]);pts.extend([(1-t)**2*a+2*(1-t)*t*b+t*t*c for t in np.linspace(0,1,17)[1:]])
 return np.asarray(pts)
# Signed distance tracing keeps the curved pane contour independent of hull noise.
x0,y0,x1,y1=[round(a*SCALE) for a in (818,20,1025,570)];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/SCALE;Y=(yy+.5)/SCALE;distance=np.full(X.shape,-100,np.float32)
for name,commands in paths.items():
 p=flatten(commands);sel=(X>=p[:,0].min()-9)&(X<=p[:,0].max()+9)&(Y>=p[:,1].min()-9)&(Y<=p[:,1].max()+9);qx=X[sel];qy=Y[sel];inside=np.zeros(qx.shape,bool);dd=np.full(qx.shape,1e10)
 for a,b in zip(p,np.roll(p,-1,0)):
  e=b-a;ee=e@e
  if ee<1e-12:continue
  t=np.clip(((qx-a[0])*e[0]+(qy-a[1])*e[1])/ee,0,1);dd=np.minimum(dd,(qx-a[0]-t*e[0])**2+(qy-a[1]-t*e[1])**2)
  if abs(e[1])>1e-12:inside^=((a[1]>qy)!=(b[1]>qy))&(qx<a[0]+(qy-a[1])*e[0]/e[1])
 distance[sel]=np.maximum(distance[sel],np.sqrt(dd)*np.where(inside,1,-1))
glass=smooth(-.30,.30,distance);surround=smooth(-2.8,-2.2,distance);oldglass=read(maps['glass']['path'])[y0:y1,x0:x1,0];oldseal=read(maps['seal']['path'])[y0:y1,x0:x1,0]
footprint=np.maximum.reduce([surround,oldseal,oldglass]);neutral=np.maximum(smooth(-7,-3,distance),np.maximum(oldseal,oldglass));oldrough=read(maps['roughness']['path'])[y0:y1,x0:x1,0]
diagnosis=dict(previous_roughness_on_actual_pane_percentiles=np.quantile(oldrough[glass>.99],[0,.25,.5,.75,1]).tolist(),actual_pane_texels=int((glass>.99).sum()),previous_matte_texels_inside_pane=int(((oldrough>.3)&(glass>.99)).sum()),cause='The earlier straight polygon did not follow the existing curved amber window outline; its roughness boundary crossed the painted pane.')
hull_images={}
for key in ['roughness','metallic','normal','height','glass','seal','panels','structure']:
 a=read(maps[key]['path']);q=a[y0:y1,x0:x1,:3]
 if key in ['roughness','metallic']:
  q[:]=q*(1-footprint[:,:,None])+(.83 if key=='roughness' else 0)*footprint[:,:,None];q[:]=q*(1-glass[:,:,None])+(.16 if key=='roughness' else 0)*glass[:,:,None]
 elif key=='normal':
  q[:]=q*(1-neutral[:,:,None])+np.array([.5,.5,1])*neutral[:,:,None];n=q*2-1;n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8);q[:]=n*.5+.5
 elif key=='height':q[:]=q*(1-neutral[:,:,None])+(8/12)*neutral[:,:,None]
 elif key=='glass':q[:]=glass[:,:,None]
 elif key=='seal':q[:]=surround[:,:,None]
 else:q[:]=q*(1-footprint[:,:,None])
 maps[key],im=save(a,'hull',key,key in ['roughness','metallic','normal'])
 if im:hull_images[key]=im
edit=np.zeros((SIZE,SIZE),np.float32);edit[y0:y1,x0:x1]=np.maximum(footprint,neutral);maps['glazing_edit_mask'],_=save(edit,'hull','glazing_edit_mask')
# A compact separate tile avoids changing any other mesh that reuses these UVs.
selected=[189,190,191,192,219,220,221,222];bx,by,tile=768,3392,512;gunmaps={};gun_images={}
paint=read(maps['paint']['path'])[by:by+tile,bx:bx+tile,0];panels=read(maps['panels']['path'])[by:by+tile,bx:bx+tile,0];structure=read(maps['structure']['path'])[by:by+tile,bx:bx+tile,0];flat=read(maps['flat_graphics']['path'])[by:by+tile,bx:bx+tile,0];control=1-np.maximum.reduce([panels,structure,flat]);newrough=None
for key in ['basecolor','roughness','metallic','normal']:
 a=read(maps[key]['path'])[by:by+tile,bx:bx+tile].copy()
 if key=='roughness':a[:,:,:3]=a[:,:,:3]*(1-control[:,:,None])+(.33+.07*paint)[:,:,None]*control[:,:,None];newrough=a[:,:,0].copy()
 if key=='normal':
  n=a[:,:,:3]*2-1;n[:,:,:2]*=1-.55*control[:,:,None];n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8);a[:,:,:3]=n*.5+.5
 gunmaps[key],gun_images[key]=save(a,'gun',key,True)
gunmaps['finish_mask'],_=save(control,'gun','finish_mask')
hull=bpy.data.objects['Basalisk'].data.materials[0];hull.name='Basilisk_Worn_hull_PBR_v4'
for key,im in hull_images.items():hull.node_tree.nodes['Delivered '+key].image=im
gun=hull.copy();gun.name='Basilisk_Worn_forward_gun_PBR_v4'
for key,im in gun_images.items():gun.node_tree.nodes['Delivered '+key].image=im
for node in list(gun.node_tree.nodes):
 if node.type=='TEX_IMAGE' and node.name.startswith('Authoring'):gun.node_tree.nodes.remove(node)
gun['matching_nose_roughness']='bare .33, paint .40';gun['normal_relief_scale']=.45;gun['original_atlas_crop']=json.dumps([bx,by,tile,tile])
o=bpy.data.objects['Basalisk'];slot=len(o.data.materials);o.data.materials.append(gun);uv=o.data.uv_layers.active;edits=[]
for fi in selected:
 p=o.data.polygons[fi];old=[list(uv.data[i].uv) for i in p.loop_indices];p.material_index=slot
 for i in p.loop_indices:
  u,v=uv.data[i].uv;uv.data[i].uv=((u*SIZE-bx)/tile,1-((1-v)*SIZE-by)/tile)
 edits.append(dict(part=o.name,face=fi,vertices=list(p.vertices),before=old,after=[list(uv.data[i].uv) for i in p.loop_indices],native_material=1,blender_material=slot))
for ob in meshes:
 b=before[ob.name];assert b['vertices']==[list(v.co) for v in ob.data.vertices] and b['faces']==[list(p.vertices) for p in ob.data.polygons] and b['normals']==[list(n.vector) for n in ob.data.corner_normals]
 for u in ob.data.uv_layers:
  for p in ob.data.polygons:
   if ob==o and u==uv and p.index in selected:continue
   if not (ob==o and p.index in selected):assert b['materials'][p.index]==p.material_index
   for i in p.loop_indices:assert b['uvs'][u.name][i]==list(u.data[i].uv)
models={ob.name:dict(part_index=previous['models'][ob.name]['part_index'],vertices=[list(v.co) for v in ob.data.vertices],faces=[dict(id=p.index,vertices=list(p.vertices),uv=[list(ob.data.uv_layers.active.data[i].uv) for i in p.loop_indices],material=p.material_index) for p in ob.data.polygons]) for ob in meshes}
scene=D/'basilisk_worn_pbr_v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_sha
r=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=sha(scene),maps={'hull':maps,'gun':gunmaps},models=models,uv_repairs=edits,geometry_normals_and_transforms_unchanged=True,base_colour_artwork_unchanged=True,previous_seam_and_machinery_uv_repairs_preserved=True,gun_material_faces=selected,gun_tile=[bx,by,tile,tile],gun_material_roughness={'bare':.33,'paint':.40},gun_normal_relief=.45,gun_roughness_median=float(np.median(newrough[control>.99])),glazing_diagnosis=diagnosis,glass_roughness=.16,glass_metallic=0,glass_paths=str(W/'glass_paths.json'),runtime_visual_review='pending_user_review')
(W/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('BASILISK_V4_SAVED',json.dumps(diagnosis),flush=True)
# Authoring checks: full nose on both sides plus the roof and grazing pane.
s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=16
cam=s.camera;cam.data.type='ORTHO'
for name,local,offset,span in [('nose_right',(8.7,35,411),(2.5,3.6,1.4),1.25),('nose_left',(8.7,35,411),(-2.5,3.6,1.4),1.25),('canopy_grazing',(8.7,-90,250),(3,1.5,.35),.82),('canopy_roof',(8.7,-90,250),(0,.7,3),1.0)]:
 target=o.matrix_world@Vector(local);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span;s.camera=cam;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('BASILISK_V4_AUTHORING_VIEWS_COMPLETE',flush=True)
