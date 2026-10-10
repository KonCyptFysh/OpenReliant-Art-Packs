import os
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/corrections_v4';M=D/'maps/corrections_v4';R=D/'review/corrections_v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();v=json.loads((W/'validation.json').read_text());bpy.ops.wm.open_mainfile(filepath=v['scene']);s=bpy.context.scene
source=(W/'build_revision.py').read_text();exec(source[source.index('def read('):source.index('N=4096;')])
N=4096;scale=N/1254;sl=np.s_[int(490*scale):int(600*scale),:int(190*scale)];y,x=np.mgrid[int(490*scale):int(600*scale),:int(190*scale)].astype(np.float32);X=(x+.5)/scale;Y=(y+.5)/scale
def poly(points):
 p=np.array(points);inside=np.zeros(X.shape,bool);dist=np.full(X.shape,1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  e=b-a;t=np.clip(((X-a[0])*e[0]+(Y-a[1])*e[1])/(e@e),0,1);dist=np.minimum(dist,np.hypot(X-a[0]-t*e[0],Y-a[1]-t*e[1]));inside^=((a[1]>Y)!=(b[1]>Y))&(X<a[0]+(Y-a[1])*e[0]/(e[1]+1e-12))
 return np.where(inside,dist,-dist)
cm=bpy.data.objects['Han_Cockpit'].data;uv=cm.uv_layers[v['active_uv']]
def corner(fi,vi):p=cm.polygons[fi];li=p.loop_indices[list(p.vertices).index(vi)];return cm.vertices[vi].co.z,uv.data[li].uv.x*1254
z0,u0=corner(42,28);z1,u1=corner(42,31);rz0,ru0=corner(41,28);rz1,ru1=corner(41,31)
bars=[];alignment=[]
for sideu in [490.5,555.]:
 z=z0+(sideu-u0)/(u1-u0)*(z1-z0);roofu=ru0+(z-rz0)/(rz1-rz0)*(ru1-ru0);bars.append([roofu,'x',2.6]);alignment.append(dict(side_u=sideu,native_z=z,roof_u=roofu,shared_vertices=[28,31],alignment_error_native_units=0.))
print('EXACT_SHARED_EDGE_ALIGNMENT',alignment,flush=True)
outer=poly(v['glass_outlines'][0]);bd=np.full(X.shape,1e6,np.float32);ribs=np.zeros(X.shape,np.float32);finish=np.zeros((*X.shape,3),np.float32);ref=read(D/'maps/alignment_v3/window_frame_reference_v3.png',N)
for centre,axis,half in bars:
 bd=np.minimum(bd,np.abs(X-centre)-half);weight=(1-smooth(-.15,.15,np.abs(X-centre)-half))*smooth(-.15,.15,outer);sx=np.clip(np.rint((85.5+(X-centre)*.6)*scale-.5).astype(int),0,N-1);sy=np.rint(Y*scale-.5).astype(int);finish+=ref[sy,sx]*weight[:,:,None];ribs=np.maximum(ribs,weight)
pane=np.minimum(outer,bd);foot=smooth(-4.5,-3.7,outer);inside=smooth(-.15,.15,outer);glass=smooth(2,2.6,pane)*inside;gasket=(1-ribs)*(1-glass)*inside;h=(.18*smooth(-2,0,outer)*(1-smooth(-.8,.6,pane))-.90*smooth(0,2.5,pane))*foot
dy,dx=np.gradient(h,1254/N);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
maps=v['maps']['hull']
for key in ['basecolor','normal','roughness','metallic','height','glass','seal','structure','panels','paint','frame_mask','glazing_edit_mask','frame_height']:
 a=read(maps[key]['path']);p=a[sl].copy()
 if key=='basecolor':p=p*(1-inside[:,:,None])+np.array([.11,.17,.145])*inside[:,:,None];p=p*(1-gasket[:,:,None])+np.array([.052,.068,.058])*gasket[:,:,None];p=p*(1-ribs[:,:,None])+finish
 elif key=='normal':p=p*(1-foot[:,:,None])+(normal*.5+.5)*foot[:,:,None];q=p*2-1;q/=np.linalg.norm(q,axis=-1,keepdims=True);p=q*.5+.5
 elif key=='roughness':p=p*(1-inside[:,:,None])+(.16*glass+.86*gasket+.62*ribs)[:,:,None]
 elif key=='metallic':p=p*(1-inside[:,:,None])+.48*ribs[:,:,None]
 elif key=='height':p=p*(1-foot[:,:,None])+((h+4)/8)[:,:,None]*foot[:,:,None]
 elif key=='glass':p[:]=glass[:,:,None]
 elif key=='seal':p[:]=(gasket+ribs)[:,:,None]
 elif key=='structure':p=p*(1-inside[:,:,None])+(gasket+ribs)[:,:,None]
 elif key in ['panels','paint']:p*=1-inside[:,:,None]
 elif key=='frame_mask':p[:]=ribs[:,:,None]
 elif key=='glazing_edit_mask':p[:]=foot[:,:,None]
 elif key=='frame_height':p[:]=((h+4)/8)[:,:,None]
 a[sl]=p
 # One remaining thin shoulder seam crosses a rotated chart and ends in metal.
 if key in ['basecolor','normal','height','panels','structure']:
  sy0,sy1=int(896*scale),int(908*scale);sx0,sx1=int(348*scale),int(468*scale);ys,xs=np.mgrid[sy0:sy1,sx0:sx1].astype(np.float32);xx=(xs+.5)/scale;yy=(ys+.5)/scale;dist=np.hypot(xx-np.clip(xx,351,464),yy-902);mask=1-smooth(3.7,5.,dist);ss=np.s_[sy0:sy1,sx0:sx1]
  if key=='basecolor':cref=read(M/'cleanup_reference.png',N);a[ss]=a[ss]*(1-mask[:,:,None])+cref[ss]*mask[:,:,None]
  elif key=='normal':a[ss]=a[ss]*(1-mask[:,:,None])+np.array([.5,.5,1])*mask[:,:,None];nn=a[ss]*2-1;nn/=np.linalg.norm(nn,axis=-1,keepdims=True);a[ss]=nn*.5+.5
  elif key=='height':a[ss]=a[ss]*(1-mask[:,:,None])+.5*mask[:,:,None]
  else:a[ss]*=1-mask[:,:,None]
 maps[key]=save(np.clip(a,0,1),'hull_'+key if key in ['basecolor','normal','roughness','metallic','height','glass','seal','structure','panels','paint'] else key);print('REFINED',key,flush=True)
maskmap=read(maps['panel_edit_mask']['path']);maskmap[ss]=np.maximum(maskmap[ss],mask[:,:,None]);maps['panel_edit_mask']=save(maskmap,'panel_edit_mask')
v['frame_layout'][0]=bars;v['roof_side_alignment']=alignment;v['line_repairs'].append([[[351,902],[464,902]],5.])
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users:
  path=Path(bpy.path.abspath(im.filepath))
  if path.parent==M:
   if im.packed_file:im.unpack(method='REMOVE')
   im.reload();im.pack()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=v['scene']);v['scene_sha256']=sha(v['scene']);(W/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
# Reuse the exact final-review camera definitions from the initial pass.
obs=[o for o in s.objects if o.type=='MESH'];body=bpy.data.objects['Han_Body'];cockpit=bpy.data.objects['Han_Cockpit'];s.cycles.samples=16
exec(source[source.index("for name in ['Front','Opposite']:"):])
