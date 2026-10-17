from pathlib import Path
import bpy, hashlib, json

S = Path('/tmp/kurgen-turret-v7')
D = Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Kurgen/worn')
source = D/'kurgen_worn_pbr_v3.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))

def signatures():
    out = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        mesh = obj.data
        data = dict(vertices=[list(v.co) for v in mesh.vertices],
                    polygons=[list(p.vertices) for p in mesh.polygons],
                    normals=[list(n.vector) for n in mesh.corner_normals],
                    uvs={u.name:[list(v.uv) for v in u.data] for u in mesh.uv_layers},
                    transform=[list(row) for row in obj.matrix_world],
                    materials=[m.name if m else None for m in mesh.materials])
        out[obj.name] = hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
    return out

before = signatures()
replacement = bpy.data.images.load(str(S/'kurgen_turret_basecolor_v7.png'),check_existing=False)
replacement.name = 'kurgen_turret_basecolor_v7.png'
replacement.pack()
replacement.filepath = str(D/'maps/turret_star_v7/kurgen_turret_basecolor_v7.png')
changed = []
for material in bpy.data.materials:
    if not material.use_nodes: continue
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image and 'kurgen_turret_basecolor_v1' in node.image.name:
            changed.append(dict(material=material.name,node=node.name,old_image=node.image.name,new_image=replacement.name))
            node.image = replacement
assert len(changed) == 1, changed
after = signatures()
assert before == after
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(S/'kurgen_worn_pbr_v7.blend'))
(S/'scene-audit.json').write_text(json.dumps(dict(source=str(source),
    mesh_uv_normals_transforms_material_assignments_unchanged=True,
    mesh_signatures=after,changed_image_nodes=changed,
    packed_texture_sha256=hashlib.sha256(replacement.packed_file.data).hexdigest()),indent=2)+'\n')
print('STAR_SCENE_AUDIT PASS',len(after),'meshes, one image replaced')
