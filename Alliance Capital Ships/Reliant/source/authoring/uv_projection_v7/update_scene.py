import bpy,json,hashlib
from pathlib import Path
D=Path('${RELIANT_WORKSPACE}');W=D/'work/uv_projection_v7'
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v6.blend'))
def geom_hash():
 out=[]
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  if o.type=='MESH':out.append((o.name,[list(v) for v in o.matrix_world],[[*v.co] for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
 return hashlib.sha256(json.dumps(out).encode()).hexdigest()
before=geom_hash();changes=0
for r in json.loads((W/'native_repairs.json').read_text())['files'][0]['uv_changes']:
 if r['lod']!=0:continue
 obj=bpy.data.objects[r['part_name']];p=obj.data.polygons[r['face']];layer=obj.data.uv_layers.active.data
 for i in p.loop_indices:
  u,v=layer[i].uv;j=min(range(3),key=lambda j:abs(u-r['before'][j][0]/256)+abs(v-(1-r['before'][j][1]/256)))
  assert abs(u-r['before'][j][0]/256)+abs(v-(1-r['before'][j][1]/256))<1e-5
  layer[i].uv=(r['after'][j][0]/256,1-r['after'][j][1]/256);changes+=1
assert changes==12 and geom_hash()==before
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'reliant_worn_pbr_v7.blend'))
(W/'scene-validation.json').write_text(json.dumps(dict(passed=True,uv_corners_updated=changes,geometry_unchanged=True,geometry_sha256=before),indent=2)+'\n')
print('V7_SCENE_VERIFIED')
