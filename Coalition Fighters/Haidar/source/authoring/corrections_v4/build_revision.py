import os
from pathlib import Path
import bpy,numpy as np,json,hashlib,math
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE'])
W=D/'work/corrections_v4';M=D/'maps/corrections_v4';R=D/'review/corrections_v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v3=json.loads((D/'work/alignment_v3/validation.json').read_text());src=Path(v3['scene']);assert sha(src)==v3['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH']
before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],matrix=[list(r) for r in o.matrix_world],uvs={u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Haidar_Delivery_UV_v4'
for o in obs:
 u=o.data.uv_layers.new(name=newuv)
 for a,b in zip(u.data,o.data.uv_layers[v3['active_uv']].data):a.uv=b.uv
 o.data.uv_layers.active=u;u.active_render=True
body=bpy.data.objects['Han_Body'];cockpit=bpy.data.objects['Han_Cockpit']
for fi in [163,164,187,188,207,208,209,210]:
 for li in body.data.polygons[fi].loop_indices:body.data.uv_layers[newuv].data[li].uv.x-=2.5/1254
# Same physical span, displaced tip artwork. Register both wing tops to the
# adjoining centre wing without changing geometry or either underside.
for name in ['Han_Left_Wing_Tip','Han_Right_Wing_Tip']:
 o=bpy.data.objects[name]
 for fi in [3,4,5,6]:
  for li in o.data.polygons[fi].loop_indices:o.data.uv_layers[newuv].data[li].uv+=Vector((-2.5/1254,-2.5/1254))
# Close only small, corresponding UV corner discrepancies. Large intentional
# atlas boundaries are never welded or re-unwrapped.
minor=[]
for o in obs:
 m=o.data;uv=m.uv_layers[newuv];parent=list(range(len(uv.data)));edges={}
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def li(fi,vi):p=m.polygons[fi];return p.loop_indices[list(p.vertices).index(vi)]
 for p in m.polygons:
  if p.material_index==1:continue
  for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]]):edges.setdefault(tuple(sorted((a,b))),[]).append(p.index)
 for edge,ff in edges.items():
  if len(ff)!=2:continue
  ds=[(uv.data[li(ff[0],v)].uv-uv.data[li(ff[1],v)].uv).length*1254 for v in edge]
  if .001<max(ds)<7.5:
   for vi in edge:parent[root(li(ff[1],vi))]=root(li(ff[0],vi))
   minor.append(dict(part=o.name,faces=ff,pixel_gap_before=ds))
 groups={}
 for i in range(len(parent)):groups.setdefault(root(i),[]).append(i)
 for ids in groups.values():
  if len(ids)<2:continue
  mean=sum((uv.data[i].uv for i in ids),Vector((0,0)))/len(ids)
  for i in ids:uv.data[i].uv=mean

def read(path,scale=None):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
 if scale:im.scale(scale,scale)
 w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return a
def save(a,key):
 h,w=a.shape[:2];buf=np.ones((h,w,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None]
 im=bpy.data.images.new('Haidar v4 '+key,w,h,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel())
 p=M/f'haidar_{key}_v4.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8';im.save();bpy.data.images.remove(im)
 return dict(path=str(p),sha256=sha(p),dimensions=[w,h])
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
N=4096;Y,X=np.mgrid[:N,:N].astype(np.float32);X=(X+.5)*1254/N;Y=(Y+.5)*1254/N
def polygon(points):
 p=np.array(points);lo=np.maximum(0,np.floor((p.min(0)-7)*N/1254).astype(int));hi=np.minimum(N,np.ceil((p.max(0)+7)*N/1254).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];xx=X[sl];yy=Y[sl]
 inside=np.zeros(xx.shape,bool);dist=np.full(xx.shape,1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  e=b-a;t=np.clip(((xx-a[0])*e[0]+(yy-a[1])*e[1])/(e@e),0,1);dist=np.minimum(dist,np.hypot(xx-a[0]-t*e[0],yy-a[1]-t*e[1]));inside^=((a[1]>yy)!=(b[1]>yy))&(xx<a[0]+(yy-a[1])*e[0]/(e[1]+1e-12))
 result=np.full((N,N),-1e6,np.float32);result[sl]=np.where(inside,dist,-dist);return result
def segmentmask(points,radius,xx=X,yy=Y):
 a,b=np.array(points);e=b-a;t=np.clip(((xx-a[0])*e[0]+(yy-a[1])*e[1])/(e@e),0,1);d=np.hypot(xx-a[0]-t*e[0],yy-a[1]-t*e[1]);return 1-smooth(radius-.65,radius+.65,d)
def sample(a,xx,yy,extent=1254):
 n=a.shape[0];x=(xx/extent*n-.5)%n;y=(yy/extent*n-.5)%n;x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[...,None];fy=(y-y0)[...,None]
 return ((a[y0,x0]*(1-fx)+a[y0,(x0+1)%n]*fx)*(1-fy)+(a[(y0+1)%n,x0]*(1-fx)+a[(y0+1)%n,(x0+1)%n]*fx)*fy).astype(np.float32)

# Roof bar positions obtained by interpolation along shared native edges.
cm=cockpit.data;uv=cm.uv_layers[newuv]
def facepoint(fi,z):
 p=cm.polygons[fi];rows=[(cm.vertices[cm.loops[li].vertex_index].co.z,uv.data[li].uv.x*1254) for li in p.loop_indices];rows=sorted(set(rows));lo=min(rows);hi=max(rows);return lo[1]+(z-lo[0])/(hi[0]-lo[0])*(hi[1]-lo[1])
# Select side upper-edge vertices (same z pairs as roof) from the native face.
side=cm.polygons[42];sidepts=[(cm.vertices[cm.loops[li].vertex_index].co.z,uv.data[li].uv.x*1254) for li in side.loop_indices]
z0=min(x[0] for x in sidepts);z1=max(x[0] for x in sidepts)
u0=np.mean([u for z,u in sidepts if abs(z-z0)<.01]);u1=np.mean([u for z,u in sidepts if abs(z-z1)<.01])
roofbars=[];alignment=[]
for sideu in [490.5,555.]:
 z=z0+(sideu-u0)/(u1-u0)*(z1-z0);roofu=facepoint(40,z);roofbars.append((float(roofu),'x',2.6));alignment.append(dict(side_u=sideu,native_z=float(z),roof_u=float(roofu)))
assert 80<roofbars[1][0]<95 and 145<roofbars[0][0]<165,alignment
paths=v3['glass_outlines'];bars=[roofbars,[(490.5,'x',3.),(555.,'x',3.)],[],[],[]]
outer=np.full((N,N),-1e6,np.float32);pane=outer.copy();ribs=np.zeros((N,N),np.float32);finish=np.zeros((N,N,3),np.float32)
gen=read(D/'maps/alignment_v3/window_frame_reference_v3.png',N)
for j,(path,defs) in enumerate(zip(paths,bars)):
 d=polygon(path);bd=np.full((N,N),1e6,np.float32)
 for centre,axis,half in defs:
  q=X if axis=='x' else Y;bd=np.minimum(bd,np.abs(q-centre)-half);refcentre=85.5 if j==0 else centre
  sx=np.clip(np.rint((refcentre+(X-centre)*.6)*N/1254-.5).astype(int),0,N-1);colour=gen[np.arange(N)[:,None],sx]
  weight=(1-smooth(-.15,.15,np.abs(q-centre)-half))*smooth(-.15,.15,d);finish+=colour*weight[:,:,None]
 outer=np.maximum(outer,d);pane=np.maximum(pane,np.minimum(d,bd));ribs=np.maximum(ribs,(1-smooth(-.15,.15,bd))*smooth(-.15,.15,d))
del gen,colour,sx
foot=smooth(-4.5,-3.7,outer);glass=smooth(2.,2.6,pane)*smooth(-.15,.15,outer);inside=smooth(-.15,.15,outer);gasket=(1-ribs)*(1-glass)*inside
h=(.18*smooth(-2,0,outer)*(1-smooth(-.8,.6,pane))-.90*smooth(.0,2.5,pane))*foot
dy,dx=np.gradient(h,1254/N);norm=np.stack((-dx,dy,np.ones_like(h)),-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
line_repairs=[([[640,90],[640,150]],4.),([[659,169],[683,169]],3.6),([[625,214],[668,214]],4.),([[590,214],[612,214]],3.2),([[1035,108],[1035,149]],4.2),([[1199,91],[1199,102]],4.),([[1203,223],[1254,223]],3.5),([[1170,225],[1170,290]],4.)]
cleanup=np.zeros((N,N),np.float32)
for pts,rad in line_repairs:cleanup=np.maximum(cleanup,segmentmask(pts,rad))
borderout=polygon([[110,79],[130,57],[398,57],[401,174],[130,177],[110,155]])
borderin=polygon([[122,83],[136,72],[385,72],[388,157],[136,161],[122,150]])
border=smooth(-.25,.25,borderout)*(1-smooth(-.25,.25,borderin))
# Never composite any generated pixels into the herringbone-arrow centre.
assert not np.any(border[(Y>96)&(Y<135)&(X>125)&(X<380)])
cleanref=read(M/'cleanup_reference.png',N);borderref=read(M/'border_reference.png',N)
maps=dict(v3['maps']['hull']);arrays={};locality={}
for key in ['basecolor','normal','roughness','metallic','height','glass','seal','structure','panels','paint']:
 a=read(v3['maps']['hull'][key]['path']);b=a.copy()
 if key=='basecolor':
  clean=a*(1-inside[:,:,None])+np.array([.11,.17,.145])*inside[:,:,None];b=clean*(1-gasket[:,:,None])+np.array([.052,.068,.058])*gasket[:,:,None];b=b*(1-ribs[:,:,None])+finish;b=b*(1-cleanup[:,:,None])+cleanref*cleanup[:,:,None];b=b*(1-border[:,:,None])+borderref*border[:,:,None];allowed=np.maximum.reduce([inside,cleanup,border])
 elif key=='normal':
  b=a*(1-foot[:,:,None])+(norm*.5+.5)*foot[:,:,None];b=b*(1-cleanup[:,:,None])+np.array([.5,.5,1])*cleanup[:,:,None];v=b*2-1;v/=np.linalg.norm(v,axis=-1,keepdims=True);b=v*.5+.5;allowed=np.maximum(foot,cleanup);b[allowed==0]=a[allowed==0]
 elif key=='roughness':value=.16*glass+.86*gasket+.62*ribs;b=a*(1-inside[:,:,None])+value[:,:,None];allowed=inside
 elif key=='metallic':b=a*(1-inside[:,:,None])+.48*ribs[:,:,None];allowed=inside
 elif key=='height':b=a*(1-foot[:,:,None])+((h+4)/8)[:,:,None]*foot[:,:,None];b=b*(1-cleanup[:,:,None])+.5*cleanup[:,:,None];allowed=np.maximum(foot,cleanup)
 elif key=='glass':b=np.broadcast_to(glass[:,:,None],a.shape).copy();allowed=np.maximum(a[:,:,0],glass)
 elif key=='seal':b=np.broadcast_to((gasket+ribs)[:,:,None],a.shape).copy();allowed=np.maximum(a[:,:,0],gasket+ribs)
 elif key=='structure':b=a*(1-inside[:,:,None])+(gasket+ribs)[:,:,None];b*=1-cleanup[:,:,None];allowed=np.maximum(inside,cleanup)
 else:b=a*(1-inside[:,:,None]);b*=1-cleanup[:,:,None];allowed=np.maximum(inside,cleanup)
 assert np.array_equal(a[allowed==0],b[allowed==0]),key
 maps[key]=save(np.clip(b,0,1),'hull_'+key);locality[key]={'outside_edit_mask_identical_before_encoding':True,'edit_coverage_percent':float(100*np.count_nonzero(allowed)/allowed.size)}
 if key in ['basecolor','normal','roughness','metallic','height']:arrays[key]=b.astype(np.float32)
 print('MAP',key,flush=True)
maps['frame_mask']=save(ribs,'frame_mask');maps['glazing_edit_mask']=save(foot,'glazing_edit_mask');maps['frame_height']=save((h+4)/8,'frame_height');maps['panel_edit_mask']=save(cleanup,'panel_edit_mask');maps['border_edit_mask']=save(border,'border_edit_mask')
del cleanref,borderref,finish,norm,outer,pane,dx,dy
# A compact separate chart keeps the nose repair from erasing valid seams on
# other faces sharing the same old texels. Lower shoulder texels remain exactly
# sampled from v3, except the narrow wrapped band and its immediate join.
PN=2048;extent=512.;py,px=np.mgrid[:PN,:PN].astype(np.float32);px=(px+.5)*extent/PN;py=(py+.5)*extent/PN
patches=[dict(name='lower_shoulder',part='Han_Body',faces=[264,265,272,273],source=[340,1096,532,1324],dest=[10,10]),dict(name='nose_cap',part='Han_Cockpit',faces=[26,27],source=[340,316,532,448],dest=[230,10])]
repair={};patch_masks={};clean_small=read(M/'cleanup_reference.png')
for key,source in arrays.items():
 b=np.zeros((PN,PN,3),np.float32)
 if key=='normal':b[:]=[.5,.5,1]
 if key in ['height','roughness']:b[:]=.5
 for p in patches:
  x0,y0,x1,y1=p['source'];ox,oy=p['dest'];xx=px-ox+x0;yy=py-oy+y0;region=(px>=ox)&(px<ox+x1-x0)&(py>=oy)&(py<oy+y1-y0);sl=np.s_[int(oy*4):int((oy+y1-y0)*4),int(ox*4):int((ox+x1-x0)*4)];xx=xx[sl];yy=yy[sl];q=sample(source,xx,yy)
  if p['name']=='nose_cap':
   mask=np.maximum(segmentmask([[471,320],[471,443]],4.,xx,yy),segmentmask([[345,438],[526,438]],5.2,xx,yy))
   if key=='basecolor':q=q*(1-mask[:,:,None])+sample(clean_small,xx,yy)*mask[:,:,None]
   elif key=='normal':q=q*(1-mask[:,:,None])+np.array([.5,.5,1])*mask[:,:,None]
   elif key=='height':q=q*(1-mask[:,:,None])+.5*mask[:,:,None]
  else:
   # Continued circumferential band: avoid V=1 wrap into unrelated upper hull.
   band=smooth(464,468,xx)*(1-smooth(493,497,xx));top=1315.1-(xx-348.4)/176.6*28.7;upper=1164.6-(xx-348.4)/176.6*22.6;sy=upper+(yy-top);bandq=sample(source,xx,sy);q=q*(1-band[:,:,None])+bandq*band[:,:,None]
   # At the upper/lower shared edge copy only a 2px join strip, keeping fixtures.
   join=1-smooth(1.0,3.5,np.abs(yy-top));jq=sample(source,xx,upper+(yy-top));q=q*(1-join[:,:,None])+jq*join[:,:,None]
   mask=np.maximum(band,join)
  if key=='normal':nn=q*2-1;nn/=np.linalg.norm(nn,axis=-1,keepdims=True);q=nn*.5+.5
  b[sl]=q
  if key=='basecolor':patch_masks[p['name']]=dict(edit_fraction=float(np.count_nonzero(mask)/mask.size),source=p['source'],dest=p['dest'])
 repair[key]=save(np.clip(b,0,1),'local_'+key);print('LOCAL_MAP',key,flush=True)
del arrays,clean_small
for p in patches:
 o=bpy.data.objects[p['part']];uv=o.data.uv_layers[newuv];x0,y0,x1,y1=p['source'];ox,oy=p['dest']
 for fi in p['faces']:
  face=o.data.polygons[fi];face.material_index=2
  for li in face.loop_indices:
   u,v=uv.data[li].uv;xx=u*1254;yy=(1-v)*1254;uv.data[li].uv=((xx-x0+ox)/extent,1-(yy-y0+oy)/extent)

def material(label,mm):
 mat=bpy.data.materials.new(label);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0])
 for key in ['basecolor','roughness','metallic','normal']:
  im=bpy.data.images.load(mm[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();tx=n.new('ShaderNodeTexImage');tx.image=im;l.new(uv.outputs[0],tx.inputs[0])
  if key=='normal':nm=n.new('ShaderNodeNormalMap');nm.uv_map=newuv;l.new(tx.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
  else:l.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 return mat
hmat=material('Haidar_Local_Corrections_v4',maps);pmat=material('Haidar_Six_Face_Local_Repairs_v4',repair)
for o in obs:
 o.data.materials[0]=hmat
 if len(o.data.materials)<3:o.data.materials.append(pmat)
 else:o.data.materials[2]=pmat
for q in list(bpy.data.materials):
 if q.users==0:bpy.data.materials.remove(q)
for q in list(bpy.data.images):
 if q.users==0:bpy.data.images.remove(q)
models={};repairs=[];aspects=[]
for o in obs:
 m=o.data;b=before[o.name]
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals] and b['matrix']==[list(row) for row in o.matrix_world]
 for name,values in b['uvs'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 changed=[]
 for p in m.polygons:
  if max((m.uv_layers[newuv].data[i].uv-m.uv_layers['Haidar_Delivery_UV_v1'].data[i].uv).length for i in p.loop_indices)>1e-7 or p.material_index==2:changed.append(p.index)
  if p.material_index==1:continue
  pts=np.array([m.vertices[i].co[:] for i in p.vertices]);e=pts[1:]-pts[0];fn=np.cross(*e);fn/=np.linalg.norm(fn);t=e[0]/np.linalg.norm(e[0]);xy=e@np.stack((t,np.cross(fn,t)),axis=1);q=np.array([m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices]);sv=np.linalg.svd(np.linalg.solve(xy,q[1:]-q[0]),compute_uv=False);aspects.append(float(sv[0]/sv[1]))
 if changed:repairs.append(dict(part=o.name,faces=changed,reason='Local shoulder, wing and panel-corner registration; six face-local charts preserve shared original artwork'))
 models[o.name]={'part_index':o['native_part_index'],'vertices':b['vertices'],'faces':[dict(id=p.index,vertices=list(p.vertices),uv=[m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices],material=1 if p.material_index==2 else 0,hidden=p.material_index==1) for p in m.polygons]}
assert max(aspects)<3.1,max(aspects)
s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=20;s.camera=bpy.data.objects['Front'];s.render.threads_mode='FIXED';s.render.threads=4
bpy.context.preferences.filepaths.save_version=0;scene=D/'haidar_worn_pbr_v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==v3['scene_sha256']
report=dict(source=str(src),source_sha256=v3['scene_sha256'],scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,parts=6,stored_triangles=478,original_geometry_normals_and_uv_layers_preserved=True,uv_repairs=repairs,minor_joins=minor,max_visible_uv_anisotropy=max(aspects),maps={'hull':maps,'repair':repair},models=models,map_locality=locality,glass_outlines=paths,frame_layout=bars,roof_side_alignment=alignment,line_repairs=line_repairs,local_patches=patches,patch_masks=patch_masks,glazing=dict(frame_height=.18,glass_depth=-.90,bevel_width_master_pixels=2.5,glass_interiors_flat=True,front_and_rear_dividers_removed=True,roof_struts=2,roof_struts_match_side_z=True),runtime_visual_validation='pending_user_review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('HAIDAR_V4_VALIDATED',flush=True)
for name in ['Front','Opposite']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
cam=bpy.data.objects['Cockpit'];cam.data.type='ORTHO';cam.data.ortho_scale=2.25;s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=1000;s.cycles.samples=16
target=body.matrix_world@Vector((0,-10,5))
for name,off in [('body_right',(3,.4,1.8)),('body_roof',(.1,0,4)),('body_belly',(2.2,.4,-2.6))]:
 cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(name+'_after.png'));bpy.ops.render.render(write_still=True)
cam.data.ortho_scale=1.4;s.render.resolution_x=1200;s.render.resolution_y=900;target=cockpit.matrix_world@Vector((0,-35,620))
for name,off in [('canopy_right',(1.5,1,.95)),('canopy_left',(-1.5,1,.95)),('canopy_roof',(0,.25,2))]:
 cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('HAIDAR_V4_RENDERS_COMPLETE',flush=True)
