from pathlib import Path
import bpy,numpy as np,json,hashlib,struct,math,os
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
D=Path('${PROWLER_WORKSPACE}');W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'prowler_source_review.blend'));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
uvname='Prowler_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=uvname,do_init=True);o.data.uv_layers.active=u;u.active_render=True
R={
'hull1':{
'flat':[[132,143,213,190],[8,172,61,208]],
'panels':[
[[10,0],[10,40]],[[0,18],[12,18]],[[0,38],[30,38]],[[29,40],[36,38],[46,38],[59,51],[59,94],[53,99],[39,99],[30,90],[30,40]],
[[13,44],[23,44],[27,48],[27,83],[21,91],[11,83],[11,49],[13,44]],[[2,84],[4,82],[18,97],[18,101],[0,101]],
[[65,51],[137,51]],[[65,58],[137,58]],[[62,51],[62,115]],[[65,96],[99,96]],[[62,142],[0,142]],[[64,114],[141,114]],
[[6,104],[6,144]],[[11,107],[45,107],[45,135],[11,135],[11,107]],[[0,146],[38,146],[38,165],[0,165]],
[[0,169],[35,169],[35,210],[0,210]],[[4,193],[60,193]],[[4,204],[60,204]],
[[72,0],[72,51]],[[135,0],[135,89]],[[75,29],[135,29]],[[75,50],[135,50]],
[[138,90],[203,90]],[[160,82],[199,82],[199,143],[160,143],[160,82]],[[163,103],[195,103]],[[163,120],[195,120]],
[[205,61],[250,61]],[[207,60],[207,138]],[[206,103],[250,103]],[[244,60],[244,138]],
[[133,167],[200,167]],[[133,190],[200,190]],[[133,202],[182,202]],[[136,211],[198,211]],[[146,208],[146,236]],
[[70,216],[199,216]],[[88,216],[88,255]],[[135,216],[135,255]],[[144,235],[198,235]],
[[199,190],[231,190]],[[200,197],[232,197],[232,237],[200,237],[200,197]],[[236,201],[236,255]],[[250,201],[250,255]],
[[1,247],[31,247]],[[30,239],[32,235],[54,235],[58,239],[58,249],[53,253],[32,253],[30,249],[30,239]],[[62,143],[62,163]],[[61,167],[61,211]]],
'slots':[[[18,50],[18,82],3.4],[[77,66],[77,104],2.9],[[93,66],[93,104],2.9],[[119,84],[119,96],3],[[3,154],[33,154],3.7],[[73,172],[118,172],3.1],[[205,191],[229,191],1.4],[[164,245],[229,245],3.0],[[43,58],[52,58],1.6],[[43,72],[52,72],1.6],[[43,87],[52,87],1.6]],
'circles':[[31,18,7.1],[54,18,7.1],[113,63,3.2],[124,63,3.2],[225,79,11],[225,121,11],[17,115,3.5],[35,115,3.5],[17,128,3.5],[35,128,3.5],[152,103,3.7],[224,159,6.9],[170,15,8],[213,15,8],[183,54,5],[195,43,5],[207,33,5],[216,210,4.5],[216,224,4.5],[43,244,7]],
'radiators':[
{'polygon':[[155,33],[181,31],[182,35],[178,42],[155,44],[153,41]],'axis':'x','centres':list(range(156,180,2))},
{'polygon':[[164,90],[192,90],[192,102],[164,102]],'axis':'x','centres':[167,173,179,185,191]},
{'polygon':[[162,134],[192,134],[192,143],[162,143]],'axis':'x','centres':[165,171,177,183,189]},
{'polygon':[[69,13],[124,13],[124,24],[69,24]],'axis':'y','centres':[16,19,22]},
{'polygon':[[51,149],[75,149],[75,164],[51,164]],'axis':'y','centres':[151,154,157,160,163]}],
'glass':[
[[91.5,39.9],[128,39.9],[128,43.5],[91.5,43.5]],
[[168,123.4],[191.7,123.4],[189,126.5],[171,126.5]],
[[148.5,153.9],[171.9,153.9],[171.9,157.5],[148.5,157.5]],
[[184.5,153.8],[191.9,153.8],[191.9,157.5],[184.5,157.5]],
[[86.4,186.5],[109.3,186.5],[105.7,190.3],[86.4,190.3]],
[[114.4,190.8],[119.1,192.3],[119.1,198],[112,198],[110.7,196.4],[110.7,195]],
[[245.1,242.9],[251,242.9],[251,246.7],[245.1,246.7]]],
'mullions':[[[105.5,40],[105.5,44]],[[111,40],[111,44]],[[118,40],[118,44]],[[178,123],[178,127]],[[182,123],[182,127]],[[96.5,186],[96.5,191]]]
},
'hull2':{
'flat':[[37,75,94,111],[75,169,94,228],[177,116,199,135],[205,226,237,242],[32,239,76,256]],
'panels':[
[[9,17],[10,15],[22,15],[22,55],[9,55],[9,17]],[[23,15],[31,7],[47,7],[51,14],[51,53],[44,67],[33,67],[23,57],[23,15]],
[[52,14],[59,14],[59,53],[52,53],[52,14]],[[60,14],[64,8],[83,8],[91,15],[91,57],[81,68],[68,68],[60,57],[60,14]],
[[96,0],[96,114]],[[96,35],[146,35]],[[109,0],[109,114]],[[15,73],[31,73],[31,103],[15,103],[15,73]],[[0,108],[29,108]],
[[6,159],[95,159],[95,123],[44,123],[30,136]],[[7,169],[75,169],[75,235],[7,235],[7,169]],[[7,191],[75,191]],[[7,212],[75,212]],
[[0,239],[76,239]],[[13,242],[30,242]],[[19,242],[19,256]],[[77,169],[114,169]],[[77,184],[114,184]],[[77,213],[114,213]],[[116,114],[116,256]],
[[159,8],[217,8]],[[169,8],[169,20]],[[201,8],[201,20]],[[159,20],[217,20]],
[[139,62],[246,62],[246,89],[139,89],[139,62]],[[139,75],[246,75]],[[171,62],[171,89]],[[182,62],[182,89]],[[221,62],[221,89]],
[[152,115],[209,115],[209,143],[171,143]],[[211,114],[251,114]],[[251,114],[251,220]],
[[129,143],[238,143],[246,150],[246,184],[238,191],[129,191]],[[127,161],[246,161]],[[127,171],[246,171]],[[150,143],[150,161]],[[150,171],[150,191]],[[162,161],[162,171]],[[221,143],[221,191]],
[[171,194],[197,194],[197,253],[133,253]],[[171,216],[244,216]],[[209,197],[209,220]],[[211,222],[243,222],[243,247],[211,247],[211,222]]],
'slots':[[[36,22],[36,52],4.2],[[77,22],[77,52],3.8],[[20,79],[25,79],2.1],[[20,95],[25,95],2.1],[[223,51],[245,51],2.2],[[223,100],[246,100],2.2],[[35,184],[62,184],4.2],[[34,222],[62,222],3.1],[[148,152],[203,152],3.6],[[150,179],[205,179],3.6],[[125,125],[141,125],2.1],[[122,205],[139,205],2.2],[[137,241],[187,241],2.6]],
'circles':[[72,143,10],[219,159,3.4],[130,14,4],[143,14,4],[230,13,4],[244,13,4]],
'radiators':[
{'polygon':[[150,32],[213,32],[213,56],[150,56]],'axis':'x','centres':list(range(152,213,4))},
{'polygon':[[151,94],[206,94],[213,100],[213,113],[151,113]],'axis':'x','centres':list(range(153,213,4))},
{'polygon':[[1,116],[21,116],[21,154],[1,154]],'axis':'x','centres':[3,7,11,15,19]},
{'polygon':[[1,73],[11,73],[11,90],[1,90]],'axis':'y','centres':[75,79,83,87]},
{'polygon':[[1,194],[5,194],[5,213],[1,213]],'axis':'y','centres':[196,200,204,208]}],
'glass':[],'mullions':[]}}
(W/'regions.json').write_text(json.dumps(dict(coordinate_size=[256,256],regions=R,policy='Follow native panel layout; paint and markings flat; only existing blue glazing emits; vents remain dark'),indent=2)+'\n')
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
for role,reg in R.items():
 h=np.zeros((N,N),np.float32);flat=h.copy();structure=h.copy();fins=h.copy();pan=h.copy();glass=h.copy()
 for a,b,c,d in reg['flat']:flat=np.maximum(flat,smooth(0,.4,poly([[a,b],[c,b],[c,d],[a,d]])))
 for a,b,r in reg['slots']:
  dist=capsule(a,b,r);mask=smooth(0,.45,dist);h-=.78*smooth(0,.95,dist);structure=np.maximum(structure,mask)
 for cx,cy,r in reg['circles']:
  dist=r-np.hypot(X-cx,Y-cy);mask=smooth(0,.4,dist);h=h*(1-mask)-.57*smooth(0,.9,dist)*mask;structure=np.maximum(structure,mask)
 for rad in reg['radiators']:
  dist=poly(rad['polygon']);mask=smooth(0,.4,dist);pos=X if rad['axis']=='x' else Y
  rib=np.maximum.reduce([1-smooth(.18,.48,np.abs(pos-c)) for c in rad['centres']])*smooth(.5,1.1,dist)
  h=h*(1-mask)+(-.68*smooth(0,.9,dist)+.39*rib)*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,rib)
 for path in reg['panels']:
  for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,.27,capsule(a,b,.38)))
 pan*=1-np.maximum(flat,structure);h-=.23*pan;h*=1-flat
 for points in reg['glass']:glass=np.maximum(glass,smooth(0,.36,poly(points)))
 for a,b in reg['mullions']:glass*=1-smooth(0,.15,capsule(a,b,.17))
 h=h*(1-glass)-.7*glass
 file='prowler_hull1_glass_v1.png' if role=='hull1' else 'prowler_hull2_reconstructed_v1.png'
 im=bpy.data.images.load(str(M/file),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
 mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.10,.30,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.14,.55,lum)*.60;metal=metal*(1-structure)+(.09+.42*fins)*structure;metal*=1-flat;metal=metal*(1-pan)+.05*pan;metal=metal*(1-glass)+.07*glass
 rough=np.clip(.78-.21*metal,.56,.85);rough=rough*(1-structure)+(.84-.22*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.76*flat;rough=rough*(1-glass)+.27*glass
 dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 rec={}
 def save(a,key,cs='Non-Color'):
  rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Prowler '+role+' '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
  if key=='normal':
   b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);v=b.reshape(-1,4);n=v[:,:3]*2-1;n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8);v[:,:3]=n*.5+.5;im.pixels.foreach_set(v.ravel())
  p=M/f'prowler_{role}_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);rec[key]=dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT]);im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=cs;return im
 maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
 # Preserve frame/mullion darkness; emission exists only in the traced glass interior.
 if reg['glass']:maps['emissive']=save(glass[:,:,None]*np.array([.25,.43,.56],np.float32),'emissive','sRGB')
 for key,a in [('height',(h+2)/4),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint),('glass',glass)]:bpy.data.images.remove(save(a,key))
 mat=bpy.data.materials.new('Prowler_Worn_'+role+'_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=uvname;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.35;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
 for key,im in maps.items():
  im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT';links.new(uv.outputs[0],tx.inputs[0])
  if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=uvname;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
  elif key=='emissive':links.new(tx.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1.0
  else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 materials[role]=mat;records[role]=rec
for o in obs:
 if o['native_part_index']!=5:o.data.materials[0]=materials['hull1'];o.data.materials[1]=materials['hull2']
 b=before[o.name];assert b[0]==[list(v.co) for v in o.data.vertices] and b[1]==[list(p.vertices) for p in o.data.polygons] and b[2]==[list(n.vector) for n in o.data.corner_normals]
 for name,values in b[3].items():assert values==[list(q.uv) for q in o.data.uv_layers[name].data]
# Native Alliance small turret is a shared model using the shared Missiles atlas.
# Preserve it unchanged; the instances here exist for authoring assembly review only.
im=bpy.data.images.load(str(D/'source/missiles.png'));im.pack();tm=bpy.data.materials.new('Native shared Alliance small turret');tm.use_nodes=True;tx=tm.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;tm.node_tree.links.new(tx.outputs[0],tm.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);tm.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
parts=json.loads((D/'source/native_parts.json').read_text());turrets=json.loads((D/'source/turret_parts.json').read_text());body=next(o for o in obs if o['native_part_index']==2);origin=Vector(parts[2]['origin']);audit=[]
for mount,a in enumerate(x for x in parts[2]['attachments'] if x['kind']==1):
 raw=bytes.fromhex(a['raw_hex']);pos=Vector(struct.unpack_from('<3f',raw,4))+origin;values=struct.unpack_from('<9f',raw,16);rot=Matrix([values[i:i+3] for i in range(0,9,3)])
 for p in turrets[1:]:
  lod=p['lods'][0];verts=[Vector(v)+Vector(p['origin']) for v in lod['vertices']];faces=[];uvs=[]
  for f in lod['faces']:
   idx=f['vertices'][:];uv=f['uv'][:];pts=[verts[j] for j in idx]
   if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(Vector(f['normal']))<0:idx[1],idx[2]=idx[2],idx[1];uv[1],uv[2]=uv[2],uv[1]
   faces.append(idx);uvs.extend(uv)
  mesh=bpy.data.meshes.new(f'Mount{mount+1}_{p["name"]}');mesh.from_pydata([rot@v+pos for v in verts],[],faces);mesh.update();u=mesh.uv_layers.new(name=uvname)
  for q,v in zip(u.data,uvs):q.uv=v
  for face in mesh.polygons:face.use_smooth=True
  mesh.normals_split_custom_set([rot@Vector(lod['normals'][l.vertex_index]) for l in mesh.loops]);mesh.materials.append(tm);o=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(o);o.matrix_world=body.matrix_world.copy();o['source_native_file']='14_al_STUR.SHP';o['source_native_part']=p['index'];o['mount']=mount;o['authoring_only_mounted_instance']=True;audit.append(dict(name=o.name,faces=len(faces)))
visible=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for _ in range(100):
  bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in visible for v in o.data.vertices]
  if all(.06<t.x<.94 and .06<t.y<.94 and t.z>0 for t in q):break
  cam.location*=1.04
scene=D/'prowler_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene))
report=dict(scene=str(scene),scene_sha256=sha(scene),source_scene_sha256=sha(D/'prowler_source_review.blend'),active_uv=uvname,original_geometry_normals_uvs_preserved=True,uv_repairs=[],maps=records,structural_height_only=True,mounted_turret_instances=audit,shared_turret_runtime='unchanged native 14_al_STUR.SHP and Missiles texture',emissives='traced original blue window interiors only; static first-pass',runtime_visual_validation='pending_user_review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
print('PROWLER_MATERIALS_VALIDATED',flush=True)
