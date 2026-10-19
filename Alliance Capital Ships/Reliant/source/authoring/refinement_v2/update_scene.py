import bpy,json
from pathlib import Path
D=Path('${RELIANT_WORKSPACE}');M=D/'maps/refinement_v2';W=D/'work/refinement_v2'
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v1.blend'))
parts=json.loads((D/'source/native_parts.json').read_text());rep=json.loads((W/'native_repairs.json').read_text())['files'][0]
changed=0
for r in rep['uv_changes']:
 if r['lod']!=0:continue
 obj=bpy.data.objects[parts[r['part']]['name']];p=obj.data.polygons[r['face']]
 assert len(p.loop_indices)==3
 old=list(r['before']);new=list(r['after']);layer=obj.data.uv_layers.active.data
 for li in p.loop_indices:
  u,v=layer[li].uv;match=min(range(3),key=lambda j:abs(u-old[j][0]/256)+abs(v-(1-old[j][1]/256)))
  assert abs(u-old[match][0]/256)+abs(v-(1-old[match][1]/256))<.001,(obj.name,r['face'],u,v,old)
  layer[li].uv=(new[match][0]/256,1-new[match][1]/256);changed+=1
for i in range(1,4):
 mat=bpy.data.materials[f'Reliant_Worn_REL_{i}_PBR'];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
 for node in list(nodes):
  if node.type=='TEX_IMAGE':nodes.remove(node)
 def tex(suffix,color):
  im=bpy.data.images.load(str(M/(f'orr{i}_hull'+suffix+'.png')),check_existing=False);im.colorspace_settings.name=color;im.pack();n=nodes.new('ShaderNodeTexImage');n.image=im;return n
 base=tex('','sRGB');links.new(base.outputs[0],bs.inputs['Base Color'])
 normal=tex('_normal','Non-Color');nm=nodes.new('ShaderNodeNormalMap');links.new(normal.outputs[0],nm.inputs[1]);links.new(nm.outputs[0],bs.inputs['Normal'])
 orm=tex('_orm','Non-Color');sep=nodes.new('ShaderNodeSeparateColor');links.new(orm.outputs[0],sep.inputs[0]);links.new(sep.outputs[1],bs.inputs['Roughness']);links.new(sep.outputs[2],bs.inputs['Metallic'])
 em=tex('_emissive','sRGB');links.new(em.outputs[0],bs.inputs['Emission Color'])
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'reliant_worn_pbr_v2.blend'));print('SCENE_V2_SAVED',changed,'UV corners')
