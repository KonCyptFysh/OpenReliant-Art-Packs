import bpy,json,math
from pathlib import Path
from mathutils import Vector
r=Path('${RELIANT_WORKSPACE}')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(r/'source/reliant.gltf'))
s=bpy.context.scene;s.frame_set(0)
for o in s.objects:
 if 'DEST' in o.name:o.hide_render=True;o.hide_set(True)
 if o.type=='LIGHT':o.hide_render=True
obs=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
points=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
lo=Vector([min(p[k] for p in points) for k in range(3)]);hi=Vector([max(p[k] for p in points) for k in range(3)]);c=(lo+hi)/2;size=(hi-lo).length
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.11,.14,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
for name,direction,strength in [('Key',(1,2,1),3),('Fill',(-1,.7,-1),1.2)]:
 l=bpy.data.lights.new(name,'SUN');l.energy=strength;l.angle=.15;o=bpy.data.objects.new(name,l);s.collection.objects.link(o);o.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
for name,vec in [('Front',(1,.8,1.3)),('Opposite',(-1,.8,1.3)),('Rear',(.8,.5,-1.3)),('Belly',(1,-.7,.7))]:
 ca=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,ca);s.collection.objects.link(o);o.location=c+Vector(vec).normalized()*size*1.0;o.rotation_euler=(c-o.location).to_track_quat('-Z','Y').to_euler();ca.type='ORTHO';ca.ortho_scale=size*.9;ca.clip_end=size*10;ca.clip_start=1;s.camera=o
s.view_settings.view_transform='AgX';s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(r/'reliant_source_review.blend'))
for name in ['Front','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(r/'review'/('source_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
print('SOURCE_REVIEW_READY')
