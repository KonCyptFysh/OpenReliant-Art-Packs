import os
from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/nose_seam_v3';R=D/'review/nose_seam_v3'
W.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'basilisk_worn_pbr_v2.blend';before_hash=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
mesh=lambda:{o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],matrix=[list(r) for r in o.matrix_world],materials=[m.name if m else None for m in o.data.materials]) for o in s.objects if o.type=='MESH'}
hashdata=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
geom=hashdata(mesh());old_uv={o.name:{u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers} for o in s.objects if o.type=='MESH'}
edits=[];selection={'Basalisk':[226,227,228,229],'Basalisk_Cpit':[27,28]};edge_records={};allowed={}
# Keep the left edge and vertical panel registration; inset only the atlas edge
# which crosses the neighboring red-painted recess. This is a shared front
# island spanning both sides, not a mesh or texture repaint.
new_right=.76875
for name,faces in selection.items():
 o=bpy.data.objects[name];uv=o.data.uv_layers.active
 left=min(uv.data[i].uv.x for f in faces for i in o.data.polygons[f].loop_indices);old_right=max(uv.data[i].uv.x for f in faces for i in o.data.polygons[f].loop_indices)
 edge_records[name]={'left':left,'before_right':old_right,'after_right':new_right}
 for f in faces:
  p=o.data.polygons[f];old=[list(uv.data[i].uv) for i in p.loop_indices]
  for i in p.loop_indices:uv.data[i].uv.x=left+(uv.data[i].uv.x-left)*(new_right-left)/(old_right-left)
  edits.append(dict(part=o.name,face=f,vertices=list(p.vertices),before=old,after=[list(uv.data[i].uv) for i in p.loop_indices]))
 allowed[name]={i for f in faces for i in o.data.polygons[f].loop_indices}
for obj in s.objects:
 if obj.type!='MESH':continue
 for u in obj.data.uv_layers:
  for i,x in enumerate(u.data):
   if u==obj.data.uv_layers.active and i in allowed.get(obj.name,set()):continue
   assert list(x.uv)==old_uv[obj.name][u.name][i]
assert geom==hashdata(mesh())
scene=D/'basilisk_worn_pbr_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==before_hash
models={}
prior=json.loads((D/'work/reconstruction_v1/validation.json').read_text())
for name in prior['models']:
 ob=bpy.data.objects[name];lay=ob.data.uv_layers.active
 models[name]=dict(part_index=prior['models'][name]['part_index'],vertices=[list(v.co) for v in ob.data.vertices],faces=[dict(id=p.index,vertices=list(p.vertices),uv=[list(lay.data[i].uv) for i in p.loop_indices]) for p in ob.data.polygons])
r=dict(source=str(src),source_sha256=before_hash,scene=str(scene),scene_sha256=sha(scene),geometry_signature=geom,geometry_normals_materials_and_transforms_unchanged=True,texture_maps_unchanged=True,only_six_front_island_faces_changed=True,active_uv=uv.name,uv_repairs=edits,atlas_edges=edge_records,atlas_right_edge_before=edge_records['Basalisk']['before_right'],atlas_right_edge_after=new_right,vertical_panel_registration_unchanged=True,models=models,maps=json.loads((D/'work/nose_finish_v2/validation.json').read_text())['maps'],runtime_visual_review='pending_user_review')
(W/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
# Tight authoring views, with matched cameras and lights, inspect both sides.
s.render.resolution_x=1050;s.render.resolution_y=1050;s.render.resolution_percentage=100;s.cycles.samples=24
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=1.25;target=bpy.data.objects['Basalisk'].matrix_world@Vector((8.7,35,411))
for side in [1,-1]:
 cam.location=target+Vector((2.5*side,3.6,1.4));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
 for phase in ['after']:
  for e in edits:
   obj=bpy.data.objects[e['part']];uv=obj.data.uv_layers.active
   for i,q in zip(obj.data.polygons[e['face']].loop_indices,e[phase]):uv.data[i].uv=q
  s.render.filepath=str(R/('nose_'+('right' if side==1 else 'left')+'_'+phase+'.png'));bpy.ops.render.render(write_still=True)
print('NOSE_SEAM_V3_SAVED',str(scene),flush=True)
