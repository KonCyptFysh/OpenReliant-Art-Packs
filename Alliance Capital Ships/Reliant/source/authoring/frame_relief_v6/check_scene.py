import bpy,hashlib,json
from pathlib import Path
D=Path('${RELIANT_WORKSPACE}')
def geometry():
 out=[]
 for ob in sorted(bpy.data.objects,key=lambda o:o.name):
  if ob.type!='MESH':continue
  m=ob.data;out.append((ob.name,[list(row) for row in ob.matrix_world],[[*v.co] for v in m.vertices],[[*p.vertices] for p in m.polygons],[[list(l.uv) for l in u.data] for u in m.uv_layers]))
 return hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v5.blend'));old=geometry()
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v6.blend'));assert geometry()==old
checked=[]
for node in bpy.data.materials['Reliant_Worn_REL_2_PBR'].node_tree.nodes:
 if node.type!='TEX_IMAGE' or not node.image:continue
 name=Path(node.image.filepath).name
 if name not in ['orr2_hull_normal.png','orr2_hull_orm.png']:continue
 assert hashlib.sha256(node.image.packed_file.data).hexdigest()==hashlib.sha256((D/'maps/frame_relief_v6'/name).read_bytes()).hexdigest();checked.append(name)
assert len(checked)==2
(D/'work/frame_relief_v6/scene-validation.json').write_text(json.dumps(dict(passed=True,geometry_and_uv_identical=True,geometry_sha256=old,packed_images_match=checked),indent=2)+'\n')
print('SCENE_GEOMETRY_UV_AND_PACKED_MAPS_VERIFIED')
