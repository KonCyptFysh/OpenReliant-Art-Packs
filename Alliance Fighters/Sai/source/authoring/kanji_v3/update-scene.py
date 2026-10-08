from pathlib import Path
import bpy, json, hashlib, shutil
import numpy as np
from mathutils import Vector

D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/kanji_v3';Q=D/'review/kanji_v3'
A=Path('/home/lva-8700/.codex/.chatgpt-projects/g-p-6ac04f0d792c8191903a4b87653b44f6/work/release-preparation/repositories/OpenReliant-Art-Packs/Alliance Fighters/Sai')
r=json.loads((W/'placement.json').read_text());old=Path(r['prior_scene']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(old)==r['prior_scene_sha256'];bpy.ops.wm.open_mainfile(filepath=str(old));s=bpy.context.scene
def mesh_signature():
 data=[]
 for o in sorted((o for o in s.objects if o.type=='MESH'),key=lambda o:o.name):
  m=o.data;data.append({'name':o.name,'matrix':[list(x) for x in o.matrix_world],'vertices':[list(v.co) for v in m.vertices],'faces':[(list(p.vertices),p.material_index) for p in m.polygons],'normals':[list(n.vector) for n in m.corner_normals],'uvs':{u.name:[list(q.uv) for q in u.data] for u in m.uv_layers},'active_uv':m.uv_layers.active.name})
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before=mesh_signature();nodes=bpy.data.materials['Sai_Worn_sam1_PBR_v2'].node_tree.nodes;tx=nodes['Delivered basecolor'];prior_img=tx.image
image=bpy.data.images.load(r['maps']['sam1']['basecolor']['path'],check_existing=False);image.colorspace_settings.name='sRGB';image.pack();tx.image=image
if prior_img.users==0:bpy.data.images.remove(prior_img)
assert mesh_signature()==before
orientation=[]
for name,ids in [('Sai_Nose',[6,7,18,19]),('Sai_Low_fin',[25,33])]:
 o=bpy.data.objects[name];m=o.data;uv=m.uv_layers.active
 for idx in ids:
  p=m.polygons[idx];points=np.array([m.vertices[i].co[:] for i in p.vertices]);q=np.array([uv.data[i].uv[:] for i in p.loop_indices]);side='left' if q[:,0].mean()<.5 else 'right'
  deriv=np.linalg.solve(q[1:]-q[0],points[1:]-points[0]);assert deriv[1,1]<0 and deriv[0,2]*(1 if side=='right' else -1)>0
  orientation.append({'part':name,'face':idx,'side':side,'text_upward':True,'text_reads_left_to_right_from_outside':True})
s['Sai_kanji_text']='侍飛将 / 神風';s['Sai_kanji_placement']='Independent upright decals on both sides; kanji_v3 placement.json';bpy.context.preferences.filepaths.save_version=0
scene=D/'sai_worn_pbr_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(old)==r['prior_scene_sha256']
report={'scene':str(scene),'scene_sha256':sha(scene),'prior_scene':str(old),'prior_scene_sha256':sha(old),'geometry_uv_normals_transforms_and_material_assignments_unchanged':True,'mesh_signature':before,'orientation_checks':orientation,'maps':r['maps'],'runtime_visual_review':'pending_user_review','local_preview_pose':'Unanimated fin-down authoring pose; inspection mission triggers native fin-down motion.'}
(W/'scene_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('KANJI_SCENE_SAVED',flush=True)
# Two local broadside views inspect reading direction without launching game.
old_camera=s.camera;old_settings=(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.cycles.samples)
camera_data=bpy.data.cameras.new('KanjiReview');camera=bpy.data.objects.new('KanjiReview',camera_data);s.collection.objects.link(camera);camera.data.type='ORTHO';camera.data.ortho_scale=3.15
s.render.resolution_x=1800;s.render.resolution_y=1800;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.cycles.samples=16
for name,x in [('left',-7),('right',7)]:
 camera.location=(x,0,0);camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera;s.render.filepath=str(Q/f'side_{name}.png');bpy.ops.render.render(write_still=True)
s.camera=old_camera;bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(camera_data)
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.cycles.samples=old_settings
# Packed source plus relative resources for a portable, reopenable snapshot.
resources=A/'source/resources';resources.mkdir(parents=True,exist_ok=True);images=[]
for im in bpy.data.images:
 if im.type!='IMAGE' or im.source!='FILE' or not im.users:continue
 path=Path(bpy.path.abspath(im.filepath));assert path.exists();digest=sha(path);dest=resources/(digest[:12]+'_'+path.name)
 if not dest.exists():shutil.copy2(path,dest)
 assert sha(dest)==digest
 if not im.packed_file:im.pack()
 assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==digest
 im.filepath='//resources/'+dest.name;images.append({'image':im.name,'resource':im.filepath,'sha256':digest,'packed_matches_source':True})
snapshot=A/'source/sai_worn_pbr_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(snapshot),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(snapshot));s=bpy.context.scene;assert mesh_signature()==before
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users:
  assert im.filepath.startswith('//resources/') and im.packed_file;assert Path(bpy.path.abspath(im.filepath)).exists()
snapshot_report={'canonical_scene':str(scene),'canonical_sha256':sha(scene),'snapshot':str(snapshot),'snapshot_sha256':sha(snapshot),'geometry_uv_normals_material_assignments_unchanged':True,'mesh_signature':before,'images':images,'packed_relative_resources_reopened':True}
(W/'repository_snapshot.json').write_text(json.dumps(snapshot_report,indent=2)+'\n');shutil.copy2(__file__,W/'update-scene.py');print('PORTABLE_SNAPSHOT_VERIFIED',flush=True)
