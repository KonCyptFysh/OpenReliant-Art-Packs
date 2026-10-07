"""Export edited delivery UVs from a current scene, preserving native geometry and metadata.
Blender --background --python export_scene.py -- scene.blend native-directory output-directory
Geometry/topology changes are rejected explicitly rather than silently discarded.
"""
import bpy,sys,json,struct,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import ordnance_native as n
scene,native,out=map(Path,sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(scene));out.mkdir(parents=True,exist_ok=True);bpy.context.view_layer.update();records=[]
for file in sorted(native.glob('*.SHP')):
 raw=file.read_bytes();parts=n.models(raw)
 for p in parts:
  found=[o for o in bpy.data.objects if o.type=='MESH' and o.get('native_model')==file.name and o.get('native_part')==p['part'] and o.get('native_lod')==p['lod']];assert len(found)==1,(file,p['part'],p['lod']);o=found[0];mesh=o.data
  assert np.array_equal(np.array([list(v.co) for v in mesh.vertices]),p['verts']),'Geometry changed: use a reviewed geometry exporter'
  assert len(mesh.polygons)==len(p['faces']);uv=mesh.uv_layers['Ordnance_Delivery_UV_v1'];orders=o['native_corner_order'];p['new_uv']={}
  for f in p['faces']:
   poly=mesh.polygons[f['id']];qs=np.zeros((3,2))
   assert len(poly.vertices)==3
   for k,li in enumerate(poly.loop_indices):
    corner=orders[li];assert poly.vertices[k]==f['indices'][corner],'Topology changed';u,v=uv.data[li].uv;qs[corner]=(u,1-v)
   p['new_uv'][f['id']]=np.array(f['uv']) if np.max(np.abs(qs-np.array(f['uv'])))<1e-7 else qs
  assert np.array_equal(np.array([list(v.vector) for v in mesh.attributes['NativeVertexNormal'].data]),p['normals'])
  for v,baseline in zip(mesh.corner_normals,mesh.attributes['ImportedCornerNormal'].data):
   assert np.linalg.norm(np.array(v.vector)-baseline.vector)<1e-6,'Custom normals changed; use a reviewed normal exporter'
 records.append(dict(file=file.name,**n.export(raw,parts,out/file.name)))
(out/'scene_export.json').write_text(json.dumps(records,indent=2));print('SCENE_EXPORT_COMPLETE',len(records),flush=True)
