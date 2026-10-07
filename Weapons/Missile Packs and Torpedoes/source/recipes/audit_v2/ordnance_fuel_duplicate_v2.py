import os
import bpy,json
from pathlib import Path
D=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve();bpy.ops.wm.open_mainfile(filepath=str(D/'ordnance_worn_audit_v2.blend'));ob=next(o for o in bpy.data.objects if o.type=='MESH' and o.get('native_model')=='31_fuel_pod.SHP' and o.get('native_lod')==0);assert len(ob.data.polygons)==74;ob['native_suppressed_duplicate_faces']=[0,1];hidden=next(i for i,m in enumerate(ob.data.materials) if m.name=='Original hidden damage caps')
for i in [0,1]:ob.data.polygons[i].material_index=hidden
bpy.context.scene['fuel_pod_duplicate_fix']='31_fuel_pod LOD0 faces 0/1 overlap the correctly mapped faces 2/73. The duplicate records are retained as hidden caps; matching in-flight panel remains visible. No vertex, normal, attachment or animation records change.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'ordnance_worn_audit_v2.blend'),compress=True)
p=D/'work/audit_v2/uv_repairs.json';v=json.loads(p.read_text());v.append(dict(file='31_fuel_pod.SHP',part=0,lod=0,repair='suppress duplicate coplanar cover faces, keep shared flight upper panel',faces=[0,1],retained_visible_faces=[2,73]));p.write_text(json.dumps(v,indent=2));print('DUPLICATE_FUEL_PANEL_SUPPRESSED',flush=True)
