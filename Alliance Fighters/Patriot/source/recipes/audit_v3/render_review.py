import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='authoring://Patriot/worn/patriot_worn_audit_v3.blend')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=850;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.exposure=.4;c=s.camera;c.data.type='ORTHO'
views=[('engine_left',(-.61,-1.18,.01),(-.3,-.3,1),1.15),('engine_right',(.61,-1.18,.01),(.3,-.3,1),1.15),('groove',(-.57,.7,-.04),(-.5,.1,-1),.78),('radiator_left',(-.66,-.26,.18),(-1,1,1.6),.78),('radiator_right',(.66,-.26,.18),(1,1,1.6),.78),('arm',(-.59,1.07,.07),(-1.4,1,-1),1.15),('overview',(0,0,0),(4,6,3.5),4.2)]
for name,at,d,scale in views:
 t=Vector(at);c.location=t+Vector(d)*2;c.rotation_euler=(t-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath='authoring://Patriot/worn/review/audit_v3/v3_'+name+'.png';bpy.ops.render.render(write_still=True)
