import os
import bpy, json, hashlib, numpy as np
from pathlib import Path
from mathutils import Vector
D=Path(os.environ['PHOENIX_WORKSPACE'])
W=D/'work/audit_v2';R=D/'review/audit_v2';M=D/'maps'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((D.parent/'project_state.json').read_text());src=Path(state['latest_scene']);original_hash=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update()
before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uvs={u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers}) for o in s.objects if o.type=='MESH'}
old=json.loads((D/'work/reconstruction_v1/validation.json').read_text());newuv='Phoenix_Delivery_UV_v2';changed=[]
for o in s.objects:
 if o.type!='MESH':continue
 m=o.data;u=m.uv_layers.new(name=newuv,do_init=True);m.uv_layers.active=u;u.active_render=True
 if o.name=='Phoenix_Body':
  # The left flank of this otherwise continuous belly band was mirrored and
  # shifted; the right flank also had a smaller independent offset. Use one
  # shared planar chart across its four nearly coplanar triangles.
  for index in [3,4,127,128]:
   for loop in m.polygons[index].loop_indices:
    p=o.matrix_world@m.vertices[m.loops[loop].vertex_index].co
    px=448.0*p.x+189.35;py=1027.2+(p.y-.324102)*225.5/(.717196-.324102)
    u.data[loop].uv=(px/1254,1-py/1254)
   changed.append({'part':o.name,'face':index})
def read_map(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);a=a.reshape(im.size[1],im.size[0],4);bpy.data.images.remove(im);return a
mask=read_map(M/'phoenix_worn_glass_4k_v1.png')[:,:,0]
core=mask>.999;outside=mask==0
maps=dict(old['maps']);statistics={}
# Bake the revised native glass material into the existing exact glazing mask.
# The tint and smoothness are constant; frames and all non-glass pixels retain
# their prior values. No broad texture reconstruction is performed.
values={'basecolor':(.11,.17,.145),'roughness':(.10,.10,.10),'metallic':(0.,0.,0.),'normal':(.5,.5,1.)}
for key,value in values.items():
 previous=read_map(Path(old['maps'][key]['path']));a=previous.copy();a[:,:,:3]=previous[:,:,:3]*(1-mask[:,:,None])+np.array(value,dtype=np.float32)[None,None,:]*mask[:,:,None]
 assert np.array_equal(a[outside],previous[outside])
 statistics[key]={'glass_core_range':np.ptp(a[core,:3],axis=0).tolist(),'non_glass_pixels_unchanged':True}
 im=bpy.data.images.new('Phoenix audit v2 '+key,a.shape[1],a.shape[0],alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(a.ravel());p=M/f'phoenix_worn_{key}_4k_v2.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if key=='basecolor' else '16';im.save();bpy.data.images.remove(im)
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();maps[key]={'path':str(p),'sha256':sha(p)}
 for mat in bpy.data.materials:
  if not mat.use_nodes:continue
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.name=='Delivered '+key:node.image=im
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 for node in mat.node_tree.nodes:
  if node.type in ['UVMAP','NORMAL_MAP'] and node.uv_map=='Phoenix_Delivery_UV_v1':node.uv_map=newuv
models={}
for name,b in before.items():
 o=bpy.data.objects[name];m=o.data
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals]
 assert all(v==[list(q.uv) for q in m.uv_layers[k].data] for k,v in b['uvs'].items())
 for p in m.polygons:
  if name!='Phoenix_Body' or p.index not in [3,4,127,128]:assert [list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices]==[b['uvs']['Phoenix_Delivery_UV_v1'][i] for i in p.loop_indices]
 models[name]={'vertices':b['vertices'],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
# Every shared vertex across the corrected panel has exactly one UV coordinate.
m=bpy.data.objects['Phoenix_Body'].data;shared={}
for index in [3,4,127,128]:
 for loop in m.polygons[index].loop_indices:
  vi=m.loops[loop].vertex_index;uv=list(m.uv_layers[newuv].data[loop].uv)
  if vi in shared:assert uv==shared[vi]
  shared[vi]=uv
scene=D/'phoenix_worn_pbr_v2.blend';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_hash
report=dict(old);report.update(source=str(src),source_sha256=original_hash,scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,maps=maps,models=models,audit_changes={'belly_band_faces':changed,'shared_vertices_have_identical_uvs':True,'glass_tint_srgb':values['basecolor'],'glass_roughness':.10,'glass_metallic':0,'glass_normal':'flat inside pane','all_previous_uv_layers_geometry_normals_preserved':True,'glass_map_validation':statistics},runtime_visual_validation='v1 reviewed by user; requested v2 corrections pending final review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
for name in ['Front','Belly','Opposite']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
# Exact same orthographic underside camera as the diagnostic, for seam review.
cam=s.camera;cam.location=(0,.18,-8);cam.rotation_euler=(Vector((0,.18,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.6
s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.filepath=str(R/'belly_after.png');bpy.ops.render.render(write_still=True)
print('PHOENIX_AUDIT_V2_COMPLETE',flush=True)
