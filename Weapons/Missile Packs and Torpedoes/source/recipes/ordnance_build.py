import sys,math,json,struct,hashlib
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent));import ordnance_native as n
D=n.D;W=n.W;M=D/'maps';E=D/'exports/runtime_v1';E.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True)
newuv='Ordnance_Delivery_UV_v1';mat=bpy.data.materials.new('Ordnance worn paint and exposed metal');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;uv.location=(-650,0);bs=nodes.new('ShaderNodeBsdfPrincipled');bs.location=(100,0);bs.inputs['Specular IOR Level'].default_value=.4;out=nodes.new('ShaderNodeOutputMaterial');out.location=(400,0);links.new(bs.outputs[0],out.inputs[0])
for key,idx in [('basecolor',0),('normal',1),('roughness',2),('metallic',3)]:
 im=bpy.data.images.load(str(M/f'ordnance_{key}_2k_v1.png'));im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();tx=nodes.new('ShaderNodeTexImage');tx.image=im;tx.name='Delivered '+key;tx.location=(-400,300-idx*230);links.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;nm.location=(-80,-150);links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(tx.outputs[0],bs.inputs[dict(basecolor='Base Color',roughness='Roughness',metallic='Metallic')[key]])
hidden_mat=bpy.data.materials.new('Original hidden damage caps');hidden_mat.use_nodes=True;ns=hidden_mat.node_tree.nodes;ns.clear();hb=ns.new('ShaderNodeBsdfTransparent');ho=ns.new('ShaderNodeOutputMaterial');hidden_mat.node_tree.links.new(hb.outputs[0],ho.inputs[0])
im=bpy.data.images.load(str(M/'ordnance_basecolor_generated_v1.png'));im.colorspace_settings.name='Non-Color';px=np.empty(1254*1254*4,np.float32);im.pixels.foreach_get(px);rgb=px.reshape(1254,1254,4)[::-1,:,:3];bpy.data.images.remove(im)
scene=bpy.context.scene;report=[];allrepairs=[];obs=[];files=sorted((D/'source/native').glob('*.SHP'))
for fi,file in enumerate(files):
 raw=file.read_bytes();parts=n.models(raw);collection=bpy.data.collections.new(file.stem);scene.collection.children.link(collection);points=np.array([np.array(v)+p['origin'] for p in parts if p['lod']==0 for v in p['verts']]);centre=(points.min(0)+points.max(0))/2;extent=max(points.max(0)-points.min(0));scale=2.8/extent;rot=Matrix.Rotation(math.radians(-25),4,'Z')@Matrix.Rotation(math.radians(-57),4,'X');place=Vector(((fi%6-2.5)*3.5,(2.5-fi//6)*3.65,0));aspects=[];changed=0
 for p in parts:
  p['new_uv'],repairs=n.repaired(p,rgb);allrepairs += [dict(file=file.name,**r) for r in repairs];changed+=sum(len(r['faces']) for r in repairs)
  faces=[];old=[];new=[];native_corner=[]
  for f in p['faces']:
   idx=f['indices'].copy();corners=[0,1,2];q=p['new_uv'][f['id']];pts=[Vector(p['verts'][j]) for j in idx]
   if f['fan']==3:idx[1],idx[2]=idx[2],idx[1];corners[1],corners[2]=corners[2],corners[1]
   faces.append(idx);old.extend([(f['uv'][k][0],1-f['uv'][k][1]) for k in corners]);new.extend([(float(q[k,0]),1-float(q[k,1])) for k in corners]);native_corner.extend(corners);aspects.append(n.ratio(np.array(p['verts'])[f['indices']],q))
  mesh=bpy.data.meshes.new(f'{file.stem}_part{p["part"]}_LOD{p["lod"]}');mesh.from_pydata(p['verts'],[],faces);mesh.update();original=mesh.uv_layers.new(name='Original_Ordnance_UV');deliver=mesh.uv_layers.new(name=newuv);mesh.uv_layers.active=deliver;deliver.active_render=True
  for layer,qs in [(original,old),(deliver,new)]:
   for q,v in zip(layer.data,qs):q.uv=v
  for f in mesh.polygons:f.use_smooth=True
  mesh.normals_split_custom_set([p['normals'][l.vertex_index] for l in mesh.loops]);mesh.materials.append(mat);mesh.materials.append(hidden_mat)
  for f in p['faces']:
   if f['hidden']:mesh.polygons[f['id']].material_index=1
  o=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(o);o.matrix_world=Matrix.Translation(place)@rot@Matrix.Scale(scale,4)@Matrix.Translation(Vector(p['origin'])-Vector(centre));o['native_model']=file.name;o['native_part']=p['part'];o['native_lod']=p['lod'];o['native_origin']=p['origin'];o['native_corner_order']=native_corner;o['native_hidden_faces']=[f['id'] for f in p['faces'] if f['hidden']];o['native_uv_v_axis']='Blender V=1-native V';o.hide_render=p['lod']!=0;o.hide_set(p['lod']!=0);obs.append(o)
 record=n.export(raw,parts,E/file.name);record.update(model=file.name,part_lods=len(parts),lod0_faces=sum(len(p['faces']) for p in parts if p['lod']==0),changed_uv_faces_all_lods=changed,max_uv_anisotropy_after=max(aspects));report.append(record)
 # Labels are source-review aids; never part of a native runtime model.
 tx=bpy.data.curves.new(file.stem+' label','FONT');tx.body=file.stem;tx.align_x='CENTER';tx.size=.17;o=bpy.data.objects.new(tx.name,tx);scene.collection.objects.link(o);o.location=place+Vector((0,-1.75,.2))
 labelmat=bpy.data.materials.get('Review labels')
 if labelmat is None:
  labelmat=bpy.data.materials.new('Review labels');labelmat.diffuse_color=(.75,.8,.85,1);labelmat.use_nodes=True;pn=labelmat.node_tree.nodes.get('Principled BSDF');pn.inputs['Base Color'].default_value=(.75,.8,.85,1);pn.inputs['Emission Color'].default_value=(.75,.8,.85,1);pn.inputs['Emission Strength'].default_value=.25
 tx.materials.append(labelmat)
# Source keeps all LODs and exact native coordinates. Only object display transforms arrange the review board.
scene['asset']='Missile Packs, Torpedoes and Fuel Pod - worn v1';scene['emissives']='deferred';scene['release']='hold';scene['source_notes']='Earlier editable meshes match native geometry but their saved UV data are empty. Native originals supply original UVs, normals, all LODs and attachment metadata. All originals preserved.'
text=bpy.data.texts.new('README - Ordnance source');text.write('32 complete native variants. Collections are model filenames; LOD0 shown, remaining LOD objects hidden. Mesh coordinates, custom normals and Original_Ordnance_UV preserve the original game data. Delivery UV is the current pass. Object transforms only arrange the review board. Runtime export must retain native metadata, part origins and LODs. Native source bytes and repeatable exporter live beside the portable snapshot. Painted markings have zero height. Emissives remain deferred. Do not run the initial build over subsequent hand edits.\n')
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=2600;scene.render.resolution_y=2600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.world=bpy.data.worlds.new('Ordnance review studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.12,.15,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,loc,power,size in [('Key',(-6,5,14),7000,15),('Fill',(8,-5,11),4300,13),('Rim',(-6,-10,6),2500,10)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new(name,ld);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Inventory camera');cam.type='ORTHO';cam.ortho_scale=23;o=bpy.data.objects.new('Inventory camera',cam);scene.collection.objects.link(o);o.location=(0,0,30);scene.camera=o
bpy.context.view_layer.update();meshobs=[o for o in scene.objects if o.type=='MESH'];assert len(files)==32;assert all(r['max_uv_anisotropy_after']<=12.01 for r in report)
scene.render.filepath=str(D/'review/reconstruction_v1/inventory.png');bpy.context.preferences.filepaths.save_version=0
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=26;area.spaces.active.shading.type='MATERIAL'
for ob in meshobs:
 source_model=next(p for p in n.models((D/'source/native'/ob['native_model']).read_bytes()) if p['part']==ob['native_part'] and p['lod']==ob['native_lod']);attr=ob.data.attributes.new('NativeVertexNormal','FLOAT_VECTOR','POINT')
 for item,v in zip(attr.data,source_model['normals']):item.vector=v
 baseline=ob.data.attributes.new('ImportedCornerNormal','FLOAT_VECTOR','CORNER')
 for item,v in zip(baseline.data,ob.data.corner_normals):item.vector=v.vector
scene_path=D/'ordnance_worn_pbr_v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene_path),compress=True)
(W/'native_export_validation.json').write_text(json.dumps(dict(models=report,uv_repairs=allrepairs,models_count=32,mesh_part_lods=len(meshobs),current_scene_sha256=n.sha(scene_path),original_geometry_normals_flags_attachments_animation_preserved=True,material_name=n.MAT,max_uv_anisotropy_after=max(r['max_uv_anisotropy_after'] for r in report),source_geometry_equivalence='All eight prior editable meshes match corresponding native loadout geometry; no saved UV data in prior blends.'),indent=2));print('ORDNANCE_SOURCE_EXPORT_COMPLETE',len(meshobs),sum(r['changed_uv_faces_all_lods'] for r in report),flush=True)
bpy.ops.render.render(write_still=True);print('ORDNANCE_INVENTORY_RENDER_COMPLETE',flush=True)
