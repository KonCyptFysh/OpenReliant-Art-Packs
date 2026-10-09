import os
from pathlib import Path
import bpy,json,hashlib,shutil
D=Path(str(Path(os.environ['KAMOV_WORKSPACE'])));W=D/'work/reconstruction_v1'
r=json.loads((W/'validation.json').read_text())
if r.get('preview_uv_check'):
 print('Preview UV correction already applied; no changes.');raise SystemExit(0)
bpy.ops.wm.open_mainfile(filepath=r['scene'])
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for u in o.data.uv_layers:
   for q in u.data:q.uv.y=1-q.uv.y
s=bpy.context.scene;s.frame_set(1);s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=r['scene'])
r['scene_sha256']=hashlib.sha256(Path(r['scene']).read_bytes()).hexdigest();r['preview_uv_check']='Parser UVs already use Blender V convention; all scene UVs checked directly against native parsed faces.'
meta=json.loads((D/'source/native_parts.json').read_text())
for o in s.objects:
 if o.type!='MESH':continue
 lod=meta[o['native_part_index']]['lods'][0]
 for face,f in zip(o.data.polygons,lod['faces']):
  for li in face.loop_indices:
   vi=o.data.loops[li].vertex_index;q=f['uv'][f['vertices'].index(vi)]
   assert max(abs(a-b) for a,b in zip(o.data.uv_layers.active.data[li].uv,q))<1e-6
(W/'validation.json').write_text(json.dumps(r,indent=2));shutil.copy2('/tmp/build-kamov-materials.py',W/'build_materials.py');shutil.copy2(__file__,W/'correct_preview_uv.py')
s.cycles.samples=16;s.render.resolution_x=1200;s.render.resolution_y=900
for name,frame in [('Front',1),('Opposite',1),('Belly',101)]:
 s.frame_set(frame);s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
