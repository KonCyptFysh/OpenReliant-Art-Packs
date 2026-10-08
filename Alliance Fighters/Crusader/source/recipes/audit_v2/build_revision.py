
def resolve_record(v):
    if isinstance(v,dict):return {k:resolve_record(x) for k,x in v.items()}
    if isinstance(v,list):return [resolve_record(x) for x in v]
    if isinstance(v,str) and v.startswith('source/'):return str(Path(__file__).resolve().parents[2]/v[7:])
    return v
from pathlib import Path
import bpy,json,hashlib,math,numpy as np
from mathutils import Vector
D=Path(__file__).resolve().parents[2];W=D/'recipes/audit_v2';R=D/'review/audit_v2';M=D/'maps/audit_v2';N=4096;S=N/1254
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();state=resolve_record(json.loads((W/'prior_project_state.json').read_text()));src=Path(state['latest_scene']);assert src.name=='crusader_worn_pbr_v1.blend';old=resolve_record(json.loads((D/'recipes/reconstruction_v1/validation.json').read_text()));source_hash=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];oldname=old['active_uv'];newname='Crusader_Delivery_UV_v2'
before={o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uvs={u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},materials=[p.material_index for p in o.data.polygons]) for o in obs}
def read(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(h,w,4)[::-1,:,:3].copy()
def save(a,key,family='hull'):
 h,w=a.shape[:2];buf=np.ones((h,w,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Crusader v2 '+family+' '+key,w,h,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());p=M/f'crusader_{family}_{key}_v2.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);return dict(path=str(p),sha256=sha(p))
def bind(mat,key,rec):
 im=bpy.data.images.load(rec['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();mat.node_tree.nodes['Delivered '+key].image=im
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def sample(im,q):
 h,w=im.shape[:2];x=np.clip(q[:,0],0,1)*(w-1);y=np.clip(q[:,1],0,1)*(h-1);ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=(x-ix)[:,None];fy=(y-iy)[:,None];return (im[iy,ix]*(1-fx)+im[iy,np.minimum(ix+1,w-1)]*fx)*(1-fy)+(im[np.minimum(iy+1,h-1),ix]*(1-fx)+im[np.minimum(iy+1,h-1),np.minimum(ix+1,w-1)]*fx)*fy
def distance_polygon(X,Y,p):
 p=np.array(p);inside=np.zeros(X.shape,bool);dd=np.full(X.shape,1e8,np.float32)
 for a,b in zip(p,np.roll(p,-1,0)):
  e=b-a;t=np.clip(((X-a[0])*e[0]+(Y-a[1])*e[1])/(e@e),0,1);dd=np.minimum(dd,(X-a[0]-t*e[0])**2+(Y-a[1]-t*e[1])**2)
  if abs(e[1])>1e-9:inside^=((a[1]>Y)!=(b[1]>Y))&(X<a[0]+(Y-a[1])*e[0]/e[1])
 return np.sqrt(dd)*np.where(inside,1,-1)
glass_paths=[[(20,182),(28,175),(79,250),(43,262),(40,260)],[(47,287),(77,279),(85,302),(52,309)],[(54,315),(87,308),(117,401),(86,416)],[(96,439),(118,431),(109,468)],[(151,338),(155,332),(189,332),(193,338),(193,389),(151,389)],[(151,399),(193,399),(193,481),(151,482)],[(232,389),(236,389),(303,422),(304,452),(234,477),(232,475)],[(880,435),(885,432),(940,432),(944,437),(944,502),(941,503)]]
# Glass is a native material override constrained to the existing inside frame.
# Rounded polygon corners are produced by a short distance-field transition.
glass=np.zeros((N,N),np.float32);flatnormal=glass.copy();gasket=glass.copy();allowed=glass.copy()
for p in glass_paths:
 pp=np.array(p);lo=np.maximum(0,np.floor((pp.min(0)-9)*S).astype(int));hi=np.minimum(N,np.ceil((pp.max(0)+9)*S).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];dist=distance_polygon((xx+.5)/S,(yy+.5)/S,p);sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];g=smooth(-.2,.5,dist);ng=smooth(-7,-3,dist);seal=smooth(-2.6,-1.8,dist)*(1-g);glass[sl]=np.maximum(glass[sl],g);flatnormal[sl]=np.maximum(flatnormal[sl],ng);gasket[sl]=np.maximum(gasket[sl],seal)
og=read(old['maps']['glass']['path'])[:,:,0];os=read(old['maps']['seal']['path'])[:,:,0];flatnormal=np.maximum(flatnormal,np.maximum(og,os));footprint=np.maximum(np.maximum(og,os),np.minimum(1,glass+gasket));allowed=np.maximum(allowed,flatnormal)
# Extend the existing cross-panel joint through the stripe to the outside edge.
box=[555,227,685,243];x0,y0,x1,y1=[round(v*S) for v in box];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/S;Y=(yy+.5)/S;blend=smooth(561,574,X)*(1-smooth(678,684,X));cut=(1-smooth(1.0,2.15,np.abs(Y-235)))*blend;lip=(1-smooth(.55,1.2,np.abs(Y-231.4)))*blend;panelmask=np.maximum(cut,lip);allowed[y0:y1,x0:x1]=np.maximum(allowed[y0:y1,x0:x1],smooth(555,562,X)*(1-smooth(679,685,X)))
ph=-1.6*(1-smooth(1.0,2.15,np.abs(Y-235)));dy,dx=np.gradient(ph,1/S);pn=np.stack((-dx,dy,np.ones_like(ph)),-1);pn/=np.linalg.norm(pn,axis=2,keepdims=True);pn=pn*.5+.5
# The local imagegen result supplies only the badge inset. Feather its border
# into the original plate; the rest of the approved hull remains untouched.
eb=[585,930,897,1124];ex0,ey0,ex1,ey1=[round(v*S) for v in eb];ey,ex=np.mgrid[ey0:ey1,ex0:ex1];qx=(ex+.5)/S;qy=(ey+.5)/S;edge=np.minimum.reduce([qx-eb[0],eb[2]-qx,qy-eb[1],eb[3]-qy]);em=smooth(1.0,6.0,edge);q=np.column_stack(((qx.ravel()-eb[0])/(eb[2]-eb[0]),(qy.ravel()-eb[1])/(eb[3]-eb[1])));badge=sample(read(M/'crusader_emblem_raf_bird_v2.png'),q).reshape(ey1-ey0,ex1-ex0,3);allowed[ey0:ey1,ex0:ex1]=np.maximum(allowed[ey0:ey1,ex0:ex1],em)
maps=dict(old['maps']);mainmat=bpy.data.objects['Crusader_Body'].data.materials[0]
for key in ['basecolor','normal','roughness','metallic','glass','seal','height','structure','panels','paint','flat_graphics']:
 a=read(old['maps'][key]['path'])
 if key=='basecolor':a=a*(1-glass[:,:,None])+np.array([.11,.17,.145])*glass[:,:,None]
 elif key=='normal':a=a*(1-flatnormal[:,:,None])+np.array([.5,.5,1])*flatnormal[:,:,None]
 elif key in ['roughness','metallic']:
  a=a*(1-footprint[:,:,None])+(.86 if key=='roughness' else 0)*footprint[:,:,None];a=a*(1-glass[:,:,None])+(.16 if key=='roughness' else 0)*glass[:,:,None]
 elif key=='glass':a=glass[:,:,None]+np.zeros_like(a)
 elif key=='seal':a=gasket[:,:,None]+np.zeros_like(a)
 elif key=='height':a=a*(1-flatnormal[:,:,None])+(8/12)*flatnormal[:,:,None]
 elif key in ['structure','panels','paint']:a*=1-footprint[:,:,None]
 b=a[y0:y1,x0:x1]
 if key=='basecolor':
  b[:]=b*(1-cut[:,:,None])+np.array([.027,.032,.032])*cut[:,:,None];b[:]=b*(1-lip[:,:,None])+np.array([.55,.58,.56])*lip[:,:,None]
 elif key=='normal':b[:]=b*(1-blend[:,:,None])+pn*blend[:,:,None]
 elif key=='roughness':b[:]=b*(1-panelmask[:,:,None])+.85*panelmask[:,:,None]
 elif key=='metallic':b*=1-cut[:,:,None]
 elif key=='height':b[:]=b*(1-blend[:,:,None])+((ph+8)/12)[:,:,None]*blend[:,:,None]
 elif key=='panels':b[:]=np.maximum(b,cut[:,:,None])
 b=a[ey0:ey1,ex0:ex1]
 if key=='basecolor':b[:]=b*(1-em[:,:,None])+badge*em[:,:,None]
 elif key in ['normal','roughness','metallic','height','flat_graphics']:
  val={'normal':np.array([.5,.5,1]),'roughness':.8,'metallic':0,'height':8/12,'flat_graphics':1}[key];b[:]=b*(1-em[:,:,None])+val*em[:,:,None]
 maps[key]=save(a,key)
 if key in ['basecolor','normal','roughness','metallic']:bind(mainmat,key,maps[key])
 del a
editmask=save(allowed,'edit_mask');print('LOCAL_HULL_GLAZING_EMBLEM_GAP_COMPLETE',flush=True)
# Only the outer bevel collars need new UVs. The engine bodies and throats keep
# their existing artwork; a periodic chart joins all six collar facets exactly.
selected=list(range(217,233))+[256,257]+list(range(277,283));body=bpy.data.objects['Crusader_Body'];m=body.data;positions=np.array([list(body.matrix_world@v.co) for v in m.vertices]);cx=.31937;cz=-.0518;ymin=-1.42059863;ymax=-1.2991
for o in obs:
 u=o.data.uv_layers.new(name=newname,do_init=True);o.data.uv_layers.active=u;u.active_render=True
u=m.uv_layers[newname]
for fi in selected:
 p=m.polygons[fi];pts=positions[list(p.vertices)];ang=(np.arctan2(pts[:,2]-cz,np.abs(pts[:,0])-cx)/(2*np.pi)+.5)%1
 if np.ptp(ang)>.5:ang[ang<.5]+=1
 for k,q,point in zip(p.loop_indices,ang,pts):u.data[k].uv=(float(q),float(.05+.9*(point[1]-ymin)/(ymax-ymin)))
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   if n.type in ['UVMAP','NORMAL_MAP'] and n.uv_map==oldname:n.uv_map=newname
EW=2048;EH=512;ey,ex=np.mgrid[:EH,:EW];U=(ex+.5)/EW;V=1-(ey+.5)/EH;donor=read(old['maps']['basecolor']['path'])[round(1195*S):round(1240*S),round(1060*S):round(1120*S)];q=np.column_stack((1-np.abs((U.ravel()*8)%2-1),1-np.abs((V.ravel()*2.2)%2-1)));steel=sample(donor,q).reshape(EH,EW,3)
# Matched circumferential panel cuts, with symmetric rivets centred on facets.
ring=np.zeros_like(U);lip=np.zeros_like(U)
for v in [.12,.46,.88]:ring=np.maximum(ring,1-smooth(.006,.013,np.abs(V-v)));lip=np.maximum(lip,1-smooth(.003,.007,np.abs(V-(v+.019))))
phase=(U*6)%1;fastener=1-smooth(.017,.029,np.hypot((phase-.5)*.7,(V-.7)));h=-1.1*ring-.45*fastener
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=2,keepdims=True);col=steel*(1-.78*ring[:,:,None])*(1-.58*fastener[:,:,None]);col=col*(1-.12*lip[:,:,None])+np.array([.62,.64,.61])*.12*lip[:,:,None];rough=np.full(U.shape,.64)*(1-ring)+.87*ring;metal=.68*(1-ring)*(1-fastener)
repair_maps={key:save(a,key,'collar') for key,a in [('basecolor',col),('normal',normal*.5+.5),('roughness',rough),('metallic',metal),('height',(h+4)/8)]};mat=mainmat.copy();mat.name='Crusader_Continuous_Engine_Collars_v2'
for k in ['basecolor','normal','roughness','metallic']:bind(mat,k,repair_maps[k])
m.materials.append(mat);assert len(m.materials)==3
for fi in selected:m.polygons[fi].material_index=2
models={}
for o in obs:
 b=before[o.name];mesh=o.data;assert b['vertices']==[list(v.co) for v in mesh.vertices] and b['faces']==[list(p.vertices) for p in mesh.polygons] and b['normals']==[list(n.vector) for n in mesh.corner_normals]
 for k,v in b['uvs'].items():assert v==[list(q.uv) for q in mesh.uv_layers[k].data]
 for p in mesh.polygons:
  if o!=body or p.index not in selected:assert all(list(mesh.uv_layers[newname].data[k].uv)==b['uvs'][oldname][k] for k in p.loop_indices) and p.material_index==b['materials'][p.index]
 models[o.name]={'vertices':b['vertices'],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(mesh.uv_layers[newname].data[k].uv) for k in p.loop_indices],'material':p.material_index} for p in mesh.polygons]}
# Geometry-keyed seam checks include vertices split by the original hard edges.
from collections import defaultdict
edges=defaultdict(list)
for fi in selected:
 p=m.polygons[fi];vs=list(p.vertices)
 for j in range(3):
  kk=[j,(j+1)%3];points=[tuple(np.round(positions[vs[i]],5)) for i in kk];uvs=[list(u.data[p.loop_indices[i]].uv) for i in kk];order=np.argsort(points,axis=0) if False else sorted(range(2),key=lambda i:points[i]);edges[tuple(points[i] for i in order)].append((fi,np.array([uvs[i] for i in order])))
joins=[]
for edge,items in edges.items():
 if len(items)!=2:continue
 delta=items[0][1]-items[1][1];delta[:,0]-=np.round(delta[:,0]);gap=float(np.abs(delta).max());assert gap<1e-4;joins.append(dict(faces=[q[0] for q in items],max_periodic_uv_gap=gap))
scene=D/'crusader_worn_pbr_v2.blend';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_hash
report=dict(old);report['emblem_redraw']={'image':str(M/'crusader_emblem_raf_bird_v2.png'),'reference':'https://commons.wikimedia.org/wiki/File:RAF-Badge.svg','colour':'silver','tool_mode':'built-in imagegen'};report.update(source=str(src),source_sha256=source_hash,scene=str(scene),scene_sha256=sha(scene),active_uv=newname,maps=maps,repair_maps=repair_maps,models=models,uv_repairs=[dict(part='Crusader_Body',faces=selected,method='Periodic cylindrical collar chart; same axial seam positions on all six facets')],audit_changes=dict(glass_paths=glass_paths,glass_roughness=.16,glass_normal='flat pane and gasket with soft outer transition',glass_tint_srgb=[.11,.17,.145],emblem_region=eb,panel_gap_region=box,panel_gap_line=[[561,235],[684,235]],edit_mask=editmask,collar_faces=selected,collar_shared_edges=joins,original_geometry_normals_and_prior_uv_layers_preserved=True),runtime_visual_validation='v2 pending user review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('CRUSADER_V2_SAVED',len(joins),'verified collar joins',flush=True)
cam=s.camera;cam.data.type='ORTHO';s.cycles.samples=16;s.render.resolution_x=1400;s.render.resolution_y=1050
views=[('engines',(.0,-1.17,-.01),(1.3,-1.7,.7),1.65),('engines_other',(.0,-1.17,-.01),(-1.3,-1.7,.7),1.65),('wing_gap',(.39,-.10,.34),(.6,.1,1.5),1.1),('emblem',(0,-.22,.32),(0,-.2,2),.87),('glass_right',(0,.8,.2),(1.4,.45,.65),.86),('glass_left',(0,.8,.2),(-1.4,.45,.65),.86),('whole',(0,0,0),(4,6,3.5),3.1)]
for name,target,offset,span in views:
 target=Vector(target);cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('CRUSADER_V2_COMPLETE',flush=True)
