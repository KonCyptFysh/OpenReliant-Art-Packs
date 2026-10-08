from pathlib import Path
import bpy,json,hashlib,shutil
D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/kanji_v3'
A=Path('/home/lva-8700/.codex/.chatgpt-projects/g-p-6ac04f0d792c8191903a4b87653b44f6/work/release-preparation/repositories/OpenReliant-Art-Packs/Alliance Fighters/Sai')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=json.loads((W/'scene_validation.json').read_text());scene=Path(r['scene']);assert sha(scene)==r['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
def signature():
 data=[]
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  m=o.data;data.append({'name':o.name,'matrix':[list(x) for x in o.matrix_world],'vertices':[list(v.co) for v in m.vertices],'faces':[(list(p.vertices),p.material_index) for p in m.polygons],'normals':[list(n.vector) for n in m.corner_normals],'uvs':{u.name:[list(q.uv) for q in u.data] for u in m.uv_layers},'active_uv':m.uv_layers.active.name})
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
assert signature()==r['mesh_signature'];resources=A/'source/resources';images=[]
for im in bpy.data.images:
 if im.type!='IMAGE' or im.source!='FILE' or not im.users:continue
 path=Path(bpy.path.abspath(im.filepath));assert path.exists();digest=sha(path);dest=resources/(digest[:12]+'_'+path.name)
 if not dest.exists():shutil.copy2(path,dest)
 assert sha(dest)==digest
 if not im.packed_file:im.pack()
 assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==digest
 im.filepath='//resources/'+dest.name;images.append({'image':im.name,'resource':im.filepath,'sha256':digest,'packed_matches_source':True})
snapshot=A/'source/sai_worn_pbr_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(snapshot),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(snapshot));s=bpy.context.scene;assert signature()==r['mesh_signature']
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users:
  assert im.filepath.startswith('//resources/') and im.packed_file,(im.name,im.filepath);assert Path(bpy.path.abspath(im.filepath)).exists();assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==sha(bpy.path.abspath(im.filepath))
report={'canonical_scene':str(scene),'canonical_sha256':sha(scene),'snapshot':str(snapshot),'snapshot_sha256':sha(snapshot),'geometry_uv_normals_material_assignments_unchanged':True,'mesh_signature':r['mesh_signature'],'images':images,'packed_relative_resources_reopened':True}
(W/'repository_snapshot.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2('/tmp/sai-kanji-scene-v3.py',W/'update-scene.py');shutil.copy2(__file__,W/'portable-source.py');print('PORTABLE_SNAPSHOT_VERIFIED')
