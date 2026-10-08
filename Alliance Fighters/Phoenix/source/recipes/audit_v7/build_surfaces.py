import os
import bpy,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v7';R=D/'review/audit_v7/after';M=D/'maps/audit_v7';N=4096;S=N/1254
M.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();state=json.loads((D.parent/'project_state.json').read_text());src=Path(state['latest_scene']);assert src.name=='phoenix_worn_pbr_v6.blend';sourcehash=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update();old=json.loads((D/'work/audit_v6/validation.json').read_text());reg=json.loads((W/'regions.json').read_text());oldname=old['active_uv'];newname='Phoenix_Delivery_UV_v7'
before={o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'n':[list(q.vector) for q in o.data.corner_normals],'uvs':{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},'materials':[p.material_index for p in o.data.polygons]} for o in s.objects if o.type=='MESH'}
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return a

def save(a,key,family):
 h,w=a.shape[:2];buf=np.ones((h,w,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Phoenix v7 '+family+' '+key,w,h,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());p=M/f'phoenix_{family}_{key}_4k_v7.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if key=='basecolor' else '16';im.save();bpy.data.images.remove(im);return {'path':str(p),'sha256':sha(p)}

def bind(mat,key,rec):
 im=bpy.data.images.load(rec['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();mat.node_tree.nodes['Delivered '+key].image=im

def poly(X,Y,p):
 p=np.array(p);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1));d=np.full(X.shape,1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d

def capsule(X,Y,a,b,r):
 a=np.array(a);v=np.array(b)-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/(v@v),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
# Replace only the three misregistered structural relief regions. Atlas colour,
# canopy maps, markings and unrelated normals remain byte-equivalent outside the mask.
x0,y0,x1,y1=[round(q*S) for q in [242,690,484,1086]];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/S;Y=(yy+.5)/S
old_dist=np.maximum(capsule(X,Y,[260,778],[260,944],11),capsule(X,Y,[309,710],[309,903],10));old_dist=np.maximum(old_dist,poly(X,Y,[[303,988],[474,822],[478,928],[305,1077]]));edit=smooth(-5,-2,old_dist);opening=np.zeros_like(X);fin=np.zeros_like(X);height=np.zeros_like(X);dmax=np.full_like(X,-1000.)
for item in [reg['intake'],*reg['vents']]:
 d=poly(X,Y,item['polygon']);dmax=np.maximum(dmax,d);edit=np.maximum(edit,smooth(-5,-2,d));inside=smooth(0,1.6,d);ridge=np.zeros_like(X)
 for x in item['fin_centres']:ridge=np.maximum(ridge,1-smooth(item['half_width']*.3,item['half_width'],np.abs(X-x)))
 ridge*=smooth(2,4,d);height+=-item['depth']*inside+item['fin_height']*ridge;opening=np.maximum(opening,inside);fin=np.maximum(fin,ridge)
dy,dx=np.gradient(height,1/S);normal=np.stack((-dx,dy,np.ones_like(height)),-1);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
# Force neutral normals at and beyond the opening perimeter, avoiding
# neighbouring-frame recesses from interpolation of the height derivative.
normal=normal*(dmax>0)[:,:,None]+np.array([0,0,1])*(dmax<=0)[:,:,None]
colour=load(Path(old['maps']['basecolor']['path']));rgb=colour[y0:y1,x0:x1];lum=rgb.mean(2);mx=rgb.max(2);mn=rgb.min(2);sat=(mx-mn)/(mx+1e-6);bronze=smooth(1.1,1.32,rgb[:,:,0]/(rgb[:,:,1]+1e-6))*smooth(1.1,1.36,rgb[:,:,1]/(rgb[:,:,2]+1e-6));paint=smooth(.09,.24,sat)*(1-bronze);frame_metal=np.maximum((1-paint)*smooth(.15,.45,lum)*.88,bronze*.75);frame_rough=.84*(1-frame_metal)+.50*frame_metal
maps=dict(old['maps']);mainmat=bpy.data.objects['Phoenix_Body'].data.materials[0]
for key in ['normal','roughness','metallic','height','structure','fins']:
 a=load(Path(old['maps'][key]['path']));q=a[y0:y1,x0:x1]
 if key=='normal':val=normal*.5+.5
 elif key=='height':val=(height+20)/32
 elif key=='structure':val=opening
 elif key=='fins':val=fin
 elif key=='roughness':val=frame_rough*(1-opening)+(.87-.37*fin)*opening
 else:val=frame_metal*(1-opening)+(.10+.72*fin)*opening
 if val.ndim==2:val=val[:,:,None]
 a[y0:y1,x0:x1]=q*(1-edit[:,:,None])+val*edit[:,:,None];maps[key]=save(a,key,'hull')
 if key in ['normal','roughness','metallic']:bind(mainmat,key,maps[key])
 del a
mask=np.zeros((N,N),np.float32);mask[y0:y1,x0:x1]=edit;edit_rec=save(mask,'relief_edit_mask','hull');mask[:]=0;mask[y0:y1,x0:x1]=(dmax>0);opening_rec=save(mask,'opening_mask','hull');del mask,colour
print('INTAKE_VENT_RELIEF_ALIGNED',flush=True)
# Full-area native-face bake for the belly and intersecting bronze nose skins.
selected={'Phoenix_Body':set(reg['body_faces']),'Phoenix_Cockpit':set([1,6,24,25]+list(range(26,34))+[40,44,45,46,47,50,51,56,57,58,62,63]+list(range(65,69)))}
frames={};positions={}
for o in s.objects:
 if o.type!='MESH':continue
 m=o.data;u=m.uv_layers.new(name=newname,do_init=True);m.uv_layers.active=u;u.active_render=True
 if o.name not in selected:continue
 positions[o.name]=np.array([list(o.matrix_world@v.co) for v in m.vertices]);rot=np.array(o.matrix_world.to_3x3());normrot=np.array(o.matrix_world.to_3x3().inverted().transposed())
 def collect(uvname):
  m.calc_tangents(uvmap=uvname);out={}
  for fi in selected[o.name]:
   p=m.polygons[fi];t=np.array([list(m.loops[k].tangent) for k in p.loop_indices])@rot.T;n=np.array([list(m.corner_normals[k].vector) for k in p.loop_indices])@normrot.T;t/=np.linalg.norm(t,axis=1,keepdims=True);n/=np.linalg.norm(n,axis=1,keepdims=True);out[fi]=(t,n,np.array([m.loops[k].bitangent_sign for k in p.loop_indices]))
  return out
 frames[o.name]={oldname:collect(oldname)};u=m.uv_layers[newname]
 if o.name=='Phoenix_Body':
  for fi in selected[o.name]:
   for k in m.polygons[fi].loop_indices:
    x,y,z=positions[o.name][m.loops[k].vertex_index];u.data[k].uv=(.25+.60*x,.035+.55*(y+.95))
 else:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.context.tool_settings.mesh_select_mode=(False,False,True)
  for p in m.polygons:p.select=p.index in selected[o.name]
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.uv.smart_project(angle_limit=math.radians(55),island_margin=.018,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');m=o.data;u=m.uv_layers[newname]
  for fi in selected[o.name]:
   for k in m.polygons[fi].loop_indices:
    q=u.data[k].uv.copy();u.data[k].uv=(.525+.45*q.x,.05+.90*q.y)
  m.update()
 frames[o.name][newname]=collect(newname)
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type in ['UVMAP','NORMAL_MAP'] and node.uv_map==oldname:node.uv_map=newname
source={key:load(Path(maps[key]['path'])) for key in ['basecolor','normal','roughness','metallic']}
def crop(box):
 a,b,c,d=[round(v*S) for v in box];return source['basecolor'][b:d,a:c].copy()
steel=crop(reg['steel_donor']);bronze=crop(reg['bronze_donor'])
def sample(im,q):
 h,w=im.shape[:2];x=(q[:,0]%1)*w-.5;y=(1-q[:,1]%1)*h-.5;ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=(x-ix)[:,None];fy=(y-iy)[:,None];return (im[iy%h,ix%w]*(1-fx)+im[iy%h,(ix+1)%w]*fx)*(1-fy)+(im[(iy+1)%h,ix%w]*(1-fx)+im[(iy+1)%h,(ix+1)%w]*fx)*fy

def mirrored(im,q):return sample(im,.002+.996*(1-np.abs((q%2)-1)))

def wear(p,kind,gn):
 if kind=='belly':
  q=np.column_stack((p[:,0]*9.0+.25,p[:,1]*5.5+.37));return .85*mirrored(steel,q)+.15*mirrored(steel,q@np.array([[.8,.6],[-.6,.8]])+.3)
 p=p.copy();p[:,0]=np.abs(p[:,0]);p[:,1]-=1.30;p[:,2]+=.20;weights=np.abs(gn)**4;weights/=np.maximum(weights.sum(1,keepdims=True),1e-8);out=np.zeros_like(p)
 for ax,(u,v) in enumerate([(1,2),(0,2),(0,1)]):
  q=np.column_stack((p[:,u]*11.0+.17,p[:,v]*14.0+.31));col=.85*mirrored(bronze,q)+.15*mirrored(bronze,q@np.array([[.8,.6],[-.6,.8]])+.37);out+=col*weights[:,ax,None]
 return out
body=bpy.data.objects['Phoenix_Body'];bm=body.data;edge_counts={}
for fi in selected['Phoenix_Body']:
 p=bm.polygons[fi]
 for a,b in zip(p.vertices,list(p.vertices[1:])+[p.vertices[0]]):edge=tuple(sorted((a,b)));edge_counts[edge]=edge_counts.get(edge,0)+1
boundaries=[positions['Phoenix_Body'][list(e),:2] for e,c in edge_counts.items() if c==1]
def detailing(p,kind):
 if kind=='nose':
  d=np.abs(p[:,1]-1.575);cut=1-smooth(.00055,.0021,d);return -.0009*cut,cut,np.zeros(len(p)),np.zeros(len(p))
 cut=np.zeros(len(p));x=p[:,0];y=p[:,1]
 for c in [-.73,-.42,-.10,.23,.565,.662]:cut=np.maximum(cut,1-smooth(.0008,.0029,np.abs(y-c)))
 for c in [-.14,0,.14]:cut=np.maximum(cut,1-smooth(.0006,.0023,np.abs(x-c)))
 edge=np.full(len(p),10.)
 for a,b in boundaries:
  v=b-a;t=np.clip(((p[:,:2]-a)@v)/(v@v),0,1);edge=np.minimum(edge,np.linalg.norm(p[:,:2]-a-t[:,None]*v,axis=1))
 cut=np.maximum(cut,1-smooth(.0010,.003,edge));band=smooth(.565,.572,y)*(1-smooth(.655,.662,y));bolts=np.zeros(len(p))
 for cx in [-.07,.07]:
  rr=np.hypot(x-cx,y-.614);bolts=np.maximum(bolts,(1-smooth(.0028,.0052,rr)))
 return -.0009*cut-.00045*bolts,cut,band,bolts
out={k:np.zeros((N,N,3),np.float32) for k in ['basecolor','normal','roughness','metallic','height']};out['normal'][:]=(.5,.5,1);coverage=np.zeros((N,N),bool);regions=np.zeros((N,N),np.uint8);face_reports=[]
for name,ids in selected.items():
 o=bpy.data.objects[name];m=o.data;posall=positions[name];gnorm=np.zeros_like(posall)
 for polyface in m.polygons:
  if polyface.material_index==1:continue
  pv=posall[list(polyface.vertices)];fn=np.cross(pv[1]-pv[0],pv[2]-pv[0])
  for vi in polyface.vertices:gnorm[vi]+=fn
 gnorm/=np.maximum(np.linalg.norm(gnorm,axis=1,keepdims=True),1e-9)
 kind='belly' if name=='Phoenix_Body' else 'nose'
 for fi in sorted(ids):
  p=m.polygons[fi];uv=np.array([list(m.uv_layers[newname].data[k].uv) for k in p.loop_indices]);prev=np.array([list(m.uv_layers[oldname].data[k].uv) for k in p.loop_indices]);xy=np.column_stack((uv[:,0]*N,(1-uv[:,1])*N));lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N,np.ceil(xy.max(0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];points=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));b=(points-xy[0])@np.linalg.inv(np.column_stack((xy[1]-xy[0],xy[2]-xy[0]))).T;b=np.column_stack((1-b.sum(1),b));inside=b.min(1)>=-1e-7;b=b[inside];rx=xx.ravel()[inside];ry=yy.ravel()[inside];dup=coverage[ry,rx];assert not np.any(dup) or np.max(b[dup].min(1))<.00005,(name,fi,'overlap');b=b[~dup];rx=rx[~dup];ry=ry[~dup];coverage[ry,rx]=True;regions[ry,rx]=1 if kind=='belly' else 2;pos=b@posall[list(p.vertices)];oldq=b@prev;blend=np.ones(len(pos)) if kind=='belly' else smooth(1.33,1.44,pos[:,1])
  def basis(data):
   ts,ns,sign=data;n=b@ns;n/=np.linalg.norm(n,axis=1,keepdims=True);t=b@ts;t-=n*np.sum(n*t,axis=1,keepdims=True);t/=np.linalg.norm(t,axis=1,keepdims=True);return t,np.cross(n,t)*np.sign(b@sign)[:,None],n
  ot,ob,on=basis(frames[name][oldname][fi]);nt,nb,nn=basis(frames[name][newname][fi]);oldnormal=sample(source['normal'],oldq)*2-1;wn=ot*oldnormal[:,0,None]+ob*oldnormal[:,1,None]+on*oldnormal[:,2,None];h,cut,band,bolts=detailing(pos,kind);grad=np.zeros_like(pos);eps=.00008
  for ax in range(3):
   off=np.zeros(3);off[ax]=eps;grad[:,ax]=(detailing(pos+off,kind)[0]-detailing(pos-off,kind)[0])/(2*eps)
  grad-=nn*np.sum(grad*nn,axis=1,keepdims=True);newnormal=nn-grad;newnormal/=np.linalg.norm(newnormal,axis=1,keepdims=True);wn=wn*(1-blend[:,None])+newnormal*blend[:,None];wn/=np.linalg.norm(wn,axis=1,keepdims=True);tangent=np.column_stack((np.sum(wn*nt,1),np.sum(wn*nb,1),np.sum(wn*nn,1)));tangent/=np.linalg.norm(tangent,axis=1,keepdims=True)
  gn=b@gnorm[list(p.vertices)];gn/=np.maximum(np.linalg.norm(gn,axis=1,keepdims=True),1e-9);col=wear(pos,kind,gn)
  if kind=='belly':col*=np.array([.93,1.,.91]);col*=1+.48*band[:,None];col*=1-.78*cut[:,None];col*=1-.65*bolts[:,None];rough=.65-.14*band;metal=.70+.16*band
  else:col*=1-.68*cut[:,None];rough=np.full(len(pos),.71);metal=np.full(len(pos),.65)
  rough=rough*(1-cut)+.87*cut;metal*=1-.90*cut;col=sample(source['basecolor'],oldq)*(1-blend[:,None])+col*blend[:,None]
  for k,val in [('basecolor',col),('normal',tangent*.5+.5),('roughness',sample(source['roughness'],oldq)*(1-blend[:,None])+rough[:,None]*blend[:,None]),('metallic',sample(source['metallic'],oldq)*(1-blend[:,None])+metal[:,None]*blend[:,None]),('height',((h*blend+.004)/.008)[:,None])]:out[k][ry,rx]=val
  face_reports.append({'object':name,'face':fi,'kind':kind,'pixels':len(rx),'blend_min':float(blend.min()),'blend_max':float(blend.max())});print('BAKED',name,fi,len(rx),flush=True)
# Flood fill island padding for filtering. This does not change atlas coverage.
idx=np.full((N,N),-1,np.int32);idx[coverage]=np.flatnonzero(coverage)
for _ in range(16):
 updated=idx.copy()
 for ax,sh in [(0,1),(0,-1),(1,1),(1,-1)]:
  q=np.roll(idx,sh,ax);take=(updated<0)&(q>=0);updated[take]=q[take]
 idx=updated
pad=(idx>=0)&~coverage;repair_maps={}
for key,a in out.items():a[pad]=a.reshape(-1,3)[idx[pad]];repair_maps[key]=save(a,key,'surfaces')
regmap=np.stack((regions==1,regions==2,np.zeros_like(regions)),axis=-1).astype(np.float32);region_rec=save(regmap,'regions','surfaces')
mat=mainmat.copy();mat.name='Phoenix_Continuous_Surfaces_PBR_v7'
for key in ['basecolor','normal','roughness','metallic']:bind(mat,key,repair_maps[key])
for name,ids in selected.items():
 m=bpy.data.objects[name].data;m.materials.append(mat);assert len(m.materials)==3
 for fi in ids:m.polygons[fi].material_index=2
models={};changed=[]
for name,b in before.items():
 o=bpy.data.objects[name];m=o.data;assert b['v']==[list(v.co) for v in m.vertices] and b['f']==[list(p.vertices) for p in m.polygons] and b['n']==[list(q.vector) for q in m.corner_normals]
 for key,q in b['uvs'].items():assert q==[list(v.uv) for v in m.uv_layers[key].data]
 for p in m.polygons:
  if p.index not in selected.get(name,set()):
   assert p.material_index==b['materials'][p.index];assert all(tuple(m.uv_layers[newname].data[k].uv)==tuple(m.uv_layers[oldname].data[k].uv) for k in p.loop_indices)
  else:changed.append({'object':name,'face':p.index})
 models[name]={'vertices':b['v'],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newname].data[k].uv) for k in p.loop_indices],'material':p.material_index} for p in m.polygons]}
scene=D/'phoenix_worn_surfaces_v7.blend';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==sourcehash
report=dict(old);report.update(source=str(src),source_sha256=sourcehash,scene=str(scene),scene_sha256=sha(scene),active_uv=newname,maps=maps,repair_maps=repair_maps,models=models,audit_changes={'relief_edit_mask':edit_rec,'relief_opening_mask':opening_rec,'relief_bounds':[x0,y0,x1,y1],'regions':reg,'surface_faces':changed,'surface_bake':face_reports,'surface_region_mask':region_rec,'original_geometry_normals_prior_uv_layers_preserved':True,'canopy_uv_material_maps_preserved':True,'main_basecolor_unchanged':True,'method':'Exact structural opening masks; continuous surface-space patina and shallow panel cuts with padded local bake, following the Naginata repair approach'},runtime_visual_validation='Blender previews prepared; in-game review pending')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Save exact boundary UV evidence for every shared edge on the new belly chart.
joins=[]
for edge,count in edge_counts.items():
 if count<2:continue
 fs=[fi for fi in selected['Phoenix_Body'] if set(edge)<=set(bm.polygons[fi].vertices)];qs=[]
 for fi in fs:
  p=bm.polygons[fi];qs.append([list(bm.uv_layers[newname].data[p.loop_indices[list(p.vertices).index(v)]].uv) for v in edge])
 gap=float(np.max(np.abs(np.array(qs[0])-np.array(qs[1])))*N);assert gap<1e-5;joins.append({'faces':fs,'edge':list(edge),'max_uv_gap_pixels':gap})
(W/'belly_shared_edges.json').write_text(json.dumps(joins,indent=2)+'\n')
cam=s.camera;cam.data.type='ORTHO';s.render.resolution_x=1600;s.render.resolution_y=1200;s.cycles.samples=16
for name,target,offset,span in json.loads((W/'review_views.json').read_text()):
 target=Vector(target);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
# Mirrored intake/nose view checks reuse the same framing.
for name,target,offset,span in [('nose_other',(.05,1.38,.01),(-1.4,1.2,.7),1.12),('vents_other',(-.45,-.10,.19),(-1.7,1.3,1.6),1.7)]:
 target=Vector(target);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('PHOENIX_SURFACES_V7_COMPLETE',len(changed),flush=True)
