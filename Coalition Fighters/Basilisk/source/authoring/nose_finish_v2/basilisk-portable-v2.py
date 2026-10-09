import os
from pathlib import Path
import bpy,json,hashlib,shutil
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/nose_finish_v2'
A=Path(os.environ['ART_PACK_REPOSITORY']).resolve()/'Coalition Fighters/Basilisk'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());scene=Path(r['scene']);assert sha(scene)==r['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(scene));bpy.context.preferences.filepaths.save_version=0
def signature():
    data={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uv={u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers},matrix=[list(row) for row in o.matrix_world]) for o in bpy.context.scene.objects if o.type=='MESH'}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before=signature();assert before==r['geometry_signature']
resources=A/'source/resources';resources.mkdir(parents=True,exist_ok=True);images=[]
for im in bpy.data.images:
    if im.type!='IMAGE' or im.source!='FILE' or not im.users:continue
    p=Path(bpy.path.abspath(im.filepath));assert p.is_file();digest=sha(p);dest=resources/(digest[:12]+'_'+p.name);shutil.copy2(p,dest)
    if not im.packed_file:im.pack()
    assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==digest
    im.filepath='//resources/'+dest.name;images.append(dict(image=im.name,path=im.filepath,sha256=digest))
snapshot=A/'source/basilisk_worn_pbr_v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(snapshot),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(snapshot));assert signature()==before
for im in bpy.data.images:
    if im.type=='IMAGE' and im.source=='FILE' and im.users:
        assert im.filepath.startswith('//resources/') and im.packed_file
        assert sha(bpy.path.abspath(im.filepath))==hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
assert sha(scene)==r['scene_sha256']
report=dict(canonical_scene=str(scene),canonical_sha256=sha(scene),snapshot=str(snapshot),snapshot_sha256=sha(snapshot),mesh_signature=before,geometry_uv_normals_material_assignments_unchanged=True,packed_relative_resources_reopened=True,images=images)
(W/'repository_snapshot.json').write_text(json.dumps(report,indent=2)+'\n');print('BASILISK_V2_PORTABLE_VERIFIED')
