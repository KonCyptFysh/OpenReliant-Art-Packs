"""Patriot v2: local material repairs on the latest scene; immutable geometry/legacy UVs.
A second atlas gives the corrected wrap surfaces real area. All base colours reuse
existing artwork; glass is a masked selection from the built-in edited reference.
"""
import bpy,numpy as np,math,json,hashlib
from pathlib import Path
D=Path('authoring://Patriot/worn');W=D/'work/audit_v3';M=D/'maps/audit_v3';N=4096
state=json.loads((W/'prior_project_state.json').read_text());src=Path(state['latest_scene']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();srcsha=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];oldname='Patriot_Delivery_UV_v1';newname='Patriot_Delivery_UV_v3';before={}
for o in obs:
 m=o.data;before[o.name]={'v':[list(v.co) for v in m.vertices],'f':[list(p.vertices) for p in m.polygons],'n':[list(q.vector) for q in m.corner_normals],'uv':{u.name:[list(q.uv) for q in u.data] for u in m.uv_layers},'m':[p.material_index for p in m.polygons]}
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def load(path,scale=None):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
 if scale:im.scale(scale,scale)
 w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(h,w,4)[::-1,:,:3].copy()
def save(a,key):
 h,w=a.shape[:2];buf=np.ones((h,w,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new(key,w,h,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());p=M/(key+'.png');im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if 'basecolor' in key else '16';im.save();bpy.data.images.remove(im);return {'path':str(p),'sha256':sha(p)}
def sample(im,q):
 h,w=im.shape[:2];x=(q[:,0]%1)*w-.5;y=(1-q[:,1]%1)*h-.5;x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[:,None];fy=(y-y0)[:,None];return (im[y0%h,x0%w]*(1-fx)+im[y0%h,(x0+1)%w]*fx)*(1-fy)+(im[(y0+1)%h,x0%w]*(1-fx)+im[(y0+1)%h,(x0+1)%w]*fx)*fy

r2=json.loads((D/'work/refinement_v2/validation.json').read_text());mainrecords=r2['main_maps'];main={k:load(v['path']) for k,v in mainrecords.items()}
coarse=load(state['maps']['basecolor']['path'],1254)
swatches={'bronze':coarse[352:405,182:255].copy(),'steel':coarse[555:629,944:1007].copy(),'green':coarse[195:237,918:985].copy()}
reference=load(D/'maps/refinement_v2/repair_wear_reference.png');mid=reference.shape[1]//2;refbrown=reference[:,:mid];refsteel=reference[:,mid:];targets={k:np.median(v.reshape(-1,3),axis=0) for k,v in swatches.items()};swatches={k:(refsteel if k=='steel' else refbrown).copy() for k in targets}
for k in swatches:swatches[k]*=targets[k]/np.median(swatches[k].reshape(-1,3),axis=0)
neutral=refbrown.mean(-1);swatches['green']=neutral[:,:,None]/np.median(neutral)*targets['green']
def triplanar(pos,norm,kind,scale=1.18):
 p=pos/scale+np.array([.08,.29,.17]);weights=np.abs(norm)**4;weights/=np.maximum(weights.sum(1)[:,None],1e-9);out=np.zeros_like(p)
 for ax,(a,b) in enumerate([(1,2),(0,2),(0,1)]):
  q=np.column_stack((p[:,a],p[:,b]));q=1-np.abs(q%2-1);out+=sample(swatches[kind],q)*weights[:,ax,None]
 return out

oldgroups=r2['groups']
extra_engine=[14,15,49,50,59,70,71,72,99,100,107,272,273,307,308,317,328,329,330,357,358,365]
# Identify both mirrored underside vent charts from their legacy UV footprint.
extra_groove=[]
for f in bpy.data.objects['Patriot_Body'].data.polygons:
 uv=np.array([list(bpy.data.objects['Patriot_Body'].data.uv_layers[oldname].data[i].uv) for i in f.loop_indices]);px=uv*np.array([1254,-1254])+[0,1254];wp=np.array([list(bpy.data.objects['Patriot_Body'].matrix_world@bpy.data.objects['Patriot_Body'].data.vertices[i].co) for i in f.vertices]);lo=px.min(0);hi=px.max(0)
 if wp[:,1].mean()>.4 and wp[:,2].mean()<0 and lo[0]<920 and hi[0]>875 and lo[1]<820 and hi[1]>575:extra_groove.append(f.index)
groups={'Patriot_Body':{'arm_fins':oldgroups['Patriot_Body']['arm_fins'],'radiator':oldgroups['Patriot_Body']['radiator'],'outer_engine':extra_engine,'groove':extra_groove}}
selected={name:{i:k for k,ids in gs.items() for i in ids} for name,gs in groups.items()};frames_old={};frames_new={};positions={};normrot={}
def frames(o,uvname):
 m=o.data;m.calc_tangents(uvmap=uvname);rot=np.array(o.matrix_world.to_3x3());nr=np.array(o.matrix_world.to_3x3().inverted().transposed());ret={}
 for p in m.polygons:
  ts=np.array([list(m.loops[i].tangent) for i in p.loop_indices])@rot.T;ts/=np.maximum(np.linalg.norm(ts,axis=1)[:,None],1e-10);ns=np.array([list(m.corner_normals[i].vector) for i in p.loop_indices])@nr.T;ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-10);ret[p.index]=(ts,ns,np.array([m.loops[i].bitangent_sign for i in p.loop_indices]))
 return ret

for o in obs:
 m=o.data;positions[o.name]=np.array([list(o.matrix_world@v.co) for v in m.vertices]);frames_old[o.name]=frames(o,oldname);u=m.uv_layers.new(name=newname,do_init=True);m.uv_layers.active=u;u.active_render=True
 for a,b in zip(u.data,m.uv_layers['Patriot_Delivery_UV_v2'].data):a.uv=b.uv
bpy.ops.object.select_all(action='DESELECT');bpy.context.tool_settings.mesh_select_mode=(False,False,True);body=bpy.data.objects['Patriot_Body'];body.select_set(True);bpy.context.view_layer.objects.active=body
for f in body.data.polygons:f.select=f.index in extra_engine+extra_groove
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.uv.smart_project(angle_limit=math.radians(35),island_margin=.018,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
for o in obs:
 for f in o.data.polygons:
  if o.name!='Patriot_Body' or f.index not in extra_engine+extra_groove:
   for i in f.loop_indices:o.data.uv_layers[newname].data[i].uv=o.data.uv_layers['Patriot_Delivery_UV_v2'].data[i].uv
 frames_new[o.name]=frames(o,newname)
# Per-group exterior edges let the grilles retain a continuous rim around folded faces.
boundaries={}
for name,gs in groups.items():
 o=bpy.data.objects[name];m=o.data
 for kind,ids in gs.items():
  sets=[ids]
  if name=='Patriot_Cockpit' and kind=='pod':sets=[[50,51,52,53]]
  count={}
  for i in sets[0]:
   vv=list(m.polygons[i].vertices)
   for a,b in zip(vv,vv[1:]+vv[:1]):e=tuple(sorted((a,b)));count[e]=count.get(e,0)+1
  boundaries[(name,kind)]=[(positions[name][a],positions[name][b]) for (a,b),v in count.items() if v==1]
def edgedist(p,edges):
 d=np.full(len(p),1e3)
 for a,b in edges:
  v=b-a;t=np.clip((p-a)@v/np.dot(v,v),0,1);d=np.minimum(d,np.linalg.norm(p-a-t[:,None]*v,axis=1))
 return d
def linecut(v,c,w=.0028):return 1-smooth(w*.3,w,np.abs(v-c))
def poly_dist(q,vertices):
 pp=np.array(vertices);d=np.full(len(q),1e6);area=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-pp[:,1]*np.roll(pp[:,0],-1))
 for a,b in zip(pp,np.roll(pp,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(q[:,1]-a[1])-v[1]*(q[:,0]-a[0]))/np.linalg.norm(v))
 return d
def capdist(q,a,b,r):
 v=np.subtract(b,a);t=np.clip((q-a)@v/np.dot(v,v),0,1);return r-np.linalg.norm(q-a-t[:,None]*v,axis=1)
def basis(fr,b):
 ts,ns,sign=fr;n=b@ns;n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-8);t=b@ts;t-=n*np.sum(n*t,axis=1)[:,None];t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-8);bt=np.cross(n,t)*np.sign(b@sign)[:,None];return t,bt,n

allrecords={};face_reports=[];preservation={}
reuse='--reuse-fins' in __import__('sys').argv
if reuse:
 previous=json.loads((W/'validation.json').read_text());allrecords['repairs']=previous['maps'];face_reports=[f for f in previous['face_reports'] if f['kind'] in ['arm_fins','radiator']];preservation=previous['preservation']
for batch in (['wrap'] if reuse else ['repairs','wrap']):
 N=4096 if batch=='repairs' else 2048
 out={k:load(r2['maps'][k]['path']) if batch=='repairs' else np.zeros((N,N,3),np.float32) for k in ['basecolor','normal','roughness','metallic','height']}
 if batch=='wrap':out['normal'][:]=(.5,.5,1)
 beforemaps={k:a.copy() for k,a in out.items()} if batch=='repairs' else None
 coverage=np.zeros((N,N),bool);classification=np.zeros((N,N),np.uint8);kindids={k:i+1 for i,k in enumerate(['arm_fins','radiator','outer_engine','groove'])}
 for name,lookup in selected.items():
  o=bpy.data.objects[name];m=o.data;vp=positions[name]
  for fi,kind in sorted(lookup.items()):
   if (kind in ['arm_fins','radiator']) != (batch=='repairs'):continue
   f=m.polygons[fi];uv=np.array([list(m.uv_layers[newname].data[i].uv) for i in f.loop_indices]);old=np.array([list(m.uv_layers[oldname].data[i].uv) for i in f.loop_indices]);fv=vp[list(f.vertices)];xy=np.column_stack((uv[:,0]*N,(1-uv[:,1])*N));lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N,np.ceil(xy.max(0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];pt=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));bb=(pt-xy[0])@np.linalg.inv(np.column_stack((xy[1]-xy[0],xy[2]-xy[0]))).T;b=np.column_stack((1-bb.sum(1),bb));inside=b.min(1)>=-1e-7;b=b[inside];rx=xx.ravel()[inside];ry=yy.ravel()[inside];dup=coverage[ry,rx];assert not dup.any() or np.max(b[dup].min(1))<.0001,(name,fi,'UV overlap');b=b[~dup];rx=rx[~dup];ry=ry[~dup];coverage[ry,rx]=True;classification[ry,rx]=kindids[kind];pos=b@fv;q=b@old;px=np.column_stack(((q[:,0]%1)*1254,(1-q[:,1]%1)*1254));col=sample(main['basecolor'],q);rough=sample(main['roughness'],q)[:,0];metal=sample(main['metallic'],q)[:,0];orig_n=sample(main['normal'],q)*2-1
   oldt,oldbt,ns=basis(frames_old[name][fi],b);ts,bts,n=basis(frames_new[name][fi],b);oldworld=oldt*orig_n[:,0,None]+oldbt*orig_n[:,1,None]+ns*orig_n[:,2,None];oldworld/=np.maximum(np.linalg.norm(oldworld,axis=1)[:,None],1e-8);fn=np.cross(fv[1]-fv[0],fv[2]-fv[0]);fn/=np.linalg.norm(fn);gn=np.broadcast_to(fn,pos.shape);replacement=np.ones(len(pos));h=np.zeros(len(pos));heightfn=None;edges=boundaries[(name,kind)]
   # Affine lookup for fixed motifs and physical gradients, continuous within each original chart.
   pinv=np.linalg.pinv((fv[1:]-fv[0]).T)
   def px_at(p):
    st=(p-fv[0])@pinv.T;qq=old[0]+st@(old[1:]-old[0]);return np.column_stack(((qq[:,0]%1)*1254,(1-qq[:,1]%1)*1254))
   if kind=='arm_fins':
    pitch=.047;start=.91
    def data(p):
     d=edgedist(p,edges);floor=smooth(.004,.008,d);fin=(1-smooth(pitch*.11,pitch*.28,np.abs((p[:,1]-start+pitch/2)%pitch-pitch/2)))*floor;return floor,fin,d
    def heightfn(p):
     floor,fin,d=data(p);return -.0038*floor+.0044*fin
    floor,fin,dd=data(pos);h=heightfn(pos);green=smooth(1.19,1.17,pos[:,1]);housing=triplanar(pos,gn,'bronze')*(1-green[:,None])+triplanar(pos,gn,'green')*green[:,None]
    # Exposed steel fins, with stable existing phase/height/UV and dark recesses.
    steel=triplanar(pos,gn,'steel');fincol=np.clip(np.array([.60,.62,.63])+(.14*(steel-steel.mean(0))),0,1)
    col=housing*(1-floor[:,None])+(np.array([.034,.042,.045])*(1-fin[:,None])+fincol*fin[:,None])*floor[:,None];rough=.80*(1-floor)+(.82-.48*fin)*floor;metal=.05*(1-floor)+(.20+.74*fin)*floor
   elif kind=='radiator':
    polygon=[(193,1189),(222,1159),(250,1147),(356,1147),(389,1176),(389,1221),(193,1221)]
    def data(p):
     uvp=px_at(p);d=poly_dist(uvp,polygon);floor=smooth(0,3,d);fin=np.zeros(len(p))
     for x in [210,243,276,309,342,375]:fin=np.maximum(fin,1-smooth(6.5,10,np.abs(uvp[:,0]-x)))
     return floor,fin*floor,d
    def heightfn(p):
     floor,fin,d=data(p);return -.0050*floor+.0065*fin
    floor,fin,d=data(pos);replacement=smooth(-1,0,d);h=heightfn(pos);newcol=np.array([.026,.034,.038])*(1-fin[:,None])+np.array([.51,.54,.55])*fin[:,None];col=col*(1-replacement[:,None])+newcol*replacement[:,None];rough=rough*(1-replacement)+(.86-.48*fin)*replacement;metal=metal*(1-replacement)+(.16+.76*fin)*replacement
   elif kind=='outer_engine':
    y=pos[:,1];bronze=smooth(-1.225,-1.231,y);paint=smooth(-.942,-.948,y);band=smooth(-1.589,-1.595,y);steel=triplanar(pos,gn,'steel');paintcol=triplanar(pos,gn,'green')*(1-bronze[:,None])+triplanar(pos,gn,'bronze')*bronze[:,None];col=steel*(1-paint[:,None])+paintcol*paint[:,None];col=col*(1-band[:,None])+steel*.72*band[:,None];rough=.57*(1-paint)+.81*paint;rough=rough*(1-band)+.43*band;metal=.84*(1-paint)+.045*paint;metal=metal*(1-band)+.88*band
    def heightfn(p):
     y=p[:,1];t=np.clip((-y-.94)/.737,0,1);cx=.64*(1-t)+.565*t;cz=-.03*(1-t)+.015*t;angle=np.arctan2(p[:,2]-cz,np.abs(p[:,0])-cx);longitudinal=(1-smooth(.014,.044,np.abs(np.sin(angle*2+.32))))*smooth(-.944,-.95,y)*(1-smooth(-1.588,-1.594,y));rings=np.maximum.reduce([linecut(y,-.945,.0030),linecut(y,-1.228,.0028),linecut(y,-1.418,.0027),linecut(y,-1.592,.0030),linecut(y,-1.633,.0025)]);return -.0017*np.maximum(rings,longitudinal)
    h=heightfn(pos);cut=np.clip(-h/.0017,0,1);col*=1-.78*cut[:,None];rough=rough*(1-cut)+.88*cut;metal*=1-.85*cut
   elif kind=='groove':
    # Retain the actual accepted radiator texture, shortening only its longitudinal mapping.
    oldd=capdist(px,np.array([898,598]),np.array([898,795]),28);erase=smooth(-2,1,oldd)
    mappedpx=px.copy();mappedpx[:,1]=580+(px[:,1]-605)*(238/192)
    mappedq=np.column_stack((mappedpx[:,0]/1254,1-mappedpx[:,1]/1254))
    source_d=capdist(mappedpx,np.array([898,598]),np.array([898,795]),24);motif=smooth(-1,2,source_d)
    bgpx=px.copy();bgpx[:,0]=970+(px[:,0]-898)*.6;bgq=np.column_stack((bgpx[:,0]/1254,1-bgpx[:,1]/1254))
    # Neighboring steel is from this same original panel, preserving its lighting/wear character.
    for key in ['basecolor','roughness','metallic']:
     original=sample(main[key],q);background=sample(main[key],bgq);detail=sample(main[key],mappedq);value=original*(1-erase[:,None])+(background*(1-motif[:,None])+detail*motif[:,None])*erase[:,None]
     if key=='basecolor':col=value
     elif key=='roughness':rough=value[:,0]*(1-erase*(1-motif))+.64*erase*(1-motif)
     else:metal=value[:,0]
    original=sample(main['normal'],q)*2-1;background=np.broadcast_to(np.array([0.,0.,1.]),pos.shape);detail=sample(main['normal'],mappedq)*2-1;detail[:,1]*=238/192;detail/=np.maximum(np.linalg.norm(detail,axis=1)[:,None],1e-9);nn=original*(1-erase[:,None])+(background*(1-motif[:,None])+detail*motif[:,None])*erase[:,None]
    oldworld=oldt*nn[:,0,None]+oldbt*nn[:,1,None]+ns*nn[:,2,None];oldworld/=np.maximum(np.linalg.norm(oldworld,axis=1)[:,None],1e-9);replacement[:]=0
   grad=np.zeros_like(pos)
   if heightfn:
    eps=.0001
    for ax in range(3):
     off=np.zeros(3);off[ax]=eps;grad[:,ax]=(heightfn(pos+off)-heightfn(pos-off))/(2*eps)
    grad-=n*np.sum(grad*n,axis=1)[:,None]
   world=n-grad;world/=np.maximum(np.linalg.norm(world,axis=1)[:,None],1e-9);world=world*replacement[:,None]+oldworld*(1-replacement[:,None]);world/=np.maximum(np.linalg.norm(world,axis=1)[:,None],1e-9);normal=np.column_stack((np.sum(world*ts,1),np.sum(world*bts,1),np.sum(world*n,1)));normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
   for key,val in [('basecolor',col),('normal',normal*.5+.5),('roughness',rough[:,None]),('metallic',metal[:,None]),('height',(h+.012)[:,None]/.024)]:out[key][ry,rx]=np.clip(val,0,1)
   e=fv[1:]-fv[0];area=np.linalg.norm(np.cross(*e))/2;t=e[0]/np.linalg.norm(e[0]);local=e@np.stack((t,np.cross(fn,t)),axis=1);sing=np.linalg.svd(np.linalg.solve(local,uv[1:]-uv[0]),compute_uv=False);face_reports.append({'part':name,'face':fi,'kind':kind,'pixels':len(rx),'uv_anisotropy':float(sing[0]/sing[1]),'texel_density':float(np.sqrt(sing.prod())*N)});print('BAKED',name,fi,kind,len(rx),flush=True)
 idx=np.full((N,N),-1,np.int32);idx[coverage]=np.flatnonzero(coverage)
 for _ in range(12):
  updated=idx.copy()
  for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
   q=np.roll(idx,shift,axis);take=(updated<0)&(q>=0);updated[take]=q[take]
  idx=updated
 pad=(idx>=0)&~coverage;records={}
 for key,a in out.items():a[pad]=a.reshape(-1,3)[idx[pad]];records[key]=save(a,'patriot_'+batch+'_'+key+('_4k_v3' if batch=='repairs' else '_2k_v3'))

 if batch=='repairs':
  untouched=~(coverage|pad)
  for k,a in out.items():assert np.array_equal(a[untouched],beforemaps[k][untouched]),k
  # Protected pod/nose charts have no overlap with this pass including padding.
  oldregions=load(r2['maps']['regions']['path'])[:,:,0];pod=(np.rint(oldregions*16)==2);assert not np.any(pod&(coverage|pad));preservation['under_nose_pixels_unchanged']=True
 allrecords[batch]=records
def material(name,maps):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newname;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.4;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
 for key in ['basecolor','normal','roughness','metallic']:
  im=bpy.data.images.load(maps[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();node=nodes.new('ShaderNodeTexImage');node.name='Delivered '+key;node.image=im;links.new(uv.outputs[0],node.inputs[0])
  if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newname;links.new(node.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
  else:links.new(node.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 return mat

fixmat=material('Patriot_Fins_PBR_v3',allrecords['repairs']);wrapmat=material('Patriot_Outer_Engine_Groove_PBR_v3',allrecords['wrap']);models={}
for o in obs:
 m=o.data
 if len(m.materials)>2:m.materials[2]=fixmat
 if o.name=='Patriot_Body':
  m.materials.append(wrapmat);assert len(m.materials)==4
  for fi in extra_engine+extra_groove:m.polygons[fi].material_index=3
 b=before[o.name];assert b['v']==[list(v.co) for v in m.vertices] and b['f']==[list(p.vertices) for p in m.polygons] and b['n']==[list(q.vector) for q in m.corner_normals]
 for name,values in b['uv'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 for f in m.polygons:
  if o.name!='Patriot_Body' or f.index not in extra_engine+extra_groove:
   assert all((m.uv_layers['Patriot_Delivery_UV_v2'].data[i].uv-m.uv_layers[newname].data[i].uv).length<1e-7 for i in f.loop_indices)
 models[o.name]={'vertices':[list(v.co) for v in m.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newname].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=newname
for mat in list(bpy.data.materials):
 if mat.users==0:bpy.data.materials.remove(mat)
for im in list(bpy.data.images):
 if im.users==0 and Path(im.filepath).name!='yank_3.png':bpy.data.images.remove(im)
assert max(f['uv_anisotropy'] for f in face_reports)<2
s['v3_audit_note']='Six full-span raised shoulder grille fins; brighter forward underside radiator ribs with unchanged layout; outer engine wrap panels and metallic end bands; shortened underside slot with rounded ends. Under-nose redesign pending. Emissives deferred.';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;scene=D/'patriot_worn_audit_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==srcsha
report={'source':str(src),'source_sha256':srcsha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newname,'main_maps':mainrecords,'maps':allrecords['repairs'],'wrap_maps':allrecords['wrap'],'groups':groups,'face_reports':face_reports,'models':models,'original_geometry_normals_and_uvs_preserved':True,'unchanged_face_uvs_preserved':True,'preservation':preservation,'glass_panes':6,'glass_roughness':.115,'glass_metallic':0,'max_repaired_uv_anisotropy':max(f['uv_anisotropy'] for f in face_reports),'emissives':'deferred','under_nose_redesign':'awaiting user direction; unchanged','runtime_visual_validation':'pending user review'};(W/'validation.json').write_text(json.dumps(report,indent=2));print('PATRIOT_V3_COMPLETE',len(face_reports),extra_groove,flush=True)
