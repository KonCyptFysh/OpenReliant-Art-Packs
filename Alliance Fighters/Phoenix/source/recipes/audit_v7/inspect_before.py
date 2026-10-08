import os
import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v7';R=D/'review/audit_v7/before';W.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
state=json.loads((D.parent/'project_state.json').read_text());assert state['latest_scene'].endswith('_v6.blend');bpy.ops.wm.open_mainfile(filepath=state['latest_scene']);s=bpy.context.scene;bpy.context.view_layer.update();out={}
for o in s.objects:
 if o.type!='MESH':continue
 m=o.data;vs=np.array([list(o.matrix_world@v.co) for v in m.vertices]);fs=[]
 for p in m.polygons:
  pp=vs[list(p.vertices)];n=np.cross(pp[1]-pp[0],pp[2]-pp[0]);n/=max(np.linalg.norm(n),1e-9)
  fs.append({'id':p.index,'vertices':list(p.vertices),'material':p.material_index,'center':pp.mean(0).tolist(),'normal':n.tolist(),'uv':[list(m.uv_layers.active.data[i].uv) for i in p.loop_indices]})
 out[o.name]={'vertices':vs.tolist(),'local_vertices':[list(v.co) for v in m.vertices],'faces':fs,'matrix':[list(row) for row in o.matrix_world]}
(W/'mesh_v6.json').write_text(json.dumps(out,indent=2));(W/'prior_project_state.json').write_text(json.dumps(state,indent=2))
views=[('whole',(0,0,.05),(4,5,3),3.5),('belly',(0,-.05,-.05),(0,0,-8),3.6),('nose',(.05,1.38,.01),(1.4,1.2,.7),1.12),('vents',(.45,-.10,.19),(1.7,1.3,1.6),1.7)]
(W/'review_views.json').write_text(json.dumps(views,indent=2));cam=s.camera;cam.data.type='ORTHO';s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=12;dg=bpy.context.evaluated_depsgraph_get()
for name,target,offset,span in views:
 target=Vector(target);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span;bpy.context.view_layer.update();labels=[]
 for ob in s.objects:
  if ob.type!='MESH':continue
  for p in ob.data.polygons:
   if p.material_index==1:continue
   c=ob.matrix_world@p.center;start=c+(cam.location-target).normalized()*10;hit,loc,n,idx,obj,matrix=s.ray_cast(dg,start,(c-start).normalized())
   if hit and obj.name==ob.name and idx==p.index:
    q=world_to_camera_view(s,cam,c)
    if 0<q.x<1 and 0<q.y<1:labels.append({'object':ob.name,'id':p.index,'xy':[q.x*1600,(1-q.y)*1200]})
 (W/(name+'_labels.json')).write_text(json.dumps(labels));s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('PHOENIX_DIAGNOSTIC_COMPLETE',flush=True)
