import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
D=Path('local-only://worn');R=D/'review/refinement_v2';W=D/'work/refinement_v2'
ver=sys.argv[-1];src=D/('patriot_source_review.blend' if ver=='legacy' else 'patriot_worn_pbr_v1.blend' if ver=='v1' else 'patriot_worn_refined_v2.blend');bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.threads=4;s.view_settings.exposure=.3;s.render.image_settings.color_depth='8'
cam=s.camera;cam.data.type='ORTHO'
views=[('nose',(0,1.02,.32),(1,2,.6),.68),('pod',(0,1.01,.23),(.8,1,-.9),.59),('arm',(-.59,1.07,.07),(-1.4,1,-1),1.15),('joint',(-.58,-.27,.15),(-1.4,1.3,.85),1.2),('rear',(0,-1.13,.5),(.45,-1.8,1.25),1.0),('rear_belly',(0,-1.08,.34),(0,-1.7,-.35),.95)]
if ver=='legacy':views=[views[1],views[2]]
if ver=='v2':views.extend([('vent_and_muzzle',(-.56,.93,.08),(-1.1,2,1.6),1.65),('overview',(0,0,0),(4,6,3.5),4.2)])
for name,at,direction,scale in views:
 target=Vector(at);cam.location=target+Vector(direction)*2;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.view_layer.update();s.render.filepath=str(R/f'{ver}_{name}.png');bpy.ops.render.render(write_still=True)
print('REVIEW_COMPLETE',ver,flush=True)
