import os
import bpy, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['PHOENIX_WORKSPACE'])
W=D/'work/audit_v2';R=D/'review/audit_v2'
W.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
state=json.loads((D.parent/'project_state.json').read_text());bpy.ops.wm.open_mainfile(filepath=state['latest_scene'])
s=bpy.context.scene;cam=s.camera;cam.location=(0,.18,-8);cam.rotation_euler=(Vector((0,.18,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.6
s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.cycles.samples=16;s.render.filepath=str(R/'belly_before.png')
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();labels=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 for p in ob.data.polygons:
  if p.material_index!=0:continue
  c=ob.matrix_world@p.center;start=Vector((c.x,c.y,-8));direct=Vector((0,0,1));hit,loc,n,idx,obj,matrix=s.ray_cast(dg,start,direct)
  if hit and obj.name==ob.name and idx==p.index:
   q=world_to_camera_view(s,cam,c);labels.append({'object':ob.name,'id':p.index,'xy':[q.x*1400,(1-q.y)*1400]})
(W/'belly_labels.json').write_text(json.dumps(labels))
bpy.ops.render.render(write_still=True)
