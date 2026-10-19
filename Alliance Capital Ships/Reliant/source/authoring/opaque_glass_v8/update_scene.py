import bpy,json,hashlib
from pathlib import Path
D=Path('${RELIANT_WORKSPACE}');M=D/'maps/opaque_glass_v8';W=D/'work/opaque_glass_v8'
def geometry():
    out=[]
    for ob in sorted(bpy.data.objects,key=lambda o:o.name):
        if ob.type!='MESH':continue
        m=ob.data;out.append((ob.name,[list(row) for row in ob.matrix_world],[[*v.co] for v in m.vertices],[[*p.vertices] for p in m.polygons],[[list(l.uv) for l in u.data] for u in m.uv_layers]))
    return hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v7.blend'));old=geometry()
names=['orr2_hull.png','orr2_hull_emissive.png','orr2_hull_orm.png','orr2_hull_normal.png'];changed=[]
for node in bpy.data.materials['Reliant_Worn_REL_2_PBR'].node_tree.nodes:
    if node.type!='TEX_IMAGE' or not node.image:continue
    name=Path(bpy.path.abspath(node.image.filepath)).name
    if name not in names:continue
    image=bpy.data.images.load(str(M/name),check_existing=False)
    image.colorspace_settings.name='sRGB' if name in names[:2] else 'Non-Color'
    image.pack();node.image=image;changed.append(name)
assert sorted(changed)==sorted(names)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'reliant_worn_pbr_v8.blend'))
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v8.blend'));assert old==geometry()
checked=[]
for node in bpy.data.materials['Reliant_Worn_REL_2_PBR'].node_tree.nodes:
    if node.type!='TEX_IMAGE' or not node.image:continue
    name=Path(node.image.filepath).name
    if name not in names:continue
    assert hashlib.sha256(node.image.packed_file.data).hexdigest()==hashlib.sha256((M/name).read_bytes()).hexdigest();checked.append(name)
assert sorted(checked)==sorted(names)
(W/'scene-validation.json').write_text(json.dumps(dict(passed=True,geometry_and_uv_identical=True,geometry_sha256=old,packed_images_match=checked),indent=2)+'\n')
print('V8 SCENE SAVED AND REOPENED; GEOMETRY, UVS AND PACKED MAPS VERIFIED',flush=True)
