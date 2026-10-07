"""Bake an editable cylindrical UV shader from the existing atlas.
Paint is flat. Seven complete circumferential repeats close the spiral seam.
No original atlas pixels or approved model materials are modified.
"""
import bpy,math
from pathlib import Path

def make_wrap(D,uvname):
 maps=Path(D)/'maps';s=bpy.context.scene
 # Bake object: UV plane; emission bake is independent of all review lights.
 mesh=bpy.data.meshes.new('Screamer wrap bake plane');mesh.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)]);mesh.uv_layers.new(name='UVMap')
 for l,q in zip(mesh.uv_layers[0].data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=q
 ob=bpy.data.objects.new('Screamer wrap authoring plane',mesh);s.collection.objects.link(ob)
 for o in bpy.context.selected_objects:o.select_set(False)
 ob.select_set(True);bpy.context.view_layer.objects.active=ob
 baked={}
 for role in ['basecolor','normal','orm']:
  mat=bpy.data.materials.new('AUTHORING Screamer cylindrical '+role);mat.use_nodes=True;mat.use_fake_user=True;ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links
  def node(t,label=None):
   n=ns.new(t)
   if label:n.label=label;n.name=label
   return n
  def plug(x,inp):
   if hasattr(x,'node'):lk.new(x,inp)
   else:inp.default_value=x
  def mathn(op,a,b=None,c=None):
   n=node('ShaderNodeMath');n.operation=op;plug(a,n.inputs[0]);
   if b is not None:plug(b,n.inputs[1])
   if c is not None:plug(c,n.inputs[2])
   return n.outputs[0]
  def vec(x,y,z=0):
   n=node('ShaderNodeCombineXYZ');plug(x,n.inputs[0]);plug(y,n.inputs[1]);plug(z,n.inputs[2]);return n.outputs[0]
  def image_sample(vector):
   n=node('ShaderNodeTexImage');n.image=bpy.data.images.load(str(maps/f'ordnance_{role}_2k_v1.png'),check_existing=True);n.image.colorspace_settings.name='sRGB' if role=='basecolor' else 'Non-Color';n.image.pack();plug(vector,n.inputs[0]);return n.outputs['Color']
  def mix(f,a,b):
   n=node('ShaderNodeMixRGB');plug(f,n.inputs[0]);plug(a,n.inputs[1]);plug(b,n.inputs[2]);return n.outputs[0]
  uv=node('ShaderNodeTexCoord');sep=node('ShaderNodeSeparateXYZ');plug(uv.outputs['UV'],sep.inputs[0]);u=sep.outputs[0];v=sep.outputs[1]
  yy=mathn('SUBTRACT',711,mathn('MULTIPLY',591,v));x=mathn('ADD',711,mathn('MULTIPLY',30,mathn('PINGPONG',mathn('MULTIPLY',8,u),1)))
  baseline=image_sample(vec(mathn('DIVIDE',x,1254),mathn('SUBTRACT',1,mathn('DIVIDE',yy,1254))))
  band=mathn('MULTIPLY',mathn('GREATER_THAN',yy,296),mathn('LESS_THAN',yy,556))
  phase=mathn('ADD',mathn('MULTIPLY',mathn('DIVIDE',mathn('SUBTRACT',yy,296),260),260/39),mathn('MULTIPLY',u,7))
  yellow=mathn('LESS_THAN',mathn('FRACT',phase),.5)
  if role=='basecolor':
   wear_u=mathn('ADD',713,mathn('MULTIPLY',25,mathn('PINGPONG',mathn('MULTIPLY',u,12),1)))
   wear_y=mathn('ADD',mathn('SUBTRACT',725,wear_u),mathn('MULTIPLY',3,mathn('SINE',mathn('MULTIPLY',v,30*math.pi))))
   red=image_sample(vec(mathn('DIVIDE',wear_u,1254),mathn('SUBTRACT',1,mathn('DIVIDE',mathn('ADD',306,wear_y),1254))))
   gold=image_sample(vec(mathn('DIVIDE',wear_u,1254),mathn('SUBTRACT',1,mathn('DIVIDE',mathn('ADD',325,wear_y),1254))))
   # Colour wear only, sampled on a seamless cylindrical domain; no embossed paint.
   noise=node('ShaderNodeTexNoise','Fine worn paint');noise.inputs['Scale'].default_value=80;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.75
   plug(vec(mathn('COSINE',mathn('MULTIPLY',u,2*math.pi)),mathn('SINE',mathn('MULTIPLY',u,2*math.pi)),mathn('MULTIPLY',v,2)),noise.inputs['Vector'])
   worn=mathn('ADD',.45,mathn('MULTIPLY',noise.outputs['Fac'],1.1));mult=node('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;plug(mix(yellow,red,gold),mult.inputs[1]);plug(worn,mult.inputs[2]);colour=mix(band,baseline,mult.outputs[0])
  elif role=='orm':colour=mix(band,baseline,(1,.72,0,1))
  else:
   n=node('ShaderNodeVectorMath');n.operation='MULTIPLY_ADD';plug(baseline,n.inputs[0]);n.inputs[1].default_value=(2,2,2);n.inputs[2].default_value=(-1,-1,-1)
   a=node('ShaderNodeVectorMath');a.operation='NORMALIZE';plug(n.outputs[0],a.inputs[0]);b=node('ShaderNodeVectorMath');b.operation='MULTIPLY_ADD';plug(a.outputs[0],b.inputs[0]);b.inputs[1].default_value=(.5,.5,.5);b.inputs[2].default_value=(.5,.5,.5);colour=mix(band,b.outputs[0],(.5,.5,1,1))
  em=node('ShaderNodeEmission');plug(colour,em.inputs['Color']);out=node('ShaderNodeOutputMaterial');plug(em.outputs[0],out.inputs[0]);ob.data.materials.clear();ob.data.materials.append(mat)
  im=bpy.data.images.new('Screamer wrap '+role,2048,2048,alpha=False);im.colorspace_settings.name='sRGB' if role=='basecolor' else 'Non-Color';target=node('ShaderNodeTexImage','Bake target');target.image=im;ns.active=target
  s.render.engine='CYCLES';s.cycles.samples=1;s.render.bake.margin=0;bpy.ops.object.bake(type='EMIT');im.filepath_raw=str(maps/f'ordnance_screamer_wrap_{role}_2k_v2.png');im.file_format='PNG';im.save();im.pack();baked[role]=im
 bpy.data.objects.remove(ob,do_unlink=True)
 mat=bpy.data.materials.new('Screamer continuous cylindrical wrap v2');mat['native_material']='orord2_scrm';mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links;uv=ns.new('ShaderNodeUVMap');uv.uv_map=uvname;p=ns.new('ShaderNodeBsdfPrincipled');p.inputs['Specular IOR Level'].default_value=.4;out=ns.new('ShaderNodeOutputMaterial');lk.new(p.outputs[0],out.inputs[0])
 for role,im in baked.items():
  tx=ns.new('ShaderNodeTexImage');tx.image=im;lk.new(uv.outputs[0],tx.inputs[0])
  if role=='basecolor':lk.new(tx.outputs[0],p.inputs['Base Color'])
  elif role=='normal':nm=ns.new('ShaderNodeNormalMap');nm.uv_map=uvname;lk.new(tx.outputs[0],nm.inputs['Color']);lk.new(nm.outputs[0],p.inputs['Normal'])
  else:sep=ns.new('ShaderNodeSeparateColor');lk.new(tx.outputs[0],sep.inputs[0]);lk.new(sep.outputs[1],p.inputs['Roughness']);lk.new(sep.outputs[2],p.inputs['Metallic'])
 return mat
