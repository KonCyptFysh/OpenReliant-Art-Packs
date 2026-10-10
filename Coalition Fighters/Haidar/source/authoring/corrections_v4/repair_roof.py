import os
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/corrections_v4';M=D/'maps/corrections_v4';R=D/'review/corrections_v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();v=json.loads((W/'validation.json').read_text());bpy.ops.wm.open_mainfile(filepath=v['scene']);s=bpy.context.scene
source=(W/'build_revision.py').read_text();exec(source[source.index('def read('):source.index('N=4096;')])
# Tighten the border composite to guarantee that the entire arrow inset, down
# to the last edge texel, stays byte-identical to the accepted artwork.
prior=json.loads((D/'work/alignment_v3/validation.json').read_text());a=read(v['maps']['hull']['basecolor']['path']);p=read(prior['maps']['hull']['basecolor']['path']);sc=4096/1254;arrow=np.s_[int(94*sc):int(np.ceil(139*sc)),int(121*sc):int(np.ceil(390*sc))];a[arrow]=p[arrow];v['maps']['hull']['basecolor']=save(a,'hull_basecolor');mask=read(v['maps']['hull']['border_edit_mask']['path']);mask[arrow]=0;v['maps']['hull']['border_edit_mask']=save(mask,'border_edit_mask');del a,p,mask
body=bpy.data.objects['Han_Body'];bm=body.data;uv=bm.uv_layers[v['active_uv']]
for fi in [16,17,21]:
 p=bm.polygons[fi]
 for li in p.loop_indices:
  if bm.loops[li].vertex_index==8:uv.data[li].uv.y=1-321.5/1254
f=bm.polygons[158];old=np.array([uv.data[i].uv[:] for i in f.loop_indices])*[1254,-1254]+[0,1254];xyz=np.array([bm.vertices[i].co[:] for i in f.vertices]);tri=np.column_stack((old,np.ones(3)));world=np.linalg.solve(tri,xyz)
def projection(fi):
 p=bm.polygons[fi];xz=np.array([[bm.vertices[i].co.x,bm.vertices[i].co.z,1] for i in p.vertices]);q=np.array([uv.data[i].uv[:] for i in p.loop_indices])*[1254,-1254]+[0,1254];return np.linalg.solve(xz,q)
pr=projection(16);pl=projection(21)
x0,y0,x1,y1=1100.,140.,1254.,518.;ox,oy=230.,160.;factor=.85;PN=2048;scale=4.
ix0,iy0=int(ox*scale),int(oy*scale);ix1,iy1=int(np.ceil((ox+(x1-x0)*factor)*scale)),int(np.ceil((oy+(y1-y0)*factor)*scale));sl=np.s_[iy0:iy1,ix0:ix1];yy,xx=np.mgrid[iy0:iy1,ix0:ix1].astype(np.float32);xx=((xx+.5)/scale-ox)/factor+x0;yy=((yy+.5)/scale-oy)/factor+y0
coords=np.stack((xx,yy,np.ones_like(xx)),-1)@world;left=coords[:,:,0]<.2;worldxz=np.stack((coords[:,:,0],coords[:,:,2],np.ones_like(xx)),-1);rq=worldxz@pr;lq=worldxz@pl;su=np.where(left,lq[:,:,0],rq[:,:,0]);sv=np.where(left,lq[:,:,1],rq[:,:,1])
def sample(a,xx,yy):
 n=a.shape[0];x=(xx*n/1254-.5)%n;y=(yy*n/1254-.5)%n;x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[...,None];fy=(y-y0)[...,None];return ((a[y0,x0]*(1-fx)+a[y0,(x0+1)%n]*fx)*(1-fy)+(a[(y0+1)%n,x0]*(1-fx)+a[(y0+1)%n,(x0+1)%n]*fx)*fy).astype(np.float32)
for key in ['basecolor','normal','roughness','metallic','height']:
 hull=read(v['maps']['hull'][key]['path']);local=read(v['maps']['repair'][key]['path']);q=sample(hull,su,sv)
 if key=='normal':
  nn=q*2-1;nn[:,:,1]=np.where(left,-nn[:,:,1],nn[:,:,1]);nn/=np.linalg.norm(nn,axis=-1,keepdims=True);q=nn*.5+.5
 local[sl]=q;v['maps']['repair'][key]=save(local,'local_'+key)
 print('REAR_ROOF_MAP',key,flush=True)
f.material_index=2
for li,q in zip(f.loop_indices,old):uv.data[li].uv=((ox+(q[0]-x0)*factor)/512,1-(oy+(q[1]-y0)*factor)/512)
for name,m in v['models'].items():
 o=bpy.data.objects[name]
 for p in o.data.polygons:
  m['faces'][p.index]['uv']=[o.data.uv_layers[v['active_uv']].data[i].uv[:] for i in p.loop_indices];m['faces'][p.index]['material']=1 if p.material_index==2 else 0
v['local_patches'].append(dict(name='rear_roof_triangle',part='Han_Body',faces=[158],source=[x0,y0,x1,y1],dest=[ox,oy],scale=factor,method='Sample the adjacent original roof charts in native X/Z on each side; reflected tangent normal Y on left half; no generated colour pixels.'))
v['uv_repairs'][0]['faces']=sorted(set(v['uv_repairs'][0]['faces'])|{16,17,21,158})
v['roof_chart_repair']=dict(face=158,adjacent_faces=[16,21],source_uv=old.tolist(),native_to_texture_right=pr.tolist(),native_to_texture_left=pl.tolist(),added_vertices=0,original_artwork_sampled=True)
for im in bpy.data.images:
 if im.type=='IMAGE' and im.source=='FILE' and im.users and Path(bpy.path.abspath(im.filepath)).parent==M:
  if im.packed_file:im.unpack(method='REMOVE')
  im.reload();im.pack()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=v['scene']);v['scene_sha256']=sha(v['scene']);(W/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
# Re-render changed views with the same camera positions for comparison.
s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=16
for name in ['Front','Opposite']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
cam=bpy.data.objects['Cockpit'];cam.data.type='ORTHO';cam.data.ortho_scale=2.25;s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=1000;target=body.matrix_world@Vector((0,-10,5))
for name,off in [('body_right',(3,.4,1.8)),('body_roof',(.1,0,4))]:
 cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(name+'_after.png'));bpy.ops.render.render(write_still=True)
print('HAIDAR_ROOF_REPAIR_COMPLETE',flush=True)
