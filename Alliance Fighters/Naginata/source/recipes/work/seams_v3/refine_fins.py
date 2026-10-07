from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
D=Path(__file__).resolve().parents[2];W=D/'work/seams_v3';state=json.loads((W/'prior_project_state.json').read_text());bpy.ops.wm.open_mainfile(filepath=state['latest_scene']);s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];new='Naginata_Aligned_UV_v3'
def sig():return hashlib.sha256(json.dumps({o.name:{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'normals':[list(n.vector) for n in o.data.corner_normals],'matrix':[list(r) for r in o.matrix_world],'original_uv':[list(q.uv) for q in o.data.uv_layers['Original_Naginata_UV'].data]} for o in obs},sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'naginata_worn_aligned_v3.blend'));s=bpy.context.scene;bpy.context.view_layer.update();body=bpy.data.objects['Naginata_Body'];m=body.data;verts=[body.matrix_world@v.co for v in m.vertices];mirror={i:min(range(len(verts)),key=lambda j:(verts[j]-Vector((-v.x,v.y,v.z))).length) for i,v in enumerate(verts)};byset={frozenset(p.vertices):p.index for p in m.polygons}
for layer in ['Naginata_Aligned_UV_v3','Naginata_Delivery_UV_v3']:
 uv=m.uv_layers[layer]
 for fi in range(206,276):
  if m.polygons[fi].material_index:continue
  for vi in m.polygons[fi].vertices:
   x,y,z=verts[vi]
   if fi<246:q=(1447.7+582.6*y+(abs(x)-(.802-.282*z))*3,374.9-544.5*z)
   elif 264<=fi<=270:q=(8+.82*(567.604849+582.593998*y+14)+(abs(x)-(.802+.214*z))*3,713.691091-544.480384*z)
   else:q=(1146.64603+539.439285*y+(abs(x)-(.802+.214*z))*3,8.38151964-544.480433*z)
   for face,vertex in [(fi,vi),(byset[frozenset(mirror[v] for v in m.polygons[fi].vertices)],mirror[vi])]:
    p=m.polygons[face];li=p.loop_indices[list(p.vertices).index(vertex)];uv.data[li].uv=(q[0]/1254,1-q[1]/1254)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'naginata_worn_aligned_v3.blend'))
for filename,uvname in [('bake_validation.json','Naginata_Delivery_UV_v3'),('repair_report.json','Naginata_Aligned_UV_v3')]:
 r=json.loads((W/filename).read_text());r['fin_pass']='Original steel/bronze lower-fin split retained; upper opening ceiling added to shared upper-fin chart.'
 for o in s.objects:
  if o.type=='MESH':
   for p,f in zip(o.data.polygons,r['models'][o.name]['faces']):f['uv']=[list(o.data.uv_layers[uvname].data[i].uv) for i in p.loop_indices]
 (W/filename).write_text(json.dumps(r,indent=2))
print('FIN_UVS_REFINED',flush=True)
