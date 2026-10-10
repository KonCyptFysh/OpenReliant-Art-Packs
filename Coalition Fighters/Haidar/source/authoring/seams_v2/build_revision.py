import os
from pathlib import Path
import bpy,numpy as np,json,hashlib,math
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/seams_v2';M=D/'maps/seams_v2';R=D/'review/seams_v2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((W/'prior_project_state.json').read_text());src=Path(prior['latest_scene']);source_sha=sha(src);old=json.loads((D/'work/reconstruction_v1/validation.json').read_text());assert source_sha==old['scene_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];before={o.name:{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'normals':[list(n.vector) for n in o.data.corner_normals],'matrix':[list(row) for row in o.matrix_world],'uvs':{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},'materials':[p.material_index for p in o.data.polygons]} for o in obs};newuv='Haidar_Delivery_UV_v2'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True

def smooth(a,b,z):t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def read(path,scale=None):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
 if scale:im.scale(scale,scale)
 w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return a

def save(a,label):
 n=a.shape[0];buf=np.ones((n,n,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Haidar v2 '+label,n,n,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());p=M/f'haidar_{label}_v2.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8';im.save();bpy.data.images.remove(im);return dict(path=str(p),sha256=sha(p),dimensions=[n,n])

def material(name,maps):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0])
 for key in ['basecolor','roughness','metallic','normal']:
  im=bpy.data.images.load(maps[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();tx=n.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;l.new(uv.outputs[0],tx.inputs[0])
  if key=='normal':nm=n.new('ShaderNodeNormalMap');nm.uv_map=newuv;l.new(tx.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
  else:l.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 return mat
# Trace only the original outside pane contours. Internal painted dividers are removed.
paths=[[[15,522],[93,508],[137,499],[170,500],[179,508],[179,581],[170,589],[139,590],[15,570]],[[427,738],[453,731],[486,727],[554,730],[614,739],[614,769],[427,769]],[[633,751],[640,750],[716,768],[716,779],[633,773]],[[975,935],[1048,962],[1048,1069],[1038,1079],[975,1104]],[[975,1141],[1046,1113],[1046,1240],[1034,1239],[975,1206]]]
N=4096;oldmaps=old['maps']['hull'];maps=dict(oldmaps);Y,X=np.mgrid[:N,:N].astype(np.float32);X=(X+.5)*1254/N;Y=(Y+.5)*1254/N;dist=np.full((N,N),-100,np.float32)
for points in paths:
 p=np.array(points);x0,y0=np.maximum(0,np.floor((p.min(0)-12)*N/1254).astype(int));x1,y1=np.minimum(N,np.ceil((p.max(0)+12)*N/1254).astype(int));sl=np.s_[y0:y1,x0:x1];xx=X[sl];yy=Y[sl];inside=np.zeros(xx.shape,bool);dd=np.full(xx.shape,1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  e=b-a;t=np.clip(((xx-a[0])*e[0]+(yy-a[1])*e[1])/(e@e),0,1);dd=np.minimum(dd,np.hypot(xx-a[0]-t*e[0],yy-a[1]-t*e[1]));inside^=((a[1]>yy)!=(b[1]>yy))&(xx<a[0]+(yy-a[1])*e[0]/(e[1]+1e-12))
 dist[sl]=np.maximum(dist[sl],np.where(inside,dd,-dd))
glass=smooth(-.25,.25,dist);surround=smooth(-2.7,-2.1,dist);seal=surround-glass;oldg=read(oldmaps['glass']['path'])[:,:,0];olds=read(oldmaps['seal']['path'])[:,:,0];footprint=np.maximum.reduce([oldg,olds,surround]);neutral=np.maximum(smooth(-9,-3,dist),np.maximum(oldg,olds))
prev=read(oldmaps['normal']['path'])*2-1;angle=np.degrees(np.arccos(np.clip(prev[:,:,2]/np.linalg.norm(prev,axis=-1),-1,1)));edge=(oldg>.01)&(oldg<.99);diagnosis={'prior_edge_normal_max_degrees':float(angle[edge].max()),'new_glass_and_gasket_normal':'flat tangent normal','tint_srgb':[.11,.17,.145],'roughness':.16,'metallic':0,'outer_outlines_preserved':True,'internal_dividers_removed':True}
locality={}
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=read(oldmaps[key]['path']);b=a.copy()
 if key=='basecolor':b=a*(1-glass[:,:,None])+np.array([.11,.17,.145])*glass[:,:,None]
 elif key in ['roughness','metallic']:b=a*(1-footprint[:,:,None])+(.86 if key=='roughness' else 0)*footprint[:,:,None];b=b*(1-glass[:,:,None])+(.16 if key=='roughness' else 0)*glass[:,:,None]
 elif key=='normal':
  b=a*(1-neutral[:,:,None])+np.array([.5,.5,1])*neutral[:,:,None];q=b*2-1;q/=np.linalg.norm(q,axis=-1,keepdims=True);b=q*.5+.5;b[neutral==0]=a[neutral==0]
 elif key=='glass':b=np.broadcast_to(glass[:,:,None],a.shape)
 elif key=='seal':b=np.broadcast_to(seal[:,:,None],a.shape)
 elif key=='height':b=a*(1-neutral[:,:,None])+.48*neutral[:,:,None]
 elif key=='structure':b=a*(1-footprint[:,:,None])+seal[:,:,None]*footprint[:,:,None]
 else:b=a*(1-footprint[:,:,None])
 allow=glass if key=='basecolor' else np.maximum(footprint,neutral)
 assert np.array_equal(a[allow==0],b[allow==0]),key
 maps[key]=save(b,'hull_'+key);locality[key]={'outside_edit_footprint_identical_before_encoding':True}
 print('GLASS_MAP',key,flush=True)
edit=save(neutral,'glazing_edit_mask');pane_mask=save(glass,'pane_mask');maps['glazing_edit_mask']=edit
hullmat=material('Haidar_Worn_Hull_PBR_v2',maps)
for o in obs:o.data.materials[0]=hullmat
# Dedicated UV islands for the complete nose and the continuous forward collar.
selection={'Han_Body':set([8,9,10,11,159,160,161,162,175,176,183,184,185,186,257]+list(range(262,274))), 'Han_Cockpit':set([0,1,2,15,16,17]+list(range(18,26))+list(range(26,32))+list(range(34,38)))}
bpy.ops.object.select_all(action='DESELECT')
for o in obs:
 o.select_set(o.name in selection)
 for p in o.data.polygons:p.select=p.index in selection.get(o.name,set())
bpy.context.view_layer.objects.active=bpy.data.objects['Han_Body'];bpy.context.tool_settings.mesh_select_mode=(False,False,True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.uv.smart_project(angle_limit=math.radians(48),island_margin=.025,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
# One continuous model-space material spans both parts; no UV-island-dependent colour or panel paths.
ref=read(M/'repair_material_reference.png');steel=ref[:,ref.shape[1]//2:];main=read(oldmaps['basecolor']['path'],1254);target=np.median(main[915:985,365:445],axis=(0,1));tint=target/np.median(steel,axis=(0,1));print('REPAIR_TINT',tint.tolist(),flush=True)
def sample(im,q):
 hh,ww=im.shape[:2];x=np.clip(q[:,0],0,1)*(ww-1);y=np.clip(q[:,1],0,1)*(hh-1);x0=x.astype(int);y0=y.astype(int);x1=np.minimum(x0+1,ww-1);y1=np.minimum(y0+1,hh-1);fx=(x-x0)[:,None];fy=(y-y0)[:,None];return (im[y0,x0]*(1-fx)+im[y0,x1]*fx)*(1-fy)+(im[y1,x0]*(1-fx)+im[y1,x1]*fx)*fy

def colour(p):
 q=np.column_stack((np.abs(p[:,0]),p[:,1]+180,p[:,2]-100))/900+.08
 radial=np.column_stack((p[:,0],p[:,1]-5,np.where(p[:,2]>600,p[:,2]-650,15.)))
 weight=np.abs(radial)**2;weight/=np.maximum(weight.sum(1)[:,None],1e-8);c=np.zeros_like(p)
 for ax,(a,b) in enumerate([(1,2),(0,2),(0,1)]):c+=sample(steel,q[:,[a,b]])*weight[:,ax,None]
 return np.clip(c*tint,0,1)

def panel(p):
 nose=p[:,2]>600;rings=np.where(nose,np.minimum(np.abs(p[:,2]-680.01),np.abs(p[:,2]-730)),np.minimum.reduce([np.abs(p[:,2]-z) for z in [103.6,175,253.5,325,396.414,460.97]]));r=1-smooth(.6,1.65,rings)
 # Longitudinal seams are defined by planes through the collar axis and close at each ring.
 theta=np.arctan2(p[:,0],-(p[:,1]-5));rad=np.hypot(p[:,0],p[:,1]-5);dist=np.full(len(p),1e6)
 for a in [0,.72,-.72,math.pi/2]:dist=np.minimum(dist,np.abs(np.sin(theta-a))*rad)
 seams=1-smooth(.55,1.45,dist)
 # Simple centre split on the nose, no small floating line fragments.
 seams=np.where(nose,1-smooth(.5,1.4,np.abs(p[:,0])),seams)
 return np.maximum(r,seams)
def height(p):return -.58*panel(p)
N2=2048;out={k:np.zeros((N2,N2,3),np.float32) for k in ['basecolor','normal','roughness','metallic','height']};out['normal'][:]=(.5,.5,1);coverage=np.zeros((N2,N2),bool);face_reports=[];repair_groups=[]
for name,ids in selection.items():
 o=bpy.data.objects[name];m=o.data;m.calc_tangents(uvmap=newuv);positions=np.array([v.co[:] for v in m.vertices]);repair_groups.append(dict(part=name,faces=sorted(ids),reason='Continuous nose and forward collar material projection'))
 for fi in sorted(ids):
  p=m.polygons[fi];uv=np.array([m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices]);xy=uv*np.array([N2,-N2])+[0,N2];lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N2,np.ceil(xy.max(0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];pt=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));bb=(pt-xy[0])@np.linalg.inv(np.column_stack((xy[1]-xy[0],xy[2]-xy[0]))).T;bb=np.column_stack((1-bb.sum(1),bb));inside=bb.min(1)>-1e-7;bb=bb[inside];rx=xx.ravel()[inside];ry=yy.ravel()[inside];dup=coverage[ry,rx];assert not np.any(dup) or np.max(bb[dup].min(1))<.00005,(name,fi,'overlap');bb=bb[~dup];rx=rx[~dup];ry=ry[~dup];coverage[ry,rx]=True;pos=bb@positions[list(p.vertices)];gap=panel(pos);col=colour(pos)*(1-.73*gap[:,None]);rough=.66+.19*gap;metal=.56*(1-.88*gap);h=height(pos)
  ns=np.array([m.corner_normals[i].vector[:] for i in p.loop_indices]);ts=np.array([m.loops[i].tangent[:] for i in p.loop_indices]);sign=np.array([m.loops[i].bitangent_sign for i in p.loop_indices]);n=bb@ns;n/=np.linalg.norm(n,axis=1)[:,None];t=bb@ts;t-=n*np.sum(n*t,axis=1)[:,None];t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-8);bt=np.cross(n,t)*np.sign(bb@sign)[:,None];grad=np.zeros_like(pos)
  for ax in range(3):e=np.zeros(3);e[ax]=.02;grad[:,ax]=(height(pos+e)-height(pos-e))/.04
  grad-=n*np.sum(grad*n,axis=1)[:,None];wn=n-grad;wn/=np.linalg.norm(wn,axis=1)[:,None];norm=np.column_stack((np.sum(wn*t,1),np.sum(wn*bt,1),np.sum(wn*n,1)));norm/=np.linalg.norm(norm,axis=1)[:,None]
  for k,val in [('basecolor',col),('normal',norm*.5+.5),('roughness',rough[:,None]),('metallic',metal[:,None]),('height',(h+1)[:,None]/2)]:out[k][ry,rx]=val
  vv=positions[list(p.vertices)];e=vv[1:]-vv[0];fn=np.cross(*e);fn/=np.linalg.norm(fn);tx=e[0]/np.linalg.norm(e[0]);local=e@np.stack((tx,np.cross(fn,tx)),axis=1);sigma=np.linalg.svd(np.linalg.solve(local,uv[1:]-uv[0]),compute_uv=False);face_reports.append(dict(part=name,face=fi,pixels=len(rx),uv_anisotropy=float(sigma[0]/sigma[1])))
 print('BAKED_PART',name,len(ids),flush=True)
# Extend each baked island 12 pixels into its gutter for filtering and mipmaps.
idx=np.full((N2,N2),-1,np.int32);idx[coverage]=np.flatnonzero(coverage)
for _ in range(12):
 updated=idx.copy()
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:q=np.roll(idx,shift,axis);take=(updated<0)&(q>=0);updated[take]=q[take]
 idx=updated
pad=(idx>=0)&~coverage;repair_maps={}
for key,a in out.items():a[pad]=a.reshape(-1,3)[idx[pad]];repair_maps[key]=save(a,'repair_'+key)
repair_maps['coverage']=save(coverage.astype(np.float32),'repair_coverage');repairmat=material('Haidar_Nose_Collar_PBR_v2',repair_maps)
for name,ids in selection.items():
 m=bpy.data.objects[name].data;m.materials.append(repairmat);assert len(m.materials)==3
 for fi in ids:m.polygons[fi].material_index=2
models={}
for o in obs:
 m=o.data;b=before[o.name]
 assert b['vertices']==[list(v.co) for v in m.vertices] and b['faces']==[list(p.vertices) for p in m.polygons] and b['normals']==[list(n.vector) for n in m.corner_normals] and b['matrix']==[list(r) for r in o.matrix_world]
 for name,values in b['uvs'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 for p in m.polygons:
  if p.index not in selection.get(o.name,set()):assert p.material_index==b['materials'][p.index] and all((m.uv_layers[newuv].data[i].uv-m.uv_layers['Haidar_Delivery_UV_v1'].data[i].uv).length<1e-8 for i in p.loop_indices)
 models[o.name]={'part_index':o['native_part_index'],'vertices':b['vertices'],'faces':[dict(id=p.index,vertices=list(p.vertices),uv=[m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices],material=1 if p.material_index==2 else 0,hidden=p.material_index==1) for p in m.polygons]}
assert max(x['uv_anisotropy'] for x in face_reports)<3
s.camera=bpy.data.objects['Front'];s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=32;bpy.context.preferences.filepaths.save_version=0;scene=D/'haidar_worn_pbr_v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_sha
report={'source':str(src),'source_sha256':source_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':6,'stored_triangles':478,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repair_groups,'max_visible_uv_anisotropy':max(x['uv_anisotropy'] for x in face_reports),'maps':{'hull':maps,'repair':repair_maps},'models':models,'glass_outlines':paths,'glazing':diagnosis,'map_locality':locality,'repair_faces':face_reports,'repair_texture_reference':{'path':str(M/'repair_material_reference.png'),'sha256':sha(M/'repair_material_reference.png'),'source':'Accepted Naginata repair material reference; steel half only','tint':tint.tolist()},'repair_method':'Continuous model-space steel and closed panel paths across separate nose/forward-collar islands; no geometry changes','runtime_visual_validation':'pending_user_review'};(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('HAIDAR_V2_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
# Detail cameras show all glass edges, nose joins and the complete collar.
o=bpy.data.objects['Han_Cockpit'];target=o.matrix_world@Vector((0,-35,630));cam=bpy.data.objects['Cockpit'];cam.data.type='ORTHO';cam.data.ortho_scale=1.7;s.render.resolution_x=1300;s.render.resolution_y=950
for name,offset in [('canopy_right',(1.5,1.0,.95)),('canopy_left',(-1.5,1.0,.95)),('canopy_grazing',(1.5,-.5,.25)),('canopy_roof',(0,.25,2))]:
 cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('HAIDAR_V2_RENDERS_COMPLETE',flush=True)
