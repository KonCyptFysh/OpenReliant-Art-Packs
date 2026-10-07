import bpy,numpy as np,json,hashlib,math
from pathlib import Path
D=Path(__file__).resolve().parents[2];W=D/'work/seams_v3';M=D/'maps/seams_v3';bpy.ops.wm.open_mainfile(filepath=str(D/'naginata_worn_aligned_v3.blend'));s=bpy.context.scene;body=bpy.data.objects['Naginata_Body'];m=body.data;bpy.context.view_layer.update();srcuv='Naginata_Aligned_UV_v3';dstuv='Naginata_Delivery_UV_v3';N=4096
# Re-baking this unreleased candidate replaces only its generated delivery layer/material.
for o in s.objects:
 if o.type=='MESH' and dstuv in o.data.uv_layers:o.data.uv_layers.remove(o.data.uv_layers[dstuv])
for poly in m.polygons:
 if poly.material_index==2:poly.material_index=0
if len(m.materials)>2:m.materials.pop(index=2)
oldpatch=bpy.data.materials.get('Naginata_Repairs_PBR_v3')
if oldpatch and not oldpatch.users:bpy.data.materials.remove(oldpatch)
nose=set(list(range(20))+list(range(24,32))+list(range(34,54))+list(range(62,68)))
engine=set([90,91,92,93,94,95,118,119,122,123,124,125,130,131,134,135,136,137,140,141,142,143,144,145,150,151,152,153]);selected={i for i in nose|engine if not m.polygons[i].material_index}
def signature():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],[list(r) for r in o.matrix_world],[list(q.uv) for q in o.data.uv_layers['Original_Naginata_UV'].data]) for o in s.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
before=signature()
for o in s.objects:
 if o.type!='MESH':continue
 values=[tuple(q.uv) for q in o.data.uv_layers[srcuv].data];uv=o.data.uv_layers.new(name=dstuv)
 for q,v in zip(uv.data,values):q.uv=v
 o.data.uv_layers.active=uv;uv.active_render=True
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.context.tool_settings.mesh_select_mode=(False,False,True)
for p in m.polygons:p.select=p.index in selected
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.005,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');m.update();bpy.context.view_layer.update()
for p in m.polygons:
 if p.index not in selected:
  assert all((m.uv_layers[srcuv].data[i].uv-m.uv_layers[dstuv].data[i].uv).length<1e-7 for i in p.loop_indices),('UNSELECTED_UV_CHANGED',p.index)
# Derive exact tangent frames before and after repacking so existing normals keep their orientation.
frames={};normalmatrix=np.array(body.matrix_world.to_3x3().inverted().transposed());rotation=np.array(body.matrix_world.to_3x3())
for name in [srcuv,dstuv]:
 m.calc_tangents(uvmap=name);frames[name]=[]
 for p in m.polygons:
  ts=np.array([list(m.loops[i].tangent) for i in p.loop_indices])@rotation.T;ts/=np.linalg.norm(ts,axis=1)[:,None];ns=np.array([list(m.corner_normals[i].vector) for i in p.loop_indices])@normalmatrix.T;ns/=np.linalg.norm(ns,axis=1)[:,None];signs=np.array([m.loops[i].bitangent_sign for i in p.loop_indices]);frames[name].append((ts,ns,signs))
mat=bpy.data.materials['Naginata_Worn_PBR_v3'];source={}
def load(path):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return a
for name in ['basecolor','normal','roughness','metallic']:
 source[name]=load(Path(mat.node_tree.nodes['Delivered '+name].image.filepath))
reference=load(M/'naginata_repair_material_reference.png');mid=reference.shape[1]//2;swatches={'nose':reference[:,:mid],'engine':reference[:,mid:]}
col=source['basecolor'];S=N/1254;donors={'nose':col[int(880*S):int(940*S),int(20*S):int(90*S)],'engine':col[int(900*S):int(980*S),int(1120*S):int(1220*S)]};tints={k:np.clip(np.median(v.reshape(-1,3),axis=0)/np.median(swatches[k].reshape(-1,3),axis=0),.75,1.35) for k,v in donors.items()}
def sample(im,q):
 h,w=im.shape[:2];x=(q[:,0]%1)*w-.5;y=(1-q[:,1]%1)*h-.5;x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[:,None];fy=(y-y0)[:,None];return (im[y0%h,x0%w]*(1-fx)+im[y0%h,(x0+1)%w]*fx)*(1-fy)+(im[(y0+1)%h,x0%w]*(1-fx)+im[(y0+1)%h,(x0+1)%w]*fx)*fy
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def structure(p,kind):
 if kind=='nose':
  ring=1-smooth(.0005,.004,np.abs(p[:,1]-1.065));centre=(1-smooth(.0004,.0025,np.abs(p[:,0])))*smooth(1.035,1.045,p[:,1]);cut=np.maximum(ring,centre)
 else:
  ring=1-smooth(.0005,.0035,np.abs(p[:,1]+1.073));long=(1-smooth(.0005,.0035,np.abs(np.abs(p[:,0])-.445)))*smooth(-1.09,-1.06,p[:,1]);cut=np.maximum(ring,long)
 return -.0032*cut,cut
def patch_colour(p,norm,kind):
 if kind=='engine':
  q=np.column_stack(((np.abs(p[:,0])+.2*p[:,2])/.85+.06,1-((-p[:,1]-1.2*p[:,2]-.7)/.85+.06)));return np.clip(sample(swatches[kind],q)*tints[kind],0,1)
 pos=p.copy();pos[:,0]=np.abs(pos[:,0]);pos[:,1]=(pos[:,1]-.65) if kind=='nose' else (-pos[:,1]-.70);pos[:,2]+=.15;pos=pos/.85+.06;weights=np.abs(norm)**4;weights/=weights.sum(1)[:,None];out=np.zeros_like(p)
 for ax,(a,b) in enumerate([(1,2),(0,2),(0,1)]):out+=sample(swatches[kind],np.column_stack((pos[:,a],1-pos[:,b])))*weights[:,ax,None]
 return np.clip(out*tints[kind],0,1)
out={k:np.zeros((N,N,3),np.float32) for k in ['basecolor','normal','roughness','metallic','height']};out['normal'][:]=(0.5,.5,1);coverage=np.zeros((N,N),bool);positions=np.array([list(body.matrix_world@v.co) for v in m.vertices]);face_report=[]
geonorm=np.zeros_like(positions)
for poly in m.polygons:
 if poly.material_index==1:continue
 a,b,c=positions[list(poly.vertices)];nrm=np.cross(b-a,c-a)
 for vi in poly.vertices:geonorm[vi]+=nrm
geonorm/=np.maximum(np.linalg.norm(geonorm,axis=1)[:,None],1e-9)
for fi in sorted(selected):
 p=m.polygons[fi];old=np.array([list(m.uv_layers[srcuv].data[i].uv) for i in p.loop_indices]);uv=np.array([list(m.uv_layers[dstuv].data[i].uv) for i in p.loop_indices]);xy=np.column_stack((uv[:,0]*N,(1-uv[:,1])*N));lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N,np.ceil(xy.max(0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];q=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));A=np.column_stack((xy[1]-xy[0],xy[2]-xy[0]));det=np.linalg.det(A);assert abs(det)>1e-5,(fi,det);b=(q-xy[0])@np.linalg.inv(A).T;b=np.column_stack((1-b.sum(1),b));inside=b.min(1)>=-1e-6;b=b[inside];rx=xx.ravel()[inside];ry=yy.ravel()[inside]
 if not len(rx):continue
 dup=coverage[ry,rx];assert not np.any(dup) or np.max(b[dup].min(1))<.00002,(fi,int(dup.sum()),float(np.max(b[dup].min(1))));b=b[~dup];rx=rx[~dup];ry=ry[~dup];coverage[ry,rx]=True;pos=b@positions[list(p.vertices)];oldq=b@old;kind='nose' if fi in nose else 'engine';mask=smooth(.94,1.015,pos[:,1]) if kind=='nose' else np.ones(len(pos));oldts,oldns,oldsgn=frames[srcuv][fi];newts,newns,newsgn=frames[dstuv][fi]
 def basis(ts,ns,sgn):
  n=b@ns;n/=np.linalg.norm(n,axis=1)[:,None];t=b@ts;t-=n*np.sum(n*t,axis=1)[:,None];t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-9);bit=np.cross(n,t)*np.sign(b@sgn)[:,None];return t,bit,n
 ot,ob,on=basis(oldts,oldns,oldsgn);nt,nb,nn=basis(newts,newns,newsgn);oldnormal=sample(source['normal'],oldq)*2-1;world=ot*oldnormal[:,0,None]+ob*oldnormal[:,1,None]+on*oldnormal[:,2,None];h,cut=structure(pos,kind);grad=np.empty_like(pos);eps=.00015
 for ax in range(3):
  off=np.zeros(3);off[ax]=eps;grad[:,ax]=(structure(pos+off,kind)[0]-structure(pos-off,kind)[0])/(2*eps)
 grad-=nn*np.sum(grad*nn,axis=1)[:,None];newnormal=nn-grad;newnormal/=np.linalg.norm(newnormal,axis=1)[:,None];world=world*(1-mask[:,None])+newnormal*mask[:,None];world/=np.linalg.norm(world,axis=1)[:,None];nmap=np.column_stack((np.sum(world*nt,1),np.sum(world*nb,1),np.sum(world*nn,1)));nmap/=np.linalg.norm(nmap,axis=1)[:,None]
 gn=b@geonorm[list(p.vertices)];gn/=np.maximum(np.linalg.norm(gn,axis=1)[:,None],1e-9);patch=patch_colour(pos,gn,kind);patch*=1-cut[:,None]*.74;colour=sample(source['basecolor'],oldq)*(1-mask[:,None])+patch*mask[:,None];wear=patch.mean(1);rough=np.clip((.83 if kind=='nose' else .53)+(.5-wear)*.16,.44,.91);rough=rough*(1-cut)+.85*cut;metal=np.full(len(pos),0.0 if kind=='nose' else .82);metal*=1-cut*.8
 for k,value in [('basecolor',colour),('normal',nmap*.5+.5),('roughness',sample(source['roughness'],oldq)*(1-mask[:,None])+rough[:,None]*mask[:,None]),('metallic',sample(source['metallic'],oldq)*(1-mask[:,None])+metal[:,None]*mask[:,None]),('height',np.repeat(((h*mask+.012)/.024)[:,None],3,axis=1))]:out[k][ry,rx]=value
 face_report.append({'face':fi,'kind':kind,'pixels':len(rx),'mask_max':float(mask.max()),'mask_min':float(mask.min())})
 print('BAKED_FACE',fi,kind,len(rx),flush=True)
# Extend island texels into padding to prevent filtering through unrelated regions.
idx=np.full((N,N),-1,np.int32);idx[coverage]=np.flatnonzero(coverage);valid=coverage.copy()
for _ in range(16):
 updated=idx.copy()
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
  q=np.roll(idx,shift,axis);take=(updated<0)&(q>=0);updated[take]=q[take]
 idx=updated
pad=(idx>=0)&~coverage;records={}
for k,a in out.items():
 a[pad]=a.reshape(-1,3)[idx[pad]];im=bpy.data.images.new('Naginata repair '+k,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=a;im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());path=M/f'naginata_repairs_{k}_4k_v3.png';im.filepath_raw=str(path);im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();bpy.data.images.remove(im);records[k]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
patchmat=bpy.data.materials.new('Naginata_Repairs_PBR_v3');patchmat.use_nodes=True;n=patchmat.node_tree.nodes;n.clear();l=patchmat.node_tree.links;uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map=dstuv;bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.3;output=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],output.inputs[0]);bs.inputs['Roughness'].default_value=.65
for k in ['basecolor','normal','roughness','metallic']:
 im=bpy.data.images.load(records[k]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if k=='basecolor' else 'Non-Color';im.pack();node=n.new('ShaderNodeTexImage');node.name='Delivered '+k;node.image=im;l.new(uvnode.outputs[0],node.inputs[0])
 if k=='normal':nm=n.new('ShaderNodeNormalMap');nm.uv_map=dstuv;l.new(node.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
 else:l.new(node.outputs[0],bs.inputs[{'basecolor':'Base Color','metallic':'Metallic','roughness':'Roughness'}[k]])
body.data.materials.append(patchmat);slot=len(body.data.materials)-1
for fi in selected:m.polygons[fi].material_index=slot
for material in [mat]:
 for node in material.node_tree.nodes:
  if hasattr(node,'uv_map'):node.uv_map=dstuv
assert signature()==before;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'naginata_worn_aligned_v3.blend'))
report={'scene':str(D/'naginata_worn_aligned_v3.blend'),'active_uv':dstuv,'original_mesh_original_uv_normals_unchanged':True,'maps':records,'groups':face_report,'coverage_pixels':int(coverage.sum()),'source_material_patch':str(M/'naginata_repair_material_reference.png'),'source_method':'Built-in image generation swatches, triplanar surface projection and native-face texture bake; no geometry edits','height_decode':'normalized * 0.024 - 0.012 model world units; local authored panel cuts only','tints':{k:v.tolist() for k,v in tints.items()},'geometry_signature':before,'models':{}}
for o in s.objects:
 if o.type=='MESH':report['models'][o.name]={'vertices':[list(v.co) for v in o.data.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(o.data.uv_layers[dstuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in o.data.polygons]}
(W/'bake_validation.json').write_text(json.dumps(report,indent=2));print('SURFACE_REPAIR_BAKED',len(selected),int(coverage.sum()),flush=True)
