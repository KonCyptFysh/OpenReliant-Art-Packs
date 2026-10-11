import os
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
D=Path(os.environ['GALAHAD_WORKSPACE']);W=D/'work/canopy_v2';R=D/'review/canopy_v2';M=D/'maps'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((D/'work/reconstruction_v1/validation.json').read_text());src=Path(old['scene']);assert sha(src)==old['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
def signature():
 return hashlib.sha256(json.dumps({o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[(list(p.vertices),p.material_index) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uv={u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers},matrix=[list(r) for r in o.matrix_world]) for o in s.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
before=signature();records=old['maps']['hull'].copy();N=4096;scale=N/1254;x0,y0,cw,ch=2528,0,844,1132
yy,xx=np.mgrid[:ch,:cw].astype(np.float32);X=(xx+x0+.5)/scale;Y=(yy+y0+.5)/scale
def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1);return np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def poly(p):
 inside=np.zeros((ch,cw),bool);d=np.full((ch,cw),1e6,np.float32)
 for a,b in zip(p,p[1:]+p[:1]):
  d=np.minimum(d,capsule(a,b));inside^=((a[1]>Y)!=(b[1]>Y))&(X<(b[0]-a[0])*(Y-a[1])/(b[1]-a[1]+1e-10)+a[0])
 return np.where(inside,d,-d)
def read(path,size=None):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
 if size:im.scale(*size)
 width,height=im.size;buf=np.empty(width*height*4,np.float32);im.pixels.foreach_get(buf);a=buf.reshape(height,width,4)[::-1].copy();bpy.data.images.remove(im);return a
def save(a,key):
 h,w=a.shape[:2];im=bpy.data.images.new('Galahad canopy v2 '+key,w,h,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());p=M/f'galahad_hull_{key}_v2.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]=dict(path=str(p),sha256=sha(p),dimensions=[w,h]);return p
regions=json.loads((D/'work/reconstruction_v1/regions.json').read_text())['regions']
old_dist=np.maximum.reduce([poly(p) for p in regions['glass'][:2]])
new_polys=[[[853,59],[999,59],[1005,65],[1005,102],[999,108],[853,108],[847,102],[846,66]],[[811,219],[887,171],[903,164],[912,169],[912,174],[907,178],[823,227],[812,227],[809,224],[809,222]]]
dist=np.maximum.reduce([poly(p) for p in new_polys])
# Preserve exact original glass, gaskets, metal frame pixels, panel lines and markings.
edit=smooth(786,791,X)*(1-smooth(1025,1030,X))*(1-smooth(238,246,Y))
edit*=1-smooth(-8,-5.5,old_dist)
panel_dist=np.full((ch,cw),1e6,np.float32)
for points in regions['panels']:
 for a,b in zip(points,points[1:]):panel_dist=np.minimum(panel_dist,capsule(a,b))
edit*=smooth(4,7,panel_dist)
# Do not alter overlapping non-cockpit body UV faces in this atlas rectangle.
for face in old['models']['Galahad_Body']['faces']:
 points=[[u*1254,(1-v)*1254] for u,v in face['uv']]
 if max(p[0] for p in points)<785 or min(p[0] for p in points)>1033 or min(p[1] for p in points)>250 or max(p[1] for p in points)<0:continue
 edit*=1-smooth(-2,0,poly(points))
patch=read(M/'galahad_cockpit_surface_generated_v2.png',(cw,ch))
a=read(records['basecolor']['path']);c=a[y0:y0+ch,x0:x0+cw];c[:,:,:3]=c[:,:,:3]*(1-edit[:,:,None])+patch[:,:,:3]*edit[:,:,None]
base_crop=c.copy();save(a,'basecolor');del a,patch
# Export the exact locality/protection mask used to insert the generated detail.
mask=np.ones((ch,cw,4),np.float32);mask[:,:,:3]=edit[:,:,None]
im=bpy.data.images.new('Cockpit bounded edit mask',cw,ch,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(mask[::-1]).ravel());im.filepath_raw=str(W/'edit_mask.png');im.file_format='PNG';im.save();bpy.data.images.remove(im)
# Refine only the material response adjacent to the two cockpit panes.
window_area=np.maximum(old_dist,dist)>-12
glass=smooth(.7,2,dist);seal=smooth(-7,-2,dist)
frame=smooth(-6,-4.5,dist)*(1-smooth(-3,0,dist))
height=.10*frame-1.0*smooth(-2.5,2.5,dist);height[dist>3]=-1; height[dist<-8]=0
dy,dx=np.gradient(height);v=np.stack((-dx*scale,dy*scale,np.ones_like(height)),-1);v/=np.linalg.norm(v,axis=-1,keepdims=True);v[dist>3]=[0,0,1]
rgb=base_crop[:,:,:3];lum=rgb.mean(-1);mx=rgb.max(-1);mn=rgb.min(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6))
metal=(1-paint)*smooth(.15,.48,lum)*.65
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25
rough=np.clip(.8*(1-metal)+.54*metal+.04*smooth(.03,.18,np.abs(lum-local)),.52,.89)
green=(rgb[:,:,1]-rgb[:,:,0]>3/255)&(rgb[:,:,1]-rgb[:,:,2]>3/255)&(rgb.max(-1)<75/255)
glass*=green # Never assign the smooth glass response to a painted frame pixel.
for key in ['normal','roughness','metallic','glass','seal','frame','height','paint']:
 a=read(records[key]['path']);c=a[y0:y0+ch,x0:x0+cw];prior=c[:,:,:3].copy()
 if key=='normal':new=v*.5+.5;c[:,:,:3][window_area]=new[window_area]
 elif key=='height':c[:,:,:3][window_area]=((height+4)/8)[window_area,None]
 elif key in ['glass','seal','frame']:
  values={'glass':glass,'seal':seal,'frame':frame}[key];c[:,:,:3][window_area]=values[window_area,None]
 elif key=='paint':c[:,:,:3]=c[:,:,:3]*(1-edit[:,:,None])+paint[:,:,None]*edit[:,:,None]
 else:
  values=rough if key=='roughness' else metal
  c[:,:,:3]=c[:,:,:3]*(1-edit[:,:,None])+values[:,:,None]*edit[:,:,None]
  if key=='roughness':win=.72*(1-glass)+.15*glass
  else:win=np.zeros_like(glass)
  # Dark seal is non-metallic; the narrow actual metal rim has its own response.
  rim=frame*(1-green)*smooth(.12,.25,lum)
  win=win*(1-rim)+(.58 if key=='roughness' else .35)*rim
  c[:,:,:3][window_area]=win[window_area,None]
 save(a,key);del a,prior
mat=next(o for o in s.objects if o.type=='MESH').data.materials[0];mat.name='Galahad_Worn_Hull_PBR_canopy_v2'
for key in ['basecolor','normal','roughness','metallic']:
 tx=mat.node_tree.nodes['Delivered '+key];im=bpy.data.images.load(records[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();tx.image=im
assert signature()==before and sha(src)==old['scene_sha256']
scene=D/'galahad_worn_pbr_v2.blend';s.camera=bpy.data.objects['Front'];bpy.ops.wm.save_as_mainfile(filepath=str(scene))
r=dict(old);r.update(source=str(src),source_sha256=sha(src),scene=str(scene),scene_sha256=sha(scene),maps={'hull':records},window_recess=dict(depth=1.0,frame_height=.10,glass_interiors_flat=True,separate_metal_frame_relief=True,scope='Two cockpit panes only; original front windshield unchanged'),revision='canopy_v2',geometry_uv_normals_transforms_signature=before,basecolor_edit_scope=dict(crop=[x0,y0,cw,ch],master_scope_y_max=246,masked_pixels=int((edit>0).sum()),coverage_percent=float((edit>0).sum()/N**2*100),glass_frames_panel_lines_original_pixels_preserved=True),glass_mask_outside_green_pixels=int(((glass>.01)&~green).sum()),runtime_visual_validation='pending_user_review')
(W/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('CANOPY_V2_MATERIALS_VALIDATED',flush=True)
# Authoring close-ups: same scene and lighting on both sides. No game launch.
o=bpy.data.objects['Galahad_Cockpit'];corners=[o.matrix_world@Vector(v) for v in o.bound_box];target=sum(corners,Vector())/8
s.cycles.samples=16;s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100
for name,offset in [('cockpit_right',Vector((2.5,2.0,1.5))),('cockpit_left',Vector((-2.5,2.0,1.5)))]:
 cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));s.collection.objects.link(cam);cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.8;s.camera=cam;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Front'];s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.filepath=str(R/'material_front.png');bpy.ops.render.render(write_still=True)
print('CANOPY_V2_RENDER_COMPLETE',flush=True)
