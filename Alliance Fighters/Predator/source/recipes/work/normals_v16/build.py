import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path('authoring://Predator/worn');W=D/'work/normals_v16';M=D/'maps/normals_v16';M.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(D/'predator_worn_normals_v15.blend'))
N=4096;S=1600/N
# Every wing section evaluates the same height in the existing seam-aligned UVs.
# Convert the physical gradient through the actual mesh tangent frame per face.
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def slot(x,y,a,b,r,rails=0,depth=3):
 a=np.array(a);v=np.array(b)-a;t=np.clip(((x-a[0])*v[0]+(y-a[1])*v[1])/np.dot(v,v),0,1);d=r-np.sqrt((x-a[0]-t*v[0])**2+(y-a[1]-t*v[1])**2);h=-depth*smooth(0,3,d)
 if rails:
  v=v/np.linalg.norm(v);cross=-(x-a[0])*v[1]+(y-a[1])*v[0];pitch=2*r/(rails+1)
  for i in range(rails):h+=(depth+1)*(1-smooth(pitch*.16,pitch*.33,np.abs(cross-(i-(rails-1)/2)*pitch)))*smooth(3,6,d)
 return h,smooth(-2,0,d)
def wing(x,y):
 h=np.zeros_like(x);m=np.zeros_like(x)
 for cy in [265,374]:
  hh,mm=slot(x,y,(238,cy),(503,cy),25,3,5);h+=hh;m=np.maximum(m,mm)
 return h,m
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);return a.reshape(N,N,4)[::-1].copy()
def save(a,path,label):
 out=bpy.data.images.new(label,N,N,alpha=False,float_buffer=True);out.colorspace_settings.name='Non-Color';out.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());out.filepath_raw=str(path);out.file_format='PNG';bpy.context.scene.render.image_settings.color_depth='16';out.save();out.pack();return out
# Authored sign interiors only. Physical frames and adjacent machinery are excluded.
polys={'base':[
 [(199,420),(294,420),(294,472),(199,472)],[(620,401),(686,401),(686,439),(620,439)],[(1384,246),(1481,246),(1481,297),(1384,297)],
 [(625,1200),(948,1200),(948,1226),(625,1226)],[(117,1569),(215,1569),(215,1598),(117,1598)],
 [(548,99),(809,99),(809,108),(548,108)],
 [(1427,11),(1577,11),(1577,22),(1427,22)],[(1427,88),(1577,88),(1577,97),(1427,97)],
 [(639,1324),(764,1324),(764,1336),(639,1336)],[(639,1402),(764,1402),(764,1413),(639,1413)],
 [(1471,1241),(1490,1241),(1490,1525),(1471,1525)],[(1556,1241),(1573,1241),(1573,1525),(1556,1525)],
 [(147,310),(174,347),(118,347)],
 ],'surface':[
 [(443,1280),(475,1267),(522,1334),(487,1355)],[(1374,294),(1393,291),(1429,491),(1411,492)],
 [(217,154),(310,181),(305,193),(213,167)],[(188,218),(278,244),(283,232),(193,207)],
 [(530,264),(641,252),(643,263),(532,275)],[(548,402),(660,390),(662,401),(551,413)],
 [(838,1454),(911,1412),(916,1423),(844,1467)],[(857,1553),(930,1511),(924,1500),(851,1541)],
 [(234,339),(269,368),(211,382)],[(288,1271),(326,1297),(298,1325)],
 ],'markings':[]}
report={};body=bpy.data.objects['Predator__Body'];body.data.calc_tangents(uvmap=body.data.uv_layers.active.name)
for k in ['base','surface','markings']:
 arr=load(D/f'maps/normals_v15/predator_{k}_normal_4k_v15.png');orig=arr.copy();changed=np.zeros((N,N),np.float32)
 if k in ['base','surface']:
  prior=load(D/f'maps/normals_v14/predator_{k}_normal_4k_v14.png')
  for fi in ([129,267] if k=='base' else [124,261]):
   p=body.data.polygons[fi];inds=list(p.loop_indices);uv=np.array([[body.data.uv_layers.active.data[i].uv.x*1600,(1-body.data.uv_layers.active.data[i].uv.y)*1600] for i in inds]);src=np.array([[body.data.uv_layers['Aligned_Predator_UV_v4'].data[i].uv.x*1600,(1-body.data.uv_layers['Aligned_Predator_UV_v4'].data[i].uv.y)*1600] for i in inds]);xyz=np.array([list(body.matrix_world@body.data.vertices[i].co) for i in p.vertices]);lo=np.maximum(0,np.floor((uv.min(0)-3)/S).astype(int));hi=np.minimum(N,np.ceil((uv.max(0)+3)/S).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];xy=np.stack(((xx+.5)*S,(yy+.5)*S),-1);ab=(xy-uv[0])@np.linalg.inv(np.stack((uv[1]-uv[0],uv[2]-uv[0]),0));tri=(ab[...,0]>=-.006)&(ab[...,1]>=-.006)&(ab.sum(-1)<=1.006);q=src[0]+ab@(src[1:]-src[0]);h,mask=wing(q[...,0],q[...,1]);eps=.15;dx=(wing(q[...,0]+eps,q[...,1])[0]-wing(q[...,0]-eps,q[...,1])[0])/(2*eps);dy=(wing(q[...,0],q[...,1]+eps)[0]-wing(q[...,0],q[...,1]-eps)[0])/(2*eps)
   jac=np.linalg.solve(src[1:]-src[0],xyz[1:]-xyz[0]);dual=np.linalg.inv(jac@jac.T)@jac;grad=dx[...,None]*dual[0]+dy[...,None]*dual[1]
   mat=body.matrix_world.to_3x3();ns=np.array([list((mat.inverted().transposed()@body.data.corner_normals[i].vector).normalized()) for i in inds]);ts=np.array([list((mat@body.data.loops[i].tangent).normalized()) for i in inds]);normal=ns[0]+ab@(ns[1:]-ns[0]);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);tangent=ts[0]+ab@(ts[1:]-ts[0]);tangent-=normal*np.sum(tangent*normal,axis=-1,keepdims=True);tangent/=np.linalg.norm(tangent,axis=-1,keepdims=True);bitangent=np.cross(normal,tangent)*body.data.loops[inds[0]].bitangent_sign
   grad-=normal*np.sum(grad*normal,axis=-1,keepdims=True);vec=normal-grad*.005;vec/=np.linalg.norm(vec,axis=-1,keepdims=True);nt=np.stack((np.sum(vec*tangent,axis=-1),np.sum(vec*bitangent,axis=-1),np.sum(vec*normal,axis=-1)),-1)*.5+.5
   sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];a=arr[sl];a[tri]=prior[sl][tri];m=mask*tri;a[:,:,:3]=a[:,:,:3]*(1-m[...,None])+nt*m[...,None];changed[sl]=np.maximum(changed[sl],tri.astype(float))
  del prior
 # Clear the full nose recess including the noisy lip, with a deliberate smooth profile.
 slots=([(1016,1348,1374,1348,17),(1016,1415,1374,1415,17)] if k=='base' else [(1348,64,1310,260,14)] if k=='surface' else [])
 for x1,y1,x2,y2,r in slots:
  lo=np.maximum(0,np.floor((np.minimum([x1,y1],[x2,y2])-r-4)/S).astype(int));hi=np.minimum(N,np.ceil((np.maximum([x1,y1],[x2,y2])+r+4)/S).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];x=(xx+.5)*S;y=(yy+.5)*S;h,m=slot(x,y,(x1,y1),(x2,y2),r);dy,dx=np.gradient(h,S);v=np.stack((-dx,dy,np.ones_like(dx)),-1);v/=np.linalg.norm(v,axis=-1,keepdims=True);sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];arr[sl][:,:,:3]=arr[sl][:,:,:3]*(1-m[...,None])+(v*.5+.5)*m[...,None];changed[sl]=np.maximum(changed[sl],m)
 # Paint-only caution labels: exact neutral tangent normals across sign interiors.
 for poly in polys[k]:
  pts=np.array(poly,float);lo=np.maximum(0,np.floor((pts.min(0)-3)/S).astype(int));hi=np.minimum(N,np.ceil((pts.max(0)+3)/S).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];x=(xx+.5)*S;y=(yy+.5)*S;d=np.full(x.shape,1e9);area=np.sum(pts[:,0]*np.roll(pts[:,1],-1)-pts[:,1]*np.roll(pts[:,0],-1))
  for a,b in zip(pts,np.roll(pts,-1,axis=0)):
   v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(y-a[1])-v[1]*(x-a[0]))/np.linalg.norm(v))
  m=smooth(-1,0,d);sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];arr[sl][:,:,:3]=arr[sl][:,:,:3]*(1-m[...,None])+np.array([.5,.5,1])*m[...,None];changed[sl]=np.maximum(changed[sl],m)
 assert np.array_equal(arr[changed==0],orig[changed==0])
 out=save(arr,M/f'predator_{k}_normal_4k_v16.png','Predator v16 '+k)
 maskimg=np.ones_like(arr);maskimg[:,:,:3]=changed[...,None];save(maskimg,M/f'predator_{k}_edit_mask_v16.png','Edit mask '+k)
 for mat in bpy.data.materials:
  if mat.use_nodes and 'Delivered normal v14' in mat.node_tree.nodes and k in mat.name:mat.node_tree.nodes['Delivered normal v14'].image=out;mat.node_tree.nodes['Delivered normal v14'].label='v16 continuous wing fins; flat caution paint'
 report[k]={'normal':str(M/f'predator_{k}_normal_4k_v16.png'),'changed_texels':int(np.count_nonzero(changed)),'sha256':hashlib.sha256(Path(out.filepath_raw).read_bytes()).hexdigest()};print('MAP',k,flush=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'predator_worn_normals_v16.blend'));(W/'validation.json').write_text(json.dumps(report,indent=2));(W/'sign_regions.json').write_text(json.dumps(polys,indent=2));print('DONE',flush=True)
