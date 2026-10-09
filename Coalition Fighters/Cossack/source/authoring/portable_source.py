from pathlib import Path
import os
import bpy,json,hashlib,shutil
D=Path(os.environ['COSSACK_WORKSPACE']).resolve();W=D/'work/reconstruction_v1'
A=Path(os.environ['ART_PACK_REPOSITORY']).resolve()/'Coalition Fighters/Cossack'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());scene=Path(r['scene']);assert sha(scene)==r['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(scene));bpy.context.preferences.filepaths.save_version=0
def signature():
 data=[]
 for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name):
  m=o.data;data.append(dict(name=o.name,matrix=[list(row) for row in o.matrix_world],vertices=[list(v.co) for v in m.vertices],faces=[(list(p.vertices),p.material_index) for p in m.polygons],normals=[list(n.vector) for n in m.corner_normals],uvs={u.name:[list(q.uv) for q in u.data] for u in m.uv_layers},active_uv=m.uv_layers.active.name))
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before=signature();resources=A/'source/resources';resources.mkdir(parents=True,exist_ok=True);images=[]
for im in bpy.data.images:
 if im.type!='IMAGE' or im.source!='FILE' or not im.users:continue
 p=Path(bpy.path.abspath(im.filepath));assert p.is_file();digest=sha(p);dest=resources/(digest[:12]+'_'+p.name);shutil.copy2(p,dest)
 if not im.packed_file:im.pack()
 assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==digest
 im.filepath='//resources/'+dest.name;images.append(dict(image=im.name,path=im.filepath,sha256=digest))
snapshot=A/'source/cossack_worn_pbr_v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(snapshot),relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(snapshot));assert signature()==before
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users:
  assert im.filepath.startswith('//resources/') and im.packed_file
  assert sha(bpy.path.abspath(im.filepath))==hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
assert sha(scene)==r['scene_sha256']
report=dict(canonical_scene=str(scene),canonical_sha256=sha(scene),snapshot=str(snapshot),snapshot_sha256=sha(snapshot),mesh_signature=before,geometry_uv_normals_material_assignments_unchanged=True,packed_relative_resources_reopened=True,images=images)
(W/'repository_snapshot.json').write_text(json.dumps(report,indent=2)+'\n');print('COSSACK_PORTABLE_SOURCE_VERIFIED')
