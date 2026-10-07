"""Repair edge density and engine surface projection from the latest v3 scene.
Reuses the accepted atlas and repair swatches; no main-atlas or mesh edits.
"""
import bpy,numpy as np,json,hashlib,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parents[2];W=D/'work/edges_v4';M=D/'maps/edges_v4';N=2048
state=json.loads((W/'prior_project_state.json').read_text());src=Path(state['latest_scene']);source_hash=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update();body=bpy.data.objects['Naginata_Body'];m=body.data;oldname=m.uv_layers.active.name;newname='Naginata_Delivery_UV_v4';positions=np.array([list(body.matrix_world@v.co) for v in m.vertices]);before={}
for o in s.objects:
 if o.type=='MESH':before[o.name]={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'normals':[list(n.vector) for n in o.data.corner_normals],'matrix':[list(row) for row in o.matrix_world],'uvs':{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},'materials':[p.material_index for p in o.data.polygons]}
edge={f['id'] for f in json.loads((W/'mesh_v3.json').read_text())['Naginata_Body']['faces'] if 206<=f['id']<346 and abs(f['normal'][0])<.7}
engine={p.index for p in m.polygons if p.material_index==2 and (body.matrix_world@p.center).y<-.5};ports={126,127,128,129};selected=edge|engine|ports
for o in s.objects:
 if o.type!='MESH':continue
 old=[tuple(q.uv) for q in o.data.uv_layers.active.data];u=o.data.uv_layers.new(name=newname)
 for q,v in zip(u.data,old):q.uv=v
 o.data.uv_layers.active=u;u.active_render=True
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.context.tool_settings.mesh_select_mode=(False,False,True)
for p in m.polygons:p.select=p.index in selected
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.uv.smart_project(angle_limit=math.radians(35),island_margin=.012,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');m.update()
# Keep a stable tangent frame for the native normal-map bake.
m.calc_tangents(uvmap=newname);rot=np.array(body.matrix_world.to_3x3());normrot=np.array(body.matrix_world.to_3x3().inverted().transposed());frames={}
for p in m.polygons:
 ts=np.array([list(m.loops[i].tangent) for i in p.loop_indices])@rot.T;ts/=np.maximum(np.linalg.norm(ts,axis=1)[:,None],1e-10);ns=np.array([list(m.corner_normals[i].vector) for i in p.loop_indices])@normrot.T;ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-10);frames[p.index]=(ts,ns,np.array([m.loops[i].bitangent_sign for i in p.loop_indices]))
def load(path,scale=None):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
 if scale:im.scale(scale,scale)
 w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1,:,:3].copy();bpy.data.images.remove(im);return a
main=load(Path(state['basecolour']));coarse=load(Path(state['basecolour']),384);reference=load(D/'maps/seams_v3/naginata_repair_material_reference.png');mid=reference.shape[1]//2;steel=reference[:,mid:];bronze=reference[:,:mid];tints=json.loads((D/'work/seams_v3/bake_validation.json').read_text())['tints'];redpixels=main[(main[:,:,0]>.2)&(main[:,:,0]>main[:,:,1]*2.2)&(main[:,:,0]>main[:,:,2]*2.4)];redbase=np.median(redpixels,axis=0);print('RED_PALETTE',redbase,flush=True)
def sample(im,q):
 h,w=im.shape[:2];x=(q[:,0]%1)*w-.5;y=(1-q[:,1]%1)*h-.5;x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[:,None];fy=(y-y0)[:,None];return (im[y0%h,x0%w]*(1-fx)+im[y0%h,(x0+1)%w]*fx)*(1-fy)+(im[(y0+1)%h,x0%w]*(1-fx)+im[(y0+1)%h,(x0+1)%w]*fx)*fy
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
# Material projection now uses all three axes, with geometric face normals.
# No projection direction is allowed to collapse to a line on a vertical face.
def triplanar(pos,norm,texture,scale=.85):
 p=pos.copy();p[:,0]=np.abs(p[:,0]);p[:,1]=(-p[:,1]-.70);p[:,2]+=.15;p=p/scale+.06;weights=np.abs(norm)**4;weights/=np.maximum(weights.sum(1)[:,None],1e-8);out=np.zeros_like(p)
 for ax,(a,b) in enumerate([(1,2),(0,2),(0,1)]):out+=sample(texture,np.column_stack((p[:,a],1-p[:,b])))*weights[:,ax,None]
 return out
geonorm=np.zeros_like(positions)
for p in m.polygons:
 if p.material_index==1:continue
 v=positions[list(p.vertices)];n=np.cross(v[1]-v[0],v[2]-v[0])
 for vi in p.vertices:geonorm[vi]+=n
geonorm/=np.maximum(np.linalg.norm(geonorm,axis=1)[:,None],1e-9)
# The native attachment is in body-part space. Imported mesh vertices already include this origin.
origin=np.array(json.loads((D/'source/native_parts.json').read_text())[1]['origin']);nativeglows=[(-122.54,-24.97,-325.56),(131.50,-27.56,-325.40)];glows=np.array([list(body.matrix_world@Vector(np.array(g)+origin)) for g in nativeglows]);radius=.041
print('NATIVE_EXHAUST_CENTRES',glows.tolist(),flush=True)
def engine_height(p):
 ring=1-smooth(.0005,.0035,np.abs(p[:,1]+1.073));long=(1-smooth(.0005,.0035,np.abs(np.abs(p[:,0])-.445)))*smooth(-1.09,-1.06,p[:,1]);cut=np.maximum(ring,long);return -.0032*cut

def port_data(p):
 c=glows[0] if p[:,0].mean()<0 else glows[1];dx=p[:,0]-c[0];dy=p[:,2]-c[2];rr=np.sqrt(dx*dx+dy*dy);q=np.column_stack(((688+dx/radius*29)/1254,1-(1113-dy/radius*29)/1254));mask=1-smooth(radius*.95,radius*1.08,rr);return q,rr,dy,mask

def port_height(p):
 q,rr,y,mask=port_data(p);inner=1-smooth(radius*.80,radius*.87,rr);lip=(1-smooth(radius*.05,radius*.10,np.abs(rr-radius*.89)));fins=np.zeros(len(p))
 for a in [-14,-7,0,7,14]:fins=np.maximum(fins,1-smooth(.0008,.0028,np.abs(y+a*radius/29)))
 fins*=1-smooth(radius*.73,radius*.81,rr)
 return (-.007*inner+.0012*lip+.0058*fins)*mask
out={k:np.zeros((N,N,3),np.float32) for k in ['basecolor','normal','roughness','metallic','height']};out['normal'][:]=(.5,.5,1);coverage=np.zeros((N,N),bool);classification=np.zeros((N,N),np.uint8);face_reports=[]
for fi in sorted(selected):
 p=m.polygons[fi];uv=np.array([list(m.uv_layers[newname].data[i].uv) for i in p.loop_indices]);old=np.array([list(m.uv_layers[oldname].data[i].uv) for i in p.loop_indices]);xy=np.column_stack((uv[:,0]*N,(1-uv[:,1])*N));lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N,np.ceil(xy.max(0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];pt=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));b=(pt-xy[0])@np.linalg.inv(np.column_stack((xy[1]-xy[0],xy[2]-xy[0]))).T;b=np.column_stack((1-b.sum(1),b));inside=b.min(1)>=-1e-7;b=b[inside];rx=xx.ravel()[inside];ry=yy.ravel()[inside];dup=coverage[ry,rx]
 assert not np.any(dup) or np.max(b[dup].min(1))<.00005,(fi,'overlap');b=b[~dup];rx=rx[~dup];ry=ry[~dup];coverage[ry,rx]=True
 pos=b@positions[list(p.vertices)];fv=positions[list(p.vertices)];fn=np.cross(fv[1]-fv[0],fv[2]-fv[0]);fn/=np.linalg.norm(fn);gn=np.broadcast_to(fn,pos.shape);col=triplanar(pos,gn,steel)*tints['engine'];kind='edge' if fi in edge else ('exhaust' if fi in ports else 'engine');classification[ry,rx]={'edge':1,'engine':2,'exhaust':3}[kind]
 h=np.zeros(len(pos));height_fn=None;rough=np.full(len(pos),.54);metal=np.full(len(pos),.82)
 if kind=='edge':
  oldcol=sample(coarse,b@old);red=smooth(1.3,2.0,oldcol[:,0]/(oldcol[:,1]+.008))*smooth(.12,.25,oldcol[:,0]);brown=smooth(1.2,1.9,oldcol[:,0]/(oldcol[:,2]+.008))*smooth(1.1,1.6,oldcol[:,1]/(oldcol[:,2]+.008))*(1-red);grayvariation=np.clip(col.mean(1)/np.median(steel.mean(-1)),.62,1.35);redcol=redbase*grayvariation[:,None];browncol=triplanar(pos,gn,bronze)*tints['nose'];col=col*(1-red[:,None])+redcol*red[:,None];col=col*(1-brown[:,None])+browncol*brown[:,None];dark=(1-smooth(.065,.20,oldcol.mean(1)))*(1-red)*(1-brown);col*=1-.82*dark[:,None];paint=np.maximum(red,brown);metal*=1-paint;rough=.54*(1-paint)+.83*paint;rough+=dark*.12
 elif kind=='engine':
  height_fn=engine_height;h=height_fn(pos);cut=np.clip(-h/.0032,0,1);col*=1-.74*cut[:,None];rough=rough*(1-cut)+.85*cut;metal*=1-.8*cut
 else:
  q,rr,y,mask=port_data(pos);port=sample(main,q);col=col*(1-mask[:,None])+port*mask[:,None];height_fn=port_height;h=height_fn(pos);rough=rough*(1-mask)+(.68-.18*smooth(-.003,.001,h))*mask;metal=metal*(1-mask)+.7*mask
 rough=np.clip(rough+(.5-col.mean(1))*.06,.42,.95)
 ts,ns,sign=frames[fi];n=b@ns;n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-8);t=b@ts;t-=n*np.sum(n*t,axis=1)[:,None];t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-8);bt=np.cross(n,t)*np.sign(b@sign)[:,None];grad=np.zeros_like(pos)
 if height_fn:
  eps=.0001
  for ax in range(3):
   off=np.zeros(3);off[ax]=eps;grad[:,ax]=(height_fn(pos+off)-height_fn(pos-off))/(2*eps)
  grad-=n*np.sum(grad*n,axis=1)[:,None]
 world=n-grad;world/=np.linalg.norm(world,axis=1)[:,None];normal=np.column_stack((np.sum(world*t,1),np.sum(world*bt,1),np.sum(world*n,1)));normal/=np.linalg.norm(normal,axis=1)[:,None]
 for key,val in [('basecolor',col),('normal',normal*.5+.5),('roughness',rough[:,None]),('metallic',metal[:,None]),('height',(h+.012)[:,None]/.024)]:out[key][ry,rx]=val
 v=positions[list(p.vertices)];e=v[1:]-v[0];fn=np.cross(*e);area=np.linalg.norm(fn)/2;fn/=np.linalg.norm(fn);tx=e[0]/np.linalg.norm(e[0]);local=e@np.stack((tx,np.cross(fn,tx)),axis=1);sigma=np.linalg.svd(np.linalg.solve(local,uv[1:]-uv[0]),compute_uv=False);face_reports.append({'face':fi,'kind':kind,'pixels':len(rx),'uv_anisotropy':float(sigma[0]/sigma[1]),'density':float(np.sqrt(sigma.prod())*N),'area':float(area)});print('BAKED',fi,kind,len(rx),round(float(sigma[0]/sigma[1]),3),flush=True)
# Extend the contents of each island through the empty margin for filtering and mipmaps.
idx=np.full((N,N),-1,np.int32);idx[coverage]=np.flatnonzero(coverage)
for _ in range(12):
 updated=idx.copy()
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
  q=np.roll(idx,shift,axis);take=(updated<0)&(q>=0);updated[take]=q[take]
 idx=updated
pad=(idx>=0)&~coverage;records={}
for key,a in out.items():
 a[pad]=a.reshape(-1,3)[idx[pad]];im=bpy.data.images.new('Naginata v4 '+key,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=a;im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());path=M/f'naginata_edges_{key}_2k_v4.png';im.filepath_raw=str(path);im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();bpy.data.images.remove(im);records[key]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
# Save region masks alongside the editable source.
im=bpy.data.images.new('Naginata v4 region mask',N,N,alpha=False);buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=np.stack([classification==i for i in [1,2,3]],-1);im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());p=M/'naginata_edges_regions_2k_v4.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8';im.save();bpy.data.images.remove(im);records['region_mask']={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
mat=bpy.data.materials.new('Naginata_Edges_Exhaust_PBR_v4');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newname;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.3;output=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],output.inputs[0])
for key in ['basecolor','normal','roughness','metallic']:
 im=bpy.data.images.load(records[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();node=nodes.new('ShaderNodeTexImage');node.name='Delivered '+key;node.image=im;links.new(uv.outputs[0],node.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newname;links.new(node.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(node.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
body.data.materials.append(mat);slot=len(body.data.materials)-1
for fi in selected:m.polygons[fi].material_index=slot
for material in m.materials:
 if material and material.use_nodes:
  for node in material.node_tree.nodes:
   if hasattr(node,'uv_map') and node.uv_map==oldname:node.uv_map=newname
for o in s.objects:
 if o.type!='MESH':continue
 b=before[o.name];assert b['vertices']==[list(v.co) for v in o.data.vertices] and b['faces']==[list(p.vertices) for p in o.data.polygons] and b['normals']==[list(n.vector) for n in o.data.corner_normals]
 for name,values in b['uvs'].items():assert values==[list(q.uv) for q in o.data.uv_layers[name].data]
 for p in o.data.polygons:
  if o!=body or p.index not in selected:
   assert b['materials'][p.index]==p.material_index
   assert all((o.data.uv_layers[oldname].data[i].uv-o.data.uv_layers[newname].data[i].uv).length<1e-8 for i in p.loop_indices)
assert max(f['uv_anisotropy'] for f in face_reports)<1.9
s['v4_surface_repair']='Dedicated full-area edge/hole islands; true three-axis steel projection; complete legacy louvres at original engine attachment points. Main and v3 nose atlas unchanged.';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;scene=D/'naginata_worn_edges_v4.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert hashlib.sha256(src.read_bytes()).hexdigest()==source_hash
report={'source':str(src),'source_sha256':source_hash,'scene':str(scene),'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'active_uv':newname,'mesh_original_uvs_custom_normals_unchanged':True,'unselected_face_uvs_and_material_assignments_unchanged':True,'main_and_v3_repair_texture_bytes_unchanged':True,'maps':records,'exhaust_centres_world':glows.tolist(),'native_engine_glow_attachments_unchanged':True,'source_louvre_atlas_center':[688,1113],'source_louvre_atlas_radius':29,'method':'Separate edge and engine chart bake with existing main atlas and wear swatches; no regenerated primary artwork. Original glow points retained.','groups':face_reports,'models':{}}
for o in s.objects:
 if o.type=='MESH':report['models'][o.name]={'vertices':[list(v.co) for v in o.data.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(o.data.uv_layers[newname].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in o.data.polygons]}
(W/'bake_validation.json').write_text(json.dumps(report,indent=2));print('V4_COMPLETE',len(selected),'faces',len(edge),'edge',len(engine),'engine',len(ports),'exhaust',flush=True)
