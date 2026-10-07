"""Bake spatially continuous pod mouth collars while retaining the existing worn artwork.
UV-only editing; original native triangles and stored custom normals remain unchanged.
"""
import os
import bpy,math,json
from pathlib import Path
D=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve();W=D/'work/audit_v3';UV='Ordnance_Delivery_UV_v3';SOURCE='Audit_v3_before_collar';BAND='Audit_v3_collar_sample';MASK='Audit_v3_collar_mask'
bpy.ops.wm.open_mainfile(filepath=str(D/'ordnance_worn_audit_v3_work.blend'))
for o in bpy.data.objects:o.hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=1;s.render.bake.margin=12;s.render.bake.use_clear=False;s.render.bake.use_selected_to_active=False;s.render.bake.normal_space='TANGENT';maps=D/'maps/audit_v3';maps.mkdir(parents=True,exist_ok=True)
source={}
for role in ['basecolor','normal','orm']:
 im=bpy.data.images.load(str(D/'maps'/f'ordnance_{role}_2k_v1.png'),check_existing=True);im.colorspace_settings.name='sRGB' if role=='basecolor' else 'Non-Color';im.pack();source[role]=im
logs=[]
for name,key,start,end,box in [('01_screamer_pod.SHP','spod',98,113.8,(165,665,205,708)),('02_raptor_POD.SHP','rpod',58,85.33,(1040,110,1098,195))]:
 obs=[o for o in bpy.data.objects if o.type=='MESH' and o.get('native_model')==name]
 for o in bpy.context.selected_objects:o.select_set(False)
 for o in obs:
  o.hide_set(False);o.hide_render=False;o.select_set(True)
  for label in [SOURCE,BAND,MASK]:o.data.uv_layers.new(name=label)
  for a,b in zip(o.data.uv_layers[SOURCE].data,o.data.uv_layers[UV].data):a.uv=b.uv
  for p in o.data.polygons:
   allowed=float(abs(p.normal.z)<.94 and o.data.materials[p.material_index].name!='Original hidden damage caps')
   angles=[(math.atan2(o.data.vertices[o.data.loops[l].vertex_index].co.y,o.data.vertices[o.data.loops[l].vertex_index].co.x)+math.pi)/(2*math.pi) for l in p.loop_indices]
   if max(angles)-min(angles)>.5:angles=[a+1 if a<.5 else a for a in angles]
   for l,angle in zip(p.loop_indices,angles):
    z=o.data.vertices[o.data.loops[l].vertex_index].co.z
    # Mirrored repetition gives shared, continuous samples at the longitudinal seam.
    phase=angle*8
    u=phase;v=(box[1]+(z-start)/(end-start)*(box[3]-box[1]))/1254
    o.data.uv_layers[BAND].data[l].uv=(u,1-v);o.data.uv_layers[MASK].data[l].uv=(z-start,allowed)
  o.data.uv_layers.active=o.data.uv_layers[UV];o.data.uv_layers[UV].active_render=True
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.008,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 mat=bpy.data.materials.new('AUTHORING continuous '+key+' collar v3');mat.use_nodes=True;mat.use_fake_user=True;ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links
 def node(t,label):q=ns.new(t);q.label=label;return q
 uv=node('ShaderNodeUVMap','Retained source artwork');uv.uv_map=SOURCE
 buv=node('ShaderNodeUVMap','Continuous mouth band');buv.uv_map=BAND
 bs=node('ShaderNodeSeparateXYZ','Unwrapped circumference');lk.new(buv.outputs[0],bs.inputs[0]);pp=node('ShaderNodeMath','Continuous mirrored tile within atlas');pp.operation='PINGPONG';lk.new(bs.outputs[0],pp.inputs[0]);pp.inputs[1].default_value=1
 bscale=node('ShaderNodeMath','Atlas band width');bscale.operation='MULTIPLY_ADD';lk.new(pp.outputs[0],bscale.inputs[0]);bscale.inputs[1].default_value=(box[2]-box[0])/1254;bscale.inputs[2].default_value=box[0]/1254
 bc=node('ShaderNodeCombineXYZ','Band sample coordinates');lk.new(bscale.outputs[0],bc.inputs[0]);lk.new(bs.outputs[1],bc.inputs[1])
 flo=node('ShaderNodeMath','Tile orientation');flo.operation='FLOOR';lk.new(bs.outputs[0],flo.inputs[0]);odd=node('ShaderNodeMath','Mirrored half');odd.operation='PINGPONG';lk.new(flo.outputs[0],odd.inputs[0]);odd.inputs[1].default_value=1
 mask=node('ShaderNodeUVMap','Longitudinal mask and face eligibility');mask.uv_map=MASK
 sep=node('ShaderNodeSeparateXYZ','Mask coordinates');lk.new(mask.outputs[0],sep.inputs[0]);gt=node('ShaderNodeMath','Band begins at shared physical station');gt.operation='GREATER_THAN';lk.new(sep.outputs[0],gt.inputs[0]);gt.inputs[1].default_value=0
 mul=node('ShaderNodeMath','Exclude mouth and end caps');mul.operation='MULTIPLY';lk.new(gt.outputs[0],mul.inputs[0]);lk.new(sep.outputs[1],mul.inputs[1]);factor=mul.outputs[0]
 mixed={}
 for role in source:
  sockets=[]
  for un in [uv,buv]:
   tx=node('ShaderNodeTexImage',role+' '+un.label);tx.image=source[role];lk.new(bc.outputs[0] if un==buv else un.outputs[0],tx.inputs[0]);colour=tx.outputs[0]
   if role=='normal':
    if un==buv:
     sp=node('ShaderNodeSeparateColor','Normal components');lk.new(colour,sp.inputs[0]);inv=node('ShaderNodeMath','Flip tangent X on mirrored tiles');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;lk.new(sp.outputs[0],inv.inputs[1]);mx=node('ShaderNodeMixRGB','Mirror normal orientation');lk.new(odd.outputs[0],mx.inputs[0]);lk.new(sp.outputs[0],mx.inputs[1]);lk.new(inv.outputs[0],mx.inputs[2]);co=node('ShaderNodeCombineColor','Oriented normal');lk.new(mx.outputs[0],co.inputs[0]);lk.new(sp.outputs[1],co.inputs[1]);lk.new(sp.outputs[2],co.inputs[2]);colour=co.outputs[0]
    nm=node('ShaderNodeNormalMap','Preserve source relief tangent orientation');nm.uv_map=un.uv_map;lk.new(colour,nm.inputs['Color']);colour=nm.outputs[0]
   sockets.append(colour)
  mix=node('ShaderNodeMixRGB','Collar '+role);mix.blend_type='MIX';lk.new(factor,mix.inputs[0]);lk.new(sockets[0],mix.inputs[1]);lk.new(sockets[1],mix.inputs[2]);mixed[role]=mix.outputs[0]
 em=node('ShaderNodeEmission','Colour and ORM bake output');p=node('ShaderNodeBsdfPrincipled','Normal rebake output');lk.new(mixed['normal'],p.inputs['Normal']);out=node('ShaderNodeOutputMaterial','Bake output');target=node('ShaderNodeTexImage','Active bake target');ns.active=target
 for o in obs:
  o.data.materials.clear();o.data.materials.append(mat)
  for f in o.data.polygons:f.material_index=0
 baked={}
 for role in ['basecolor','orm','normal']:
  im=bpy.data.images.new('Ordnance '+key+' '+role+' v3',4096,4096,alpha=False);im.colorspace_settings.name='sRGB' if role=='basecolor' else 'Non-Color';target.image=im
  for l in list(out.inputs[0].links):lk.remove(l)
  if role=='normal':lk.new(p.outputs[0],out.inputs[0]);kind='NORMAL'
  else:lk.new(mixed[role],em.inputs[0]);lk.new(em.outputs[0],out.inputs[0]);kind='EMIT'
  print('BAKE_BEGIN',name,role,flush=True);bpy.ops.object.bake(type=kind);im.filepath_raw=str(maps/f'ordnance_{key}_{role}_4k_v3.png');im.file_format='PNG';im.save();im.pack();baked[role]=im;print('BAKE_DONE',name,role,flush=True)
 final=bpy.data.materials.new('Ordnance '+key+' continuous mouth collar v3');final['native_material']='orord3_'+key;final.use_nodes=True;fn=final.node_tree.nodes;fn.clear();fl=final.node_tree.links;fuv=fn.new('ShaderNodeUVMap');fuv.uv_map=UV;fp=fn.new('ShaderNodeBsdfPrincipled');fo=fn.new('ShaderNodeOutputMaterial');fl.new(fp.outputs[0],fo.inputs[0])
 for role,im in baked.items():
  tx=fn.new('ShaderNodeTexImage');tx.image=im;fl.new(fuv.outputs[0],tx.inputs[0])
  if role=='basecolor':fl.new(tx.outputs[0],fp.inputs['Base Color'])
  elif role=='normal':nm=fn.new('ShaderNodeNormalMap');nm.uv_map=UV;fl.new(tx.outputs[0],nm.inputs['Color']);fl.new(nm.outputs[0],fp.inputs['Normal'])
  else:sp=fn.new('ShaderNodeSeparateColor');fl.new(tx.outputs[0],sp.inputs[0]);fl.new(sp.outputs[1],fp.inputs['Roughness']);fl.new(sp.outputs[2],fp.inputs['Metallic'])
 for o in obs:o.data.materials[0]=final
 logs.append(dict(model=name,material=final['native_material'],lod_objects=len(obs),z_start=start,z_end=end,source_box=box,resolution=4096))
(W/'pod_collar_bakes.json').write_text(json.dumps(logs,indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'ordnance_worn_audit_v3_baked.blend'),compress=True);print('POD_BAKES_SAVED',flush=True)
