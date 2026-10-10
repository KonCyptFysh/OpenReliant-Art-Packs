import os
from pathlib import Path
import bpy, numpy as np, json, hashlib, math
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE'])
W=D/'work/alignment_v3'; M=D/'maps/alignment_v3'; R=D/'review/alignment_v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v1=json.loads((D/'work/reconstruction_v1/validation.json').read_text())
v2=json.loads((D/'work/seams_v2/validation.json').read_text())
src=Path(json.loads((W/'prior_project_state.json').read_text())['latest_scene'])
assert sha(src)==v2['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src)); s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH']
before={o.name:{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'normals':[list(n.vector) for n in o.data.corner_normals],'matrix':[list(row) for row in o.matrix_world],'uvs':{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers}} for o in obs}
newuv='Haidar_Delivery_UV_v3'
for o in obs:
 m=o.data; u=m.uv_layers.new(name=newuv)
 for a,b in zip(u.data,m.uv_layers['Haidar_Delivery_UV_v1'].data):a.uv=b.uv
 m.uv_layers.active=u;u.active_render=True
 for p in m.polygons:p.material_index=1 if p.index in o['native_hidden_faces'] else 0
 while len(m.materials)>2:m.materials.pop(index=len(m.materials)-1)

# Retain all original charts and artwork. Correct only the longitudinal
# registration of the existing circumferential shoulder band.
body=bpy.data.objects['Han_Body']; m=body.data; u=m.uv_layers[newuv]
band_faces=[257]+list(range(262,270))+[272,273]
back=min(m.vertices[v].co.z for fi in band_faces for v in m.polygons[fi].vertices)
front=max(m.vertices[v].co.z for fi in band_faces for v in m.polygons[fi].vertices)
for fi in band_faces:
 for li in m.polygons[fi].loop_indices:
  z=m.vertices[m.loops[li].vertex_index].co.z
  u.data[li].uv.x=(348.4+(525.-348.4)*(z-back)/(front-back))/1254

# Close existing sub-pixel split corners only in the reported nose/shoulder
# regions. No unwrap, new projection, replacement panels, or layout invention.
minor=[]
for o,selection in [(body,set(band_faces)),(bpy.data.objects['Han_Cockpit'],set(range(38)))]:
 m=o.data; uv=m.uv_layers[newuv]; parent=list(range(len(uv.data))); edges={}
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def li(fi,vi):p=m.polygons[fi];return p.loop_indices[list(p.vertices).index(vi)]
 for p in m.polygons:
  if p.material_index:continue
  for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]]):edges.setdefault(tuple(sorted((a,b))),[]).append(p.index)
 for edge,ff in edges.items():
  if len(ff)!=2 or not set(ff)<=selection:continue
  ds=[(uv.data[li(ff[0],v)].uv-uv.data[li(ff[1],v)].uv).length*1254 for v in edge]
  if max(ds)<1.5 and max(ds)>.001:
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
 w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a)
 a=a.reshape(h,w,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return a
def save(a,key):
 n=a.shape[0];buf=np.ones((n,n,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None]
 im=bpy.data.images.new('Haidar v3 '+key,n,n,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel())
 p=M/f'haidar_{key}_v3.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8';im.save();bpy.data.images.remove(im)
 return dict(path=str(p),sha256=sha(p),dimensions=[n,n])
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
N=4096;Y,X=np.mgrid[:N,:N].astype(np.float32);X=(X+.5)*1254/N;Y=(Y+.5)*1254/N
def polygon(points):
 p=np.array(points);lo=np.maximum(0,np.floor((p.min(0)-7)*N/1254).astype(int));hi=np.minimum(N,np.ceil((p.max(0)+7)*N/1254).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];xx=X[sl];yy=Y[sl]
 inside=np.zeros(xx.shape,bool);dist=np.full(xx.shape,1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  e=b-a;t=np.clip(((xx-a[0])*e[0]+(yy-a[1])*e[1])/(e@e),0,1)
  dist=np.minimum(dist,np.hypot(xx-a[0]-t*e[0],yy-a[1]-t*e[1]))
  inside^=((a[1]>yy)!=(b[1]>yy))&(xx<a[0]+(yy-a[1])*e[0]/(e[1]+1e-12))
 result=np.full((N,N),-1e6,np.float32);result[sl]=np.where(inside,dist,-dist);return result

# Explicit frame geometry in atlas space, traced from the original artwork.
# Glass remains planar; only the metal chamfer/gasket carries the height change.
paths=v2['glass_outlines']
bars=[[(84.,'x',2.6),(100.5,'x',2.6),(119.5,'x',2.6)],[(490.5,'x',3.0),(555.,'x',3.0)],[],[(998.,'y',2.8)],[(1164.,'y',2.8)]]
outer=np.full((N,N),-1e6,np.float32);pane=outer.copy();ribs=np.zeros((N,N),np.float32)
finish=np.zeros((N,N,3),np.float32)
gen=read(M/'window_frame_reference_v3.png',N)
for j,(path,defs) in enumerate(zip(paths,bars)):
 d=polygon(path);cut=d.copy();bd=np.full((N,N),1e6,np.float32)
 for centre,axis,half in defs:
  q=X if axis=='x' else Y;bd=np.minimum(bd,np.abs(q-centre)-half)
  # Use the AI-authored steel finish, registered to each old bar. The tiny
  # centre roof upright samples the same finish as its two neighbours.
  refcentre=85.5 if j==0 else centre
  if axis=='x':
   sx=np.clip(np.rint((refcentre+(X-centre)*.6)*N/1254-.5).astype(int),0,N-1);colour=gen[np.arange(N)[:,None],sx]
  else:
   sy=np.clip(np.rint((centre+(Y-centre)*.6)*N/1254-.5).astype(int),0,N-1);colour=gen[sy,np.arange(N)[None,:]]
  weight=(1-smooth(-.15,.15,np.abs(q-centre)-half))*smooth(-.15,.15,d)
  finish+=colour*weight[:,:,None]
 cut=np.minimum(cut,bd);outer=np.maximum(outer,d);pane=np.maximum(pane,cut)
 ribs=np.maximum(ribs,(1-smooth(-.15,.15,bd))*smooth(-.15,.15,d))
foot=smooth(-4.5,-3.7,outer)
glass=smooth(2.0,2.6,pane)*smooth(-.15,.15,outer)
inside=smooth(-.15,.15,outer)
gasket=(1-ribs)*(1-glass)*inside
frame=inside*(1-smooth(-.25,.25,pane))
# Height units refer to the 1254-pixel native authoring atlas. Smooth analytic
# chamfers are evaluated directly at 4K, with no albedo-derived bump.
h=.18*smooth(-2,0,outer)*(1-smooth(-.8,.6,pane))-.90*smooth(.0,2.5,pane)
h*=foot
dy,dx=np.gradient(h,1254/N);norm=np.stack((-dx,dy,np.ones_like(h)),-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
normal_weight=foot
oldmaps=v1['maps']['hull'];old2=v2['maps']['hull'];maps=dict(oldmaps);locality={}
for key in ['basecolor','normal','roughness','metallic','height','glass','seal','structure','panels','paint']:
 a=read(oldmaps[key]['path']);b=a.copy()
 if key=='basecolor':
  clean=a*(1-inside[:,:,None])+np.array([.11,.17,.145])*inside[:,:,None];b=clean*(1-gasket[:,:,None])+np.array([.052,.068,.058])*gasket[:,:,None]
  # No generated pixels survive outside the internal steel ribs.
  b=b*(1-ribs[:,:,None])+finish
  allowed=inside
 elif key=='normal':
  b=a*(1-normal_weight[:,:,None])+(norm*.5+.5)*normal_weight[:,:,None]
  v=b*2-1;v/=np.linalg.norm(v,axis=-1,keepdims=True);b=v*.5+.5;b[normal_weight==0]=a[normal_weight==0];allowed=foot
 elif key=='roughness':
  value=.16*glass+.86*gasket+.62*ribs
  b=a*(1-inside[:,:,None])+value[:,:,None];allowed=inside
 elif key=='metallic':b=a*(1-inside[:,:,None])+.48*ribs[:,:,None];allowed=inside
 elif key=='height':b=a*(1-foot[:,:,None])+((h+4)/8)[:,:,None]*foot[:,:,None];allowed=foot
 elif key=='glass':b=np.broadcast_to(glass[:,:,None],a.shape).copy();allowed=np.maximum(a[:,:,0],glass)
 elif key=='seal':b=np.broadcast_to((gasket+ribs)[:,:,None],a.shape).copy();allowed=np.maximum(a[:,:,0],gasket+ribs)
 elif key=='structure':b=a*(1-inside[:,:,None])+(gasket+ribs)[:,:,None];allowed=inside
 else:b=a*(1-inside[:,:,None]);allowed=inside
 assert np.array_equal(a[allowed==0],b[allowed==0]),key
 maps[key]=save(np.clip(b,0,1),'hull_'+key)
 locality[key]={'outside_allowed_footprint_identical_before_encoding':True,'pixel_coverage_percent':float(100*np.count_nonzero(allowed)/allowed.size)}
 print('MAP',key,flush=True)
maps['frame_mask']=save(ribs,'frame_mask');maps['glazing_edit_mask']=save(foot,'glazing_edit_mask');maps['frame_height']=save((h+4)/8,'frame_height')

mat=bpy.data.materials.new('Haidar_Restored_Hull_Framed_Glazing_v3');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
uv=n.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0])
for key in ['basecolor','roughness','metallic','normal']:
 im=bpy.data.images.load(maps[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();tx=n.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;l.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=n.new('ShaderNodeNormalMap');nm.uv_map=newuv;l.new(tx.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
 else:l.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
for o in obs:o.data.materials[0]=mat
for q in list(bpy.data.materials):
 if q.users==0:bpy.data.materials.remove(q)
for q in list(bpy.data.images):
 if q.users==0:bpy.data.images.remove(q)
models={};repairs=[];aspects=[];uv_delta=[]
for o in obs:
 m=o.data;b=before[o.name]
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals] and b['matrix']==[list(row) for row in o.matrix_world]
 for name,values in b['uvs'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 changed=[]
 for p in m.polygons:
  delta=max((m.uv_layers[newuv].data[i].uv-m.uv_layers['Haidar_Delivery_UV_v1'].data[i].uv).length*1254 for i in p.loop_indices)
  if delta>1e-5:changed.append(p.index);uv_delta.append(dict(part=o.name,face=p.index,max_master_pixel_shift=delta))
  if p.material_index:continue
  pts=np.array([m.vertices[i].co[:] for i in p.vertices]);e=pts[1:]-pts[0];fn=np.cross(*e);fn/=np.linalg.norm(fn);t=e[0]/np.linalg.norm(e[0]);xy=e@np.stack((t,np.cross(fn,t)),axis=1);q=np.array([m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices]);sv=np.linalg.svd(np.linalg.solve(xy,q[1:]-q[0]),compute_uv=False);aspects.append(float(sv[0]/sv[1]))
 if changed:repairs.append(dict(part=o.name,faces=changed,reason='Align existing shoulder-band longitudinal coordinates; original atlas layout and artwork retained'))
 models[o.name]={'part_index':o['native_part_index'],'vertices':b['vertices'],'faces':[dict(id=p.index,vertices=list(p.vertices),uv=[m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices],material=0,hidden=p.material_index==1) for p in m.polygons]}
print('UV_METRICS',max(aspects),max(q['max_master_pixel_shift'] for q in uv_delta),flush=True)
assert max(aspects)<3 and max(q['max_master_pixel_shift'] for q in uv_delta)<13
s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];s.render.threads_mode='FIXED';s.render.threads=4
bpy.context.preferences.filepaths.save_version=0;scene=D/'haidar_worn_pbr_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==v2['scene_sha256']
report=dict(source=str(src),source_sha256=v2['scene_sha256'],scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,parts=6,stored_triangles=478,original_geometry_normals_and_uv_layers_preserved=True,uv_repairs=repairs,uv_pixel_shifts=uv_delta,minor_joins=minor,max_visible_uv_anisotropy=max(aspects),maps={'hull':maps},models=models,map_locality=locality,glass_outlines=paths,frame_layout=bars,glazing=dict(frame_height=.18,glass_depth=-.90,bevel_width_master_pixels=2.5,glass_interiors_flat=True,old_internal_divider_locations_restored=True,baked_reflections_removed=True),artwork_restoration='All 51 rejected nose/collar faces use their original material and original UV charts again, with only local shoulder-band alignment. No replacement metal or new panel layout.',runtime_visual_validation='pending_user_review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('HAIDAR_V3_VALIDATED',len(uv_delta),flush=True)
for name in ['Front','Opposite']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
cam=bpy.data.objects['Cockpit'];cam.data.type='ORTHO';cam.data.ortho_scale=1.40;s.render.resolution_x=1200;s.render.resolution_y=900
target=bpy.data.objects['Han_Cockpit'].matrix_world@Vector((0,-35,620))
for name,offset in [('canopy_right',(1.5,1.0,.95)),('canopy_left',(-1.5,1.0,.95)),('canopy_roof',(0,.25,2))]:
 cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('HAIDAR_V3_RENDERS_COMPLETE',flush=True)
