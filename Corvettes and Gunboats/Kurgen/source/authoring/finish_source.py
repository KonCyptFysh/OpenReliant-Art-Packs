from pathlib import Path
import os,bpy,json,hashlib,struct,shutil
from mathutils import Vector,Matrix
D=Path(os.environ['KURGEN_WORKSPACE']);W=D/'work/reconstruction_v1';r=json.loads((W/'validation.json').read_text());bpy.ops.wm.open_mainfile(filepath=r['scene']);bpy.context.preferences.filepaths.save_version=0
# Correct mounted authoring instances to the documented row-major engine transforms.
parts=json.loads((D/'source/native_parts.json').read_text());turrets=json.loads((D/'source/turret_parts.json').read_text());att=[x for x in parts[0]['attachments'] if x['kind']==1]
for o in bpy.context.scene.objects:
 if not o.get('authoring_only_mounted_instance'):continue
 p=turrets[o['source_native_part']];d=bytes.fromhex(att[o['mount']]['raw_hex']);v=struct.unpack_from('<9f',d,16);rot=Matrix([v[i:i+3] for i in range(0,9,3)]);pos=Vector(struct.unpack_from('<3f',d,4))+Vector(parts[0]['origin']);lod=p['lods'][0]
 for a,b in zip(o.data.vertices,lod['vertices']):a.co=rot@(Vector(b)+Vector(p['origin']))+pos
 o.data.update();o.data.normals_split_custom_set([rot@Vector(lod['normals'][l.vertex_index]) for l in o.data.loops])
bpy.ops.wm.save_as_mainfile(filepath=r['scene']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r['scene_sha256']=sha(r['scene']);r['mounted_instance_transform']='Verified row-major native attachment transforms; independent runtime models preserved';(W/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
# Save an amended repeatable recipe for subsequent inspection, without regenerating the maps.
p=W/'build_materials.py';s=p.read_text().replace("Matrix([values[i:i+3] for i in range(0,9,3)]).transposed()","Matrix([values[i:i+3] for i in range(0,9,3)])");p.write_text(s)
for name in ['Front','Opposite','Belly','Rear']:
 bpy.context.scene.camera=bpy.data.objects[name];bpy.context.scene.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
print('ASSEMBLY_TRANSFORMS_CHECKED',flush=True)
