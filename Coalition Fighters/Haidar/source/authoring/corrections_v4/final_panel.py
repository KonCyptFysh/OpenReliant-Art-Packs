import os
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/corrections_v4';M=D/'maps/corrections_v4';R=D/'review/corrections_v4';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();v=json.loads((W/'validation.json').read_text());bpy.ops.wm.open_mainfile(filepath=v['scene']);s=bpy.context.scene
source=(W/'build_revision.py').read_text();exec(source[source.index('def read('):source.index('N=4096;')])
sc=4096/1254;sy0,sy1=int(287*sc),int(301*sc);sx0,sx1=int(1013*sc),int(1066*sc);yy,xx=np.mgrid[sy0:sy1,sx0:sx1].astype(np.float32);x=(xx+.5)/sc;y=(yy+.5)/sc;dist=np.hypot(x-np.clip(x,1018,1060),y-294);mask=1-smooth(3.1,4.4,dist);sl=np.s_[sy0:sy1,sx0:sx1]
# Reuse immediately adjacent worn finish in the generated repair reference.
# Only this dangling line footprint is composited; the dark curved panel paint,
# surrounding seams and its adjacent rivet remain untouched.
ref=read(M/'cleanup_reference.png',4096);finish=ref[np.rint(yy-10*sc).astype(int),np.rint(xx).astype(int)]
for key in ['basecolor','normal','height','panels','structure']:
 a=read(v['maps']['hull'][key]['path'])
 if key=='basecolor':a[sl]=a[sl]*(1-mask[:,:,None])+finish*mask[:,:,None]
 elif key=='normal':a[sl]=a[sl]*(1-mask[:,:,None])+np.array([.5,.5,1])*mask[:,:,None];q=a[sl]*2-1;q/=np.linalg.norm(q,axis=-1,keepdims=True);a[sl]=q*.5+.5
 elif key=='height':a[sl]=a[sl]*(1-mask[:,:,None])+.5*mask[:,:,None]
 else:a[sl]*=1-mask[:,:,None]
 v['maps']['hull'][key]=save(a,'hull_'+key)
a=read(v['maps']['hull']['panel_edit_mask']['path']);a[sl]=np.maximum(a[sl],mask[:,:,None]);v['maps']['hull']['panel_edit_mask']=save(a,'panel_edit_mask');v['line_repairs'].append([[[1018,294],[1060,294]],4.4])
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users and Path(bpy.path.abspath(im.filepath)).parent==M:
  if im.packed_file:im.unpack(method='REMOVE')
  im.reload();im.pack()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=v['scene']);v['scene_sha256']=sha(v['scene']);(W/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=16
for name in ['Front','Opposite']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
cam=bpy.data.objects['Cockpit'];cam.data.type='ORTHO';cam.data.ortho_scale=2.25;s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=1000;target=bpy.data.objects['Han_Body'].matrix_world@Vector((0,-10,5))
for name,off in [('body_right',(3,.4,1.8)),('body_roof',(.1,0,4)),('body_belly',(2.2,.4,-2.6))]:
 cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(name+'_after.png'));bpy.ops.render.render(write_still=True)
print('HAIDAR_FINAL_PANEL_COMPLETE',flush=True)
