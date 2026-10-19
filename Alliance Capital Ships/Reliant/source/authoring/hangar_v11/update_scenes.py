import bpy,json,hashlib
from pathlib import Path
D=Path('${RELIANT_WORKSPACE}');W=D/'work/hangar_v11';M=D/'maps/hangar_v11'
def material(stem):
    mat=bpy.data.materials.new('Reliant_Interior_'+stem);mat.use_nodes=True
    tree=mat.node_tree;bs=tree.nodes.get('Principled BSDF');bs.inputs['Emission Strength'].default_value=1
    images={}
    for suffix in ['', '_normal','_orm','_emissive']:
        im=bpy.data.images.load(str(M/(stem+suffix+'.png')),check_existing=True)
        im.colorspace_settings.name='Non-Color' if suffix in ['_normal','_orm'] else 'sRGB';im.pack()
        node=tree.nodes.new('ShaderNodeTexImage');node.image=im;images[suffix]=node
    tree.links.new(images[''].outputs['Color'],bs.inputs['Base Color'])
    tree.links.new(images['_emissive'].outputs['Color'],bs.inputs['Emission Color'])
    split=tree.nodes.new('ShaderNodeSeparateColor');tree.links.new(images['_orm'].outputs['Color'],split.inputs['Color'])
    tree.links.new(split.outputs['Green'],bs.inputs['Roughness']);tree.links.new(split.outputs['Blue'],bs.inputs['Metallic'])
    normal=tree.nodes.new('ShaderNodeNormalMap');tree.links.new(images['_normal'].outputs['Color'],normal.inputs['Color']);tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    return mat
def geo():
    return hashlib.sha256(json.dumps([(o.name,[list(r) for r in o.matrix_world],[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in sorted(bpy.data.objects,key=lambda o:o.name) if o.type=='MESH']).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v10.blend'));before=geo()
tube=material('orr_tube');slots={}
records=json.loads((W/'build-report.json').read_text())['tube_models'][0]['changes'];n=0
for r in records:
    if r['lod']!=0:continue
    obj=bpy.data.objects[r['part_name']]
    if obj.name not in slots:
        obj.data.materials.append(tube);slots[obj.name]=len(obj.data.materials)-1
    slot=slots[obj.name]
    p=obj.data.polygons[r['face']];layer=obj.data.uv_layers.active.data
    for i in p.loop_indices:
        u,v=layer[i].uv;j=min(range(3),key=lambda j:abs(u-r['old_uv'][j][0]/256)+abs(v-(1-r['old_uv'][j][1]/256)))
        assert abs(u-r['old_uv'][j][0]/256)+abs(v-(1-r['old_uv'][j][1]/256))<1e-5
        layer[i].uv=(r['new_uv'][j][0]/256,1-r['new_uv'][j][1]/256);n+=1
    p.material_index=slot
assert n==216 and geo()==before
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'reliant_worn_pbr_v11.blend'))
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v11.blend'));assert geo()==before
main_hash=geo()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(W/'hangar.gltf'))
mats={stem:material(stem) for stem in ['orr_hang1','orr_hang2','orr_hang3']}
meshes=[]
for o in bpy.data.objects:
    if o.type!='MESH':continue
    for slot in o.material_slots:
        old=slot.material.name
        stem=next((s for s in mats if old.startswith(s)),None)
        assert stem,old
        slot.material=mats[stem]
    meshes.append(o.name)
bpy.context.scene['native_animation_source']=str(W/'native/Reliant_Hang.SHP')
bpy.context.scene['note']='Editable material and mesh scene; native SHP remains authoritative for animations, attachments and collision.'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'reliant_hangar_v11.blend'))
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_hangar_v11.blend'))
for m in bpy.data.materials:
    if not m.name.startswith('Reliant_Interior_'):continue
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE':assert node.image.packed_file
(W/'scene-validation.json').write_text(json.dumps(dict(passed=True,tube_uv_corners=n,main_geometry_hash=main_hash,main_geometry_unchanged=True,hangar_meshes=meshes,packed_maps=True),indent=2)+'\n')
print('MAIN AND HANGAR SCENES SAVED AND REOPENED')
