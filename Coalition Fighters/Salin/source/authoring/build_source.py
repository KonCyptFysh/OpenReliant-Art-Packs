from pathlib import Path
import os
import bpy,math,json,hashlib,struct
from mathutils import Matrix,Vector
D=Path(os.environ['SALIN_WORKSPACE']).resolve();W=D/'work/reconstruction_v1';R=D/'review/reconstruction_v1';bpy.ops.wm.read_factory_settings(use_empty=True)
raw=(D/'source/Luda.SHP').read_bytes();chs=[];pos=0
while pos<len(raw):
 t,z,c=struct.unpack_from('<HHH',raw,pos);end=pos+6+z*c;chs.append((t,z,c,raw[pos+6:end]));pos=end
assert pos==len(raw);meta=json.loads((D/'source/native_parts.json').read_text());part=-1;lod=-1;meshes=[];audit=[]
for tag,size,count,data in chs:
 if tag==2:part+=1;lod=-1
 if tag==4:
  lod+=1
  if lod==0:verts=[struct.unpack_from('<3f',data,i*size) for i in range(count)];normals=[struct.unpack_from('<3f',data,i*size+12) for i in range(count)]
 if tag==3 and lod==0:
  desc=meta[part];origin=Vector(desc['origin']);faces=[];uvs=[];hidden=[];materials=[]
  for i in range(count):
   off=i*size;materials.append(struct.unpack_from('<I',data,off)[0]);hidden.append(bool((struct.unpack_from('<I',data,off+8)[0]&1) or (struct.unpack_from('<I',data,off+4)[0]&15)==1));idx=list(struct.unpack_from('<3I',data,off+12));uv=struct.unpack_from('<6f',data,off+24);pairs=[(uv[k],1-uv[k+3]) for k in range(3)];normal=Vector(struct.unpack_from('<3f',data,off+48));poly=struct.unpack_from('<I',data,off+72)[0] if size>=80 else 0
   if poly==3:idx[1],idx[2]=idx[2],idx[1];pairs[1],pairs[2]=pairs[2],pairs[1]
   pts=[Vector(verts[j]) for j in idx]
   if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(normal)<0:idx[1],idx[2]=idx[2],idx[1];pairs[1],pairs[2]=pairs[2],pairs[1]
   faces.append(idx);uvs.extend(pairs)
  desc['name']=desc['name'].replace(' ','_');mesh=bpy.data.meshes.new(desc['name']);mesh.from_pydata([Vector(v)+origin for v in verts],[],faces);mesh.update();uv=mesh.uv_layers.new(name='Original_Salin_UV')
  for q,v in zip(uv.data,uvs):q.uv=v
  mesh.uv_layers.new(name='Salin_Atlas_UV_v1',do_init=True);mesh.uv_layers.active=mesh.uv_layers['Salin_Atlas_UV_v1'];mesh.uv_layers.active.active_render=True
  for p in mesh.polygons:p.use_smooth=True
  mesh.normals_split_custom_set([normals[l.vertex_index] for l in mesh.loops]);o=bpy.data.objects.new(desc['name'],mesh);o['native_part_index']=part;o['native_material_indices']=materials;o['native_hidden_faces']=[i for i,h in enumerate(hidden) if h];bpy.context.collection.objects.link(o);o.matrix_world=Matrix.Rotation(-math.pi/2,4,'X');o.scale*=.0025;meshes.append(o);audit.append({'part':o.name,'vertices':len(verts),'faces':len(faces),'visible_faces':len(faces)-sum(hidden)})
bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);centre=(lo+hi)/2
for o in meshes:o.location-=centre
mats=[];native=[]
for mi in [1]:
 original=bpy.data.images.load(str(D/'source/luda.png'));original.pack();original.colorspace_settings.name='sRGB';native.append(list(original.size))
 mat=bpy.data.materials.new(f'Salin_Colour_Review_{mi}');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();uv=n.new('ShaderNodeUVMap');uv.name='Atlas UV';uv.uv_map='Salin_Atlas_UV_v1';tx=n.new('ShaderNodeTexImage');tx.name='Base colour';tx.image=original;tx.extension='REPEAT';l.new(uv.outputs[0],tx.inputs[0]);bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.85;bs.inputs['Specular IOR Level'].default_value=0;l.new(tx.outputs[0],bs.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0]);mats.append(mat)
hidden_mat=bpy.data.materials.new('Native caps hidden on intact ship');hidden_mat.use_nodes=True;hn=hidden_mat.node_tree.nodes;hn.clear();hb=hn.new('ShaderNodeBsdfTransparent');ho=hn.new('ShaderNodeOutputMaterial');hidden_mat.node_tree.links.new(hb.outputs[0],ho.inputs[0])
for o in meshes:
 [o.data.materials.append(m) for m in mats];o.data.materials.append(hidden_mat)
 for p,mi in zip(o.data.polygons,o['native_material_indices']):p.material_index=mi
 for idx in o['native_hidden_faces']:o.data.polygons[idx].material_index=1
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.5
s.world=bpy.data.worlds.new('Black review studio');s.world.use_nodes=True;nw=s.world.node_tree.nodes;lw=s.world.node_tree.links;nw.clear();lp=nw.new('ShaderNodeLightPath');black=nw.new('ShaderNodeBackground');black.inputs[1].default_value=0;amb=nw.new('ShaderNodeBackground');amb.inputs[0].default_value=(.16,.16,.16,1);amb.inputs[1].default_value=.35;mix=nw.new('ShaderNodeMixShader');outw=nw.new('ShaderNodeOutputWorld');lw.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);lw.new(amb.outputs[0],mix.inputs[1]);lw.new(black.outputs[0],mix.inputs[2]);lw.new(mix.outputs[0],outw.inputs[0])
for name,loc,power,sz in [('Key',(3,5,7),800,5),('Fill',(-4,2,3),450,4),('Rim',(2,-5,5),950,4),('Bottom',(0,0,-5),300,4)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=sz;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,target in [('Front',(4,6,3.5),(0,0,0)),('Opposite',(-4,6,3.5),(0,0,0)),('Rear',(-6,-9,5),(0,0,0)),('Belly',(5,7,-5),(0,0,0)),('Cockpit',(2,4,2),(0,1,.15))]:
 data=bpy.data.cameras.new(name);data.lens=60;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects['Front'];
from bpy_extras.object_utils import world_to_camera_view
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for attempt in range(100):
  bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in meshes for v in o.data.vertices]
  if all(.06<t.x<.94 and .06<t.y<.94 and t.z>0 for t in q):break
  cam.location*=1.04
bpy.context.preferences.filepaths.save_version=0
bpy.context.view_layer.update();assert len(meshes)==1 and sum(len(o.data.polygons) for o in meshes)==456
record={'parts':audit,'source_sha256':hashlib.sha256(raw).hexdigest(),'orientation':'native -Y top -> world +Z, native +Z nose -> world +Y','source_atlas_resolution':native,'geometry_signature':hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in meshes},sort_keys=True).encode()).hexdigest()}
(W/'baseline_audit.json').write_text(json.dumps(record,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(D/'salin_source_review.blend'))
s.camera=bpy.data.objects['Front'];s.render.filepath=str(R/'source_front.png');bpy.ops.render.render(write_still=True);print('BUILD_SOURCE_COMPLETE',flush=True)
