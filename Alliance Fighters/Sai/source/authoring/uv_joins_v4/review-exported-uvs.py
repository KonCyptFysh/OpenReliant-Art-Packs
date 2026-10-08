from pathlib import Path
import bpy,json,hashlib,shutil
from mathutils import Vector

D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/uv_joins_v4';Q=D/'review/uv_joins_v4'
state=json.loads((D.parent/'project_state.json').read_text());path=Path(state['latest_scene']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();original=sha(path)
bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.context.view_layer.update()
mesh=bpy.data.objects['Sai_Nose'];points=[mesh.matrix_world@v.co for v in mesh.data.vertices];target=sum(points,Vector())/len(points)+Vector((0,-.08,.07))
data=bpy.data.cameras.new('Canopy_UV_Diagnostic');cam=bpy.data.objects.new('Canopy_UV_Diagnostic',data);s.collection.objects.link(cam);data.type='ORTHO';data.ortho_scale=1.4;s.camera=cam
s.render.resolution_x=1400;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=12
def apply_effective(name):
 native=json.loads((W/f'effective_uvs_{name}.json').read_text())
 for part,faces in native.items():
  o=bpy.data.objects[part];m=o.data;layer=m.uv_layers.active
  for record in faces:
   p=m.polygons[record['id']]
   for li in p.loop_indices:
    idx=record['vertices'].index(m.loops[li].vertex_index);u,v=record['uv'][idx];layer.data[li].uv=(u,1-v)
 for o in s.objects:
  if o.type=='MESH':o.data.update()
for label,case,x in [('canopy_before','before',2.5),('canopy_after_right','after',2.5),('canopy_after_left','after',-2.5)]:
 apply_effective(case);cam.location=target+Vector((x,4,3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(Q/f'{label}.png');bpy.ops.render.render(write_still=True);print('REVIEW_RENDER',label,flush=True)
assert sha(path)==original
report={'scene':str(path),'scene_sha256_unchanged':original,'rendering':'Local Blender renders using the per-corner UVs produced by the verified OpenReliant 0.7.0 fan/strip continuation rule. Not in-game captures.','views':['canopy_before.png','canopy_after_right.png','canopy_after_left.png'],'source_scene_modified':False,'runtime_launched':False}
(W/'local_review.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(__file__,W/'review-exported-uvs.py')
