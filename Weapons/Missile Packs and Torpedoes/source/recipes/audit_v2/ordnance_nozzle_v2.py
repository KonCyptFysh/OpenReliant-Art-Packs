"""Bake one aligned nozzle material shared by all nine missiles and their displays."""
import bpy
from pathlib import Path

def make_nozzle(D,uvname):
 maps=Path(D)/'maps';s=bpy.context.scene;mesh=bpy.data.meshes.new('Nozzle bake plane');mesh.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)]);mesh.uv_layers.new(name='UVMap')
 for l,q in zip(mesh.uv_layers[0].data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=q
 ob=bpy.data.objects.new('Nozzle authoring plane',mesh);s.collection.objects.link(ob)
 for o in bpy.context.selected_objects:o.select_set(False)
 ob.select_set(True);bpy.context.view_layer.objects.active=ob;baked={}
 for role in ['basecolor','normal','orm']:
  mat=bpy.data.materials.new('AUTHORING aligned nozzle '+role);mat.use_nodes=True;mat.use_fake_user=True;ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links
  uv=ns.new('ShaderNodeTexCoord');mp=ns.new('ShaderNodeVectorMath');mp.operation='MULTIPLY_ADD';lk.new(uv.outputs['UV'],mp.inputs[0]);mp.inputs[1].default_value=(82/1254,82/1254,1);centre=(1206,44) if role=='basecolor' else (1200,44);mp.inputs[2].default_value=((centre[0]-41)/1254,1-(centre[1]+41)/1254,0)
  tx=ns.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(maps/f'ordnance_{role}_2k_v1.png'),check_existing=True);tx.image.colorspace_settings.name='sRGB' if role=='basecolor' else 'Non-Color';tx.image.pack();lk.new(mp.outputs[0],tx.inputs[0]);colour=tx.outputs[0]
  if role=='normal':
   a=ns.new('ShaderNodeVectorMath');a.operation='MULTIPLY_ADD';lk.new(colour,a.inputs[0]);a.inputs[1].default_value=(2,2,2);a.inputs[2].default_value=(-1,-1,-1);b=ns.new('ShaderNodeVectorMath');b.operation='NORMALIZE';lk.new(a.outputs[0],b.inputs[0]);c=ns.new('ShaderNodeVectorMath');c.operation='MULTIPLY_ADD';lk.new(b.outputs[0],c.inputs[0]);c.inputs[1].default_value=(.5,.5,.5);c.inputs[2].default_value=(.5,.5,.5);colour=c.outputs[0]
  em=ns.new('ShaderNodeEmission');lk.new(colour,em.inputs[0]);out=ns.new('ShaderNodeOutputMaterial');lk.new(em.outputs[0],out.inputs[0]);ob.data.materials.clear();ob.data.materials.append(mat);im=bpy.data.images.new('Aligned nozzle '+role,512,512,alpha=False);im.colorspace_settings.name='sRGB' if role=='basecolor' else 'Non-Color';target=ns.new('ShaderNodeTexImage');target.image=im;ns.active=target;s.cycles.samples=1;s.render.bake.margin=0;bpy.ops.object.bake(type='EMIT');im.filepath_raw=str(maps/f'ordnance_nozzle_{role}_512_v2.png');im.file_format='PNG';im.save();im.pack();baked[role]=im
 bpy.data.objects.remove(ob,do_unlink=True);mat=bpy.data.materials.new('Aligned missile nozzle v2');mat['native_material']='orord2_nozz';mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links;uv=ns.new('ShaderNodeUVMap');uv.uv_map=uvname;p=ns.new('ShaderNodeBsdfPrincipled');out=ns.new('ShaderNodeOutputMaterial');lk.new(p.outputs[0],out.inputs[0])
 for role,im in baked.items():
  tx=ns.new('ShaderNodeTexImage');tx.image=im;lk.new(uv.outputs[0],tx.inputs[0])
  if role=='basecolor':lk.new(tx.outputs[0],p.inputs['Base Color'])
  elif role=='normal':a=ns.new('ShaderNodeNormalMap');a.uv_map=uvname;lk.new(tx.outputs[0],a.inputs['Color']);lk.new(a.outputs[0],p.inputs['Normal'])
  else:a=ns.new('ShaderNodeSeparateColor');lk.new(tx.outputs[0],a.inputs[0]);lk.new(a.outputs[1],p.inputs['Roughness']);lk.new(a.outputs[2],p.inputs['Metallic'])
 return mat
