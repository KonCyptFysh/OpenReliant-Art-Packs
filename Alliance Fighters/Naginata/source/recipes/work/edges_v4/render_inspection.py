import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[2];R=D/'review/edges_v4';args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['after'];mode=args[0];name='naginata_worn_aligned_v3.blend' if mode=='before' else 'naginata_worn_edges_v4.blend';bpy.ops.wm.open_mainfile(filepath=str(D/name));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.image_settings.color_depth='8';s.render.image_settings.color_mode='RGB';s.view_settings.exposure=0;s.world.color=(.03,.03,.03);cam=s.camera;cam.data.lens=65
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
lights=[]
for name,power,size in [('inspection key',220,2),('inspection fill',150,2)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);lights.append(o)
views=[('upper_leading_edge',(1.12,.32,.57),(.73,-.40,.32)),('upper_trailing_edge',(1.2,-1.62,.6),(.73,-.9,.32)),('upper_opening',(1.25,-.47,.55),(.685,-.64,.43)),('lower_opening',(1.28,-.88,-.50),(.73,-.69,-.31)),('engine_surface',(1.0,-1.56,.64),(.38,-.99,.14)),('exhaust_outlets',(0,-2.7,.58),(0,-1.02,.18))]
if len(args)>1:views=[v for v in views if v[0] in args[1:]]
(R/mode).mkdir(parents=True,exist_ok=True)
for name,c,t in views:
 cam.location=c;target=Vector(t);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();direction=(cam.location-target).normalized();right=direction.cross(Vector((0,0,1))).normalized()
 for light,pos in zip(lights,[target+direction*1.3+right*.6+Vector((0,0,.5)),target+direction*1.0-right*.6]):light.location=pos;light.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update();s.render.filepath=str(R/mode/(name+'.png'));bpy.ops.render.render(write_still=True);print('INSPECTION_RENDER',mode,name,flush=True)
