import bpy,json,struct,hashlib
from pathlib import Path
D=Path('authoring://Naginata/worn');E=D/'exports/common';E.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(D/'naginata_worn_edges_v4.blend'));s=bpy.context.scene;original=[o for o in s.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT');copies=[]
for source in original:
 faces=[p for p in source.data.polygons if p.material_index!=1];mesh=bpy.data.meshes.new(source.name+'_intact');mesh.from_pydata([v.co for v in source.data.vertices],[],[[source.data.loops[i].vertex_index for i in p.loop_indices] for p in faces]);mesh.update()
 for old in source.data.uv_layers:
  uv=mesh.uv_layers.new(name=old.name);values=[old.data[i].uv.copy() for p in faces for i in p.loop_indices]
  for a,b in zip(uv.data,values):a.uv=b
 mesh.uv_layers.active=mesh.uv_layers['Naginata_Delivery_UV_v4'];mesh.uv_layers.active.active_render=True
 for p in mesh.polygons:p.use_smooth=True
 mesh.normals_split_custom_set([source.data.corner_normals[i].vector.copy() for p in faces for i in p.loop_indices]);
 for material in source.data.materials:mesh.materials.append(material)
 for newface,oldface in zip(mesh.polygons,faces):newface.material_index=oldface.material_index
 obj=bpy.data.objects.new(source.name+'_intact',mesh);s.collection.objects.link(obj);obj.matrix_world=source.matrix_world.copy();obj.select_set(True);copies.append(obj)
bpy.context.view_layer.objects.active=copies[-1];bpy.context.view_layer.update();assert sum(len(o.data.polygons) for o in copies)==376
path=E/'Naginata-Worn-v4.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
raw=path.read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert magic==0x46546c67 and version==2 and length==len(raw);size,kind=struct.unpack_from('<II',raw,12);data=json.loads(raw[20:20+size]);triangles=sum(data['accessors'][p['indices']]['count']//3 for m in data['meshes'] for p in m['primitives']);assert triangles==376 and len(data['meshes'])==2
assert len(data['materials'])==3;mat=data['materials'][0];assert 'baseColorTexture' in mat['pbrMetallicRoughness'] and 'metallicRoughnessTexture' in mat['pbrMetallicRoughness'] and 'normalTexture' in mat;assert all('bufferView' in i for i in data['images'])
(E/'validation_v4.json').write_text(json.dumps({'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'parts':2,'intact_triangles':376,'embedded_material_images':len(data['images']),'scope':'Portable intact-ship preview; invisible damage caps omitted only from this GLB copy. Native SHP and Blender retain them. Original source mesh and normals preserved; active UVs repaired in v4.'},indent=2));print('GLB_VALIDATED',flush=True)
