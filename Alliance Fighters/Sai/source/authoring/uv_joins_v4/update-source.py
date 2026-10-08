from pathlib import Path
import bpy,json,hashlib,shutil,struct
D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/uv_joins_v4'
A=Path('/home/lva-8700/.codex/.chatgpt-projects/g-p-6ac04f0d792c8191903a4b87653b44f6/work/release-preparation/repositories/OpenReliant-Art-Packs/Alliance Fighters/Sai')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();state=json.loads((D.parent/'project_state.json').read_text());prior=Path(state['latest_scene']);prior_hash=sha(prior)
bpy.ops.wm.open_mainfile(filepath=str(prior));s=bpy.context.scene;bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
def signature():
 data=[]
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  m=o.data;data.append({'name':o.name,'matrix':[list(x) for x in o.matrix_world],'vertices':[list(v.co) for v in m.vertices],'faces':[(list(p.vertices),p.material_index) for p in m.polygons],'normals':[list(n.vector) for n in m.corner_normals],'uvs':{u.name:[list(q.uv) for q in u.data] for u in m.uv_layers},'active_uv':m.uv_layers.active.name})
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before=signature();old_images={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in bpy.data.images if im.packed_file};r=json.loads((W/'validation.json').read_text())
raw=Path(r['output']).read_bytes();pos=0;part=lod=-1;names=['Sai_Nose','Sai_Low_fin','Sai_Main_body'];groups=[]
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);pos+=6;data=raw[pos:pos+size*count];pos+=size*count
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==3:
  kinds=[];remaining=[]
  for i in range(count):k,n=struct.unpack_from('<2I',data,i*size+72);kinds.append(k);remaining.append(n)
  groups.append({'part':names[part],'lod':lod,'polygon_kind':kinds,'remaining':remaining})
  if lod==0:
   o=bpy.data.objects[names[part]];o['native_polygon_kind_v4']=kinds;o['native_polygon_remaining_v4']=remaining
text=bpy.data.texts.new('Sai_Native_Draw_Groups_v4.json');text.write(json.dumps({'source_sha256':r['output_sha256'],'levels':groups},indent=2))
s['Sai_native_export']='openreliant_v4: fan/strip groups split at UV seams; all authored UVs and artwork preserved.'
assert signature()==before;scene=D/'sai_worn_pbr_v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(prior)==prior_hash
assert old_images=={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in bpy.data.images if im.packed_file}
for im in bpy.data.images:
 if im.type!='IMAGE' or im.source!='FILE' or not im.users:continue
 path=Path(bpy.path.abspath(im.filepath));assert path.exists();digest=sha(path);dest=A/'source/resources'/(digest[:12]+'_'+path.name)
 if not dest.exists():shutil.copy2(path,dest)
 assert sha(dest)==digest;assert im.packed_file and hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==digest;im.filepath='//resources/'+dest.name
snapshot=A/'source/sai_worn_pbr_v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(snapshot),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(snapshot));s=bpy.context.scene;assert signature()==before
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users:
  assert im.filepath.startswith('//resources/') and im.packed_file;assert sha(bpy.path.abspath(im.filepath))==hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
report={'scene':str(scene),'scene_sha256':sha(scene),'prior_scene':str(prior),'prior_scene_sha256':prior_hash,'snapshot':str(snapshot),'snapshot_sha256':sha(snapshot),'geometry_uv_normals_material_assignments_and_transforms_unchanged':True,'mesh_signature':before,'packed_images_unchanged':True,'portable_snapshot_reopened':True,'native_group_metadata_stored_for_all_detail_levels':len(groups)}
(W/'source_validation.json').write_text(json.dumps(report,indent=2)+'\n');(W/'native_groups.json').write_text(json.dumps(groups,indent=2)+'\n');shutil.copy2(__file__,W/'update-source.py');print('SOURCE_V4_VERIFIED',flush=True)
