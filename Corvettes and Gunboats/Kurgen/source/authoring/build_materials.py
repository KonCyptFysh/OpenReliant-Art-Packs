from pathlib import Path
import bpy,numpy as np,json,hashlib,struct,math,os
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['KURGEN_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';OUT=4096;N=1254
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'kurgen_source_review.blend';source_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
# Model parts preserve original per-corner UVs and normals. No geometry repair is needed.
baseobs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in baseobs}
newuv='Kurgen_Delivery_UV_v1'
for o in baseobs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# All semantic regions are authored on a 256-square coordinate grid and saved for further edits.
R={
'hull':{
 'flat':[[83,17,120,41],[218,147,244,178],[54,4,66,52],[179,60,247,74],[66,107,104,125],[66,183,93,198],[157,194,166,214],[168,192,179,222],[22,141,39,156]],
 'panels':[
 [[0,8],[27,8],[27,0]],[[1,69],[43,69],[43,103]],[[0,84],[26,84]],[[46,65],[57,65]],[[46,71],[57,71]],[[46,76],[57,76]],[[46,82],[57,82]],
 [[67,60],[247,60],[247,73],[65,73],[65,60]],[[88,60],[88,73]],[[110,60],[110,73]],[[132,60],[132,73]],[[156,60],[156,73]],[[177,60],[177,73]],[[201,60],[201,73]],[[225,60],[225,73]],
 [[63,75],[188,75],[188,106],[64,106]],[[64,87],[188,87]],[[118,75],[118,87]],[[103,98],[103,106]],
 [[80,9],[84,6],[120,6],[125,11],[125,50],[120,54],[85,54],[80,49],[80,9]],[[87,7],[87,50]],[[82,15],[124,15]],[[82,40],[124,40]],[[106,7],[106,50]],
 [[134,13],[139,6],[147,6],[153,12],[153,50],[148,55],[139,55],[134,50],[134,13]],[[134,28],[153,28]],
 [[169,8],[174,4],[242,4],[247,9],[247,50],[242,55],[169,55],[169,8]],[[169,11],[246,11]],[[184,5],[184,11]],[[223,5],[223,11]],[[221,17],[221,40]],
 [[104,107],[251,107]],[[212,108],[212,126]],[[227,108],[227,126]],[[64,118],[104,118]],[[86,107],[86,126]],
 [[17,138],[22,136],[43,136],[43,185],[26,185],[17,177],[17,138]],[[8,185],[44,185]],[[12,197],[45,197]],[[49,189],[49,240]],
 [[55,163],[104,163]],[[70,169],[91,169],[97,175],[97,199],[62,199],[62,175],[70,169]],
 [[60,201],[103,201],[106,204],[106,239],[62,239],[60,237],[60,201]],[[61,220],[103,220]],[[98,201],[98,239]],
 [[151,147],[171,147],[182,158],[182,191],[154,191],[151,188],[151,147]],[[153,191],[204,191]],[[171,192],[171,224]],[[154,224],[168,243],[200,243],[200,223]],[[176,222],[196,222]],[[178,224],[178,242]],
 [[223,139],[227,134],[234,134],[240,140],[240,234],[236,239],[219,239],[216,233],[216,146],[223,139]],[[216,172],[240,172]],[[222,177],[222,235]],
 [[5,241],[247,241]],[[23,241],[23,255]],[[57,241],[57,255]],[[97,242],[97,255]],[[140,243],[140,255]],[[166,243],[166,255]],[[244,190],[251,190]]],
 'slots':[[[176,14],[238,14],2.7],[[176,44],[238,44],2.7],[[186,28],[218,28],4.4],[[68,82],[180,82],3.6],[[68,95],[180,95],3.6],[[15,51],[15,60],2.5],[[34,51],[34,60],2.5],[[120,207],[120,217],3],[[142,207],[142,217],3],[[66,177],[88,177],2.6],[[224,190],[224,221],2.8],[[238,190],[238,221],2.8],[[41,106],[41,120],3],[[100,133],[100,166],2.8],[[100,173],[100,178],2.7],[[188,196],[188,206],2.6],[[188,213],[188,235],2.7]],
 'circles':[[11,26,4.4],[31,74,5.6],[31,87,5.6],[10,97,7],[10,120,7],[142,13,6],[142,46,6],[209,88,8],[233,88,8],[117,147,6],[117,165,6],[117,183,6],[140,154,5],[140,169,5],[140,185,5],[59,163,3.6],[70,163,3.6],[81,163,3.6],[91,163,3.6],[118,242,4.2],[135,242,4.2],[28,221,6],[70,208,5],[70,229,5]],
 'radiators':[{'polygon':[[30,18],[41,18],[44,24],[44,30],[40,35],[33,35],[29,31],[29,23]],'axis':'y','centres':[21,24,27,30,33]}, {'polygon':[[55,132],[67,132],[67,154],[55,154]],'axis':'y','centres':[135,139,143,147,151]}, {'polygon':[[159,13],[165,13],[165,49],[159,49]],'axis':'y','centres':list(range(15,49,2))}]
},
 'turret':{
 'flat':[[65,91,108,128],[0,2,8,42],[0,80,41,101],[0,158,42,183],[54,145,122,171],[157,132,222,143],[157,157,222,167],[229,139,246,163],[68,189,101,198],[68,215,103,221]],
 'panels':[
 [[11,0],[11,43],[15,47],[32,47],[32,0]],[[11,48],[11,70]],[[32,48],[32,69]],[[50,50],[128,50],[128,69],[50,69],[50,50]],[[0,70],[130,70]],[[50,80],[135,80]],
 [[55,90],[62,86],[119,86],[127,93],[127,127],[120,133],[52,133],[48,129],[48,98],[55,90]],[[65,90],[65,129]],[[111,90],[111,131]],
 [[137,52],[243,52],[247,59],[247,103],[239,110],[137,110],[137,52]],[[191,65],[245,65]],[[188,86],[245,86]],[[223,65],[223,86]],[[136,99],[185,99]],[[224,88],[224,110]],
 [[138,114],[232,114],[232,122],[138,122],[138,114]],[[156,128],[223,128],[223,172],[156,172],[156,128]],[[139,134],[153,134]],[[137,173],[244,173]],
 [[10,183],[17,179],[26,179],[34,186],[34,222],[27,230],[18,230],[10,221],[10,183]],[[45,180],[64,180],[64,222],[46,222],[46,180]],
 [[50,224],[124,224],[127,229],[127,245],[50,245],[46,240],[46,228],[50,224]],[[86,225],[86,243]],
 [[141,190],[245,190],[245,221],[137,221],[137,193],[141,190]],[[175,191],[175,200]],[[218,191],[218,200]],[[174,217],[174,222]],
 [[138,225],[246,225],[246,245],[138,245],[138,225]],[[169,225],[169,245]],[[217,225],[217,245]]],
 'slots':[[[173,24],[204,24],3.3],[[17,23],[17,39],3.5],[[18,198],[18,219],3.2],[[15,109],[22,109],2.5],[[15,121],[22,121],2.5],[[15,133],[22,133],2.5],[[15,146],[22,146],2.5],[[186,228],[193,228],1.2],[[182,231],[182,236],1.2],[[206,231],[206,236],1.2]],
 'circles':[[164,81,10],[171,206,7.5],[209,206,7.5],[154,235,5.5],[230,235,5.5],[72,234,6],[109,234,6],[144,29,2.6],[232,29,2.6]],
 'radiators':[{'polygon':[[173,141],[213,141],[219,147],[218,155],[211,160],[172,160],[167,153],[167,147]],'axis':'y','centres':[145,150,155]}, {'polygon':[[71,197],[99,197],[103,202],[103,208],[98,212],[71,212],[67,207],[67,202]],'axis':'y','centres':[200,205,210]}]
}}
(W/'regions.json').write_text(json.dumps({'coordinate_size':[256,256],'regions':R,'policy':'Structural relief only. Painted stars and caution graphics remain flat. No invented glazing.'},indent=2)+'\n')
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=(xx+.5)*256/N;Y=(yy+.5)*256/N
def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def poly(points):
 p=np.array(points);inside=np.zeros((N,N),bool);d=np.full((N,N),1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  d=np.minimum(d,-capsule(a,b,0));inside^=((a[1]>Y)!=(b[1]>Y))&(X<(b[0]-a[0])*(Y-a[1])/(b[1]-a[1]+1e-10)+a[0])
 return np.where(inside,d,-d)
records={};materials={}
for role,regions in R.items():
 h=np.zeros((N,N),np.float32);flat=h.copy();structure=h.copy();fins=h.copy();pan=h.copy()
 for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,.4,poly([[a,b],[c,b],[c,d],[a,d]])))
 for a,b,r in regions['slots']:
  dist=capsule(a,b,r);mask=smooth(0,.4,dist);h-=.45*smooth(0,.8,dist);structure=np.maximum(structure,mask)
 for cx,cy,r in regions['circles']:
  dist=r-np.hypot(X-cx,Y-cy);mask=smooth(0,.4,dist);h=h*(1-mask)-.3*smooth(0,.8,dist)*mask;structure=np.maximum(structure,mask)
 for rad in regions['radiators']:
  dist=poly(rad['polygon']);mask=smooth(0,.35,dist);pos=X if rad['axis']=='x' else Y
  rib=np.maximum.reduce([1-smooth(.15,.4,np.abs(pos-c)) for c in rad['centres']])*smooth(.5,1.0,dist)
  h=h*(1-mask)+(-.4*smooth(0,.8,dist)+.22*rib)*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,rib)
 for path in regions['panels']:
  for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,.23,capsule(a,b,.38)))
 pan*=1-np.maximum(flat,structure);h-=.12*pan;h*=1-flat
 im=bpy.data.images.load(str(M/f'kurgen_{role}_reconstructed_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
 mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.10,.30,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.14,.55,lum)*.60;metal=metal*(1-structure)+(.09+.42*fins)*structure;metal*=1-flat;metal=metal*(1-pan)+.06*pan
 rough=np.clip(.79-.21*metal,.56,.85);rough=rough*(1-structure)+(.83-.23*fins)*structure;rough=rough*(1-pan)+.85*pan;rough=rough*(1-flat)+.77*flat
 dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 rec={}
 def save(a,key,colorspace='Non-Color'):
  rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Kurgen '+role+' '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
  if key=='normal':
   buf=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(buf);v=buf.reshape(-1,4);norm=v[:,:3]*2-1;norm/=np.maximum(np.linalg.norm(norm,axis=-1,keepdims=True),1e-8);v[:,:3]=norm*.5+.5;im.pixels.foreach_set(v.ravel())
  p=M/f'kurgen_{role}_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);rec[key]=dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT]);im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
 maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
 for key,a in [('height',(h+2)/4),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
 mat=bpy.data.materials.new('Kurgen_Worn_'+role+'_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
 for key,im in maps.items():
  im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT';links.new(uv.outputs[0],tx.inputs[0])
  if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
  else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 materials[role]=mat;records[role]=rec
for o in baseobs:
 if o['native_part_index']==0:o.data.materials[0]=materials['hull']
 b=before[o.name];assert b[0]==[list(v.co) for v in o.data.vertices] and b[1]==[list(p.vertices) for p in o.data.polygons] and b[2]==[list(n.vector) for n in o.data.corner_normals]
 for name,values in b[3].items():assert values==[list(q.uv) for q in o.data.uv_layers[name].data]
# Three mounted instances for authoring inspection; transforms follow native attachment orientation.
parts=json.loads((D/'source/native_parts.json').read_text());turrets=json.loads((D/'source/turret_parts.json').read_text());body=next(o for o in baseobs if o['native_part_index']==0);origin=Vector(parts[0]['origin']);audit=[]
for mount,a in enumerate(x for x in parts[0]['attachments'] if x['kind']==1):
 raw=bytes.fromhex(a['raw_hex']);pos=Vector(struct.unpack_from('<3f',raw,4))+origin;values=struct.unpack_from('<9f',raw,16);rot=Matrix([values[i:i+3] for i in range(0,9,3)])
 for p in turrets[:3]:
  lod=p['lods'][0];verts=[Vector(v)+Vector(p['origin']) for v in lod['vertices']];faces=[];uvs=[]
  for f in lod['faces']:
   idx=f['vertices'][:];uv=f['uv'][:];pts=[verts[j] for j in idx]
   if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(Vector(f['normal']))<0:idx[1],idx[2]=idx[2],idx[1];uv[1],uv[2]=uv[2],uv[1]
   faces.append(idx);uvs.extend(uv)
  mesh=bpy.data.meshes.new(f'Mount{mount+1}_{p["name"]}');mesh.from_pydata([rot@v+pos for v in verts],[],faces);mesh.update();u=mesh.uv_layers.new(name=newuv)
  for q,v in zip(u.data,uvs):q.uv=v
  for face in mesh.polygons:face.use_smooth=True
  mesh.normals_split_custom_set([rot@Vector(lod['normals'][l.vertex_index]) for l in mesh.loops]);mesh.materials.append(materials['turret']);o=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(o);o.matrix_world=body.matrix_world.copy();o['source_native_file']='10_Rus_STUR.SHP';o['source_native_part']=p['index'];o['mount']=mount; o['authoring_only_mounted_instance']=True;audit.append(dict(name=o.name,faces=len(faces),vertices=len(verts)))
obs=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for _ in range(100):
  bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if all(.06<t.x<.94 and .06<t.y<.94 and t.z>0 for t in q):break
  cam.location*=1.04
scene=D/'kurgen_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==source_sha
report=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=sha(scene),active_uv=newuv,original_geometry_normals_and_uv_layers_preserved=True,uv_repairs=[],maps=records,structural_height_only=True,mounted_turret_instances=audit,painted_graphics_flat=True,emissives='deferred',wreck='original DAM_1 retained',runtime_visual_validation='pending_user_review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('KURGEN_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
