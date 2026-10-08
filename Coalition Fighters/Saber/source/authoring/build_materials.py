from pathlib import Path
import os
import bpy,numpy as np,json,hashlib
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['SABER_WORKSPACE']).resolve();W=D/'work/reconstruction_v1';M=D/'maps';N=1254
src=D/'saber_source_review.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];source_sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.context.view_layer.update()
before={o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'n':[list(n.vector) for n in o.data.corner_normals],'uv':{u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers}} for o in obs};newuv='Saber_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# Restore the missing transverse coordinate on the thin edge strips. Fit a
# metric plane to each strip while retaining its original location/long axis.
repairs=[]
# Expand collapsed transverse coordinates on small machinery strips only.
groups=[[90,91,105,112,113,486],[188],[192],[198],[202],[495,496],[498,499],[572,573],[574],[577],[580,581],[582],[585]]
o=bpy.data.objects['Sabre_Body'];m=o.data;uv=m.uv_layers[newuv]
for ids in groups:
 loops=[i for idx in ids for i in m.polygons[idx].loop_indices]
 p=np.array([m.vertices[m.loops[i].vertex_index].co[:] for i in loops]);q=np.array([uv.data[i].uv[:] for i in loops]);p0=p.mean(0);q0=q.mean(0)
 _,_,axes=np.linalg.svd(p-p0,full_matrices=False);xy=(p-p0)@axes[:2].T
 _,_,uvaxes=np.linalg.svd(q-q0,full_matrices=False);direction=uvaxes[0];along=(q-q0)@direction
 gradient=np.linalg.lstsq(xy,along,rcond=None)[0];scale=np.linalg.norm(gradient);assert scale>1e-8
 axis=gradient/scale;crossaxis=np.array([-axis[1],axis[0]]);crossuv=np.array([-direction[1],direction[0]])
 transverse=xy@crossaxis
 if np.sum(transverse*((q-q0)@crossuv))<0:crossuv=-crossuv
 out=q0+scale*((xy@axis)[:,None]*direction+transverse[:,None]*crossuv)
 for i,v in zip(loops,out):uv.data[i].uv=v
 repairs.append(dict(part=o.name,faces=ids,method='Metric planar machinery strip; preserve UV centroid and dominant mapped axis',original_uv=q.tolist(),uv=out.tolist()))
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def poly(p):
 p=np.array(p);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
# Coordinates trace the generated sheets, not brightness-derived bump relief.
regions={'hull': {'glass': [[(10, 218), (22, 218), (26, 223), (26, 241), (22, 246), (10, 246), (8, 242), (8, 223)], [(13, 267), (30, 267), (36, 274), (36, 359), (31, 367), (15, 367), (11, 359), (11, 274)], [(15, 391), (28, 391), (32, 397), (32, 415), (28, 422), (15, 422), (12, 417), (12, 396)], [(64, 232), (82, 232), (88, 238), (88, 257), (83, 263), (64, 263), (60, 257), (60, 238)], [(66, 281), (82, 281), (89, 287), (89, 360), (85, 369), (66, 369), (62, 362), (62, 290)], [(120, 289), (132, 289), (138, 296), (138, 379), (133, 387), (119, 387), (115, 381), (115, 298)], [(117, 410), (125, 408), (140, 424), (139, 431), (132, 436), (127, 434), (114, 420)], [(4, 1012), (21, 1012), (27, 1018), (27, 1039), (21, 1045), (3, 1045)], [(3, 1100), (19, 1100), (26, 1108), (26, 1193), (22, 1200), (2, 1200)]], 'glass_capsules': [], 'flat': [(165, 148, 284, 258), (105, 684, 324, 917), (1015, 1044, 1150, 1182), (1120, 130, 1210, 190), (875, 475, 1097, 495), (79, 1083, 230, 1127), (410, 965, 465, 1023), (545, 1, 627, 65), (480, 1138, 580, 1207), (1099, 464, 1175, 498), (982, 533, 998, 553)], 'vents': [((92, 39), (349, 39), 11, 1), ((91, 87), (351, 87), 10, 1), ((949, 34), (1180, 34), 13, 1), ((353, 239), (433, 239), 13, 2), ((793, 316), (1187, 316), 10, 1), ((698, 559), (817, 559), 12, 1), ((405, 665), (495, 665), 23, 3), ((889, 682), (933, 682), 12, 1), ((889, 754), (931, 754), 12, 1), ((129, 1036), (181, 1036), 11, 1), ((169, 1211), (396, 1211), 10, 1), ((754, 1159), (785, 1159), 7, 1)], 'circles': [(550, 299, 29), (271, 400, 28), (1152, 964, 33), (480, 741, 15), (552, 399, 15), (352, 997, 26), (514, 997, 26)], 'panels': [[(157, 0), (157, 126)], [(48, 113), (637, 113)], [(50, 0), (50, 179), (157, 179)], [(295, 0), (295, 215)], [(458, 111), (458, 273)], [(159, 126), (637, 126)], [(301, 217), (456, 217)], [(154, 309), (351, 309)], [(157, 516), (383, 516)], [(4, 447), (137, 447)], [(383, 418), (474, 418)], [(641, 113), (641, 476)], [(655, 113), (655, 793)], [(731, 214), (731, 346)], [(730, 284), (1230, 284)], [(879, 214), (879, 282)], [(1097, 215), (1097, 282)], [(1191, 214), (1191, 507)], [(661, 347), (1191, 347)], [(878, 352), (878, 474)], [(660, 472), (1097, 472)], [(49, 530), (49, 995)], [(68, 664), (68, 979)], [(290, 787), (290, 931)], [(333, 740), (454, 858)], [(332, 783), (655, 783)], [(445, 706), (445, 771)], [(507, 704), (507, 779)], [(558, 744), (657, 850)], [(457, 890), (611, 890)], [(458, 894), (458, 950)], [(288, 931), (289, 1172)], [(98, 929), (289, 929)], [(75, 981), (256, 981)], [(255, 952), (560, 952)], [(564, 956), (564, 1076)], [(291, 1078), (735, 1078)], [(455, 1104), (455, 1254)], [(869, 622), (869, 795)], [(979, 622), (979, 806)], [(1100, 643), (1194, 643)], [(980, 797), (1194, 797)], [(1056, 810), (1056, 1033)], [(655, 794), (760, 902)], [(667, 848), (850, 848)], [(759, 1018), (975, 1018)], [(976, 1020), (1195, 1233)]]}}
(W/'regions.json').write_text(json.dumps(dict(coordinate_resolution=N,atlases=regions,normal_source='Explicit structural shapes only; paint and panes are flat'),indent=2))
allmaps={};stats={};materials=[]
for atlas,OUT in [('hull',4096)]:
 reg=regions[atlas];h=np.zeros((N,N),np.float32);glass=h.copy();seal=h.copy();flat=h.copy();structure=h.copy();fins=h.copy();pan=h.copy()
 for p in reg['glass']:
  d=poly(p);glass=np.maximum(glass,smooth(0,2,d));seal=np.maximum(seal,smooth(-6,-2,d))
 for a,b,r in reg['glass_capsules']:
  d=capsule(a,b,r);glass=np.maximum(glass,smooth(0,2,d));seal=np.maximum(seal,smooth(-6,-2,d))
 for a,b,c,d in reg['flat']:flat=np.maximum(flat,smooth(0,2,poly([(a,b),(c,b),(c,d),(a,d)])))
 for a,b,r,count in reg['vents']:
  d=capsule(a,b,r);v=np.subtract(b,a);v=v/np.linalg.norm(v);across=-(X-a[0])*v[1]+(Y-a[1])*v[0];f=np.zeros_like(X)
  if count>1:
   pitch=2*r/(count+1)
   for i in range(count):f=np.maximum(f,1-smooth(pitch*.12,pitch*.35,np.abs(across-(i-(count-1)/2)*pitch)))
  f*=smooth(3,5,d);mask=smooth(0,1.5,d);z=-2.1*smooth(0,4,d)+2.4*f;h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,f)
 # Radiator ribs stay inside their traced recess boundaries.
 for points,positions in [([(125,523),(380,523),(380,620),(125,620)],range(138,380,23)), ([(386,433),(474,433),(474,620),(386,620)],range(393,474,23))]:
  d=poly(points);mask=smooth(0,2,d);f=np.zeros_like(X)
  for x in positions:f=np.maximum(f,1-smooth(2,5,np.abs(X-x)))
  f*=smooth(4,7,d);z=-1.3*smooth(0,4,d)+1.7*f;h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,f)
 rr=np.hypot(X-961,Y-884);d=58-rr;mask=smooth(0,2,d);f=np.zeros_like(X)
 for y in range(834,939,14):f=np.maximum(f,1-smooth(1.3,3.4,np.abs(Y-y)))
 f*=smooth(4,7,d);z=-1.3*smooth(0,4,d)+1.7*f;h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,f)
 for cx,cy,r in reg['circles']:
  rr=np.hypot(X-cx,Y-cy);mask=1-smooth(r,r+2,rr);z=-1.2*(1-smooth(r-3,r,rr));h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask)
 for path in reg['panels']:
  for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.3,capsule(a,b,1.6)))
 protected=np.maximum(flat,seal);pan*=1-np.maximum(protected,structure);h-=.6*pan;h*=1-protected
 im=bpy.data.images.load(str(M/f'saber_{atlas}_generated_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
 mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);paint=smooth(.12,.3,sat);metal=(1-paint)*smooth(.15,.48,lum)*.78;metal=metal*(1-structure)+(.08+.74*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.04*pan
 local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.53*metal+.05*wear,.49,.91);rough=rough*(1-structure)+(.9-.38*fins)*structure;rough=rough*(1-pan)+.87*pan;rough=rough*(1-flat)+.81*flat;rough=rough*(1-seal)+.83*seal;rough=rough*(1-glass)+.16*glass
 dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[seal>.05]=(0,0,1);records={}
 def save(a,key,colorspace='Non-Color'):
  b=np.ones((N,N,4),np.float32);b[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Saber '+atlas+' '+key,N,N,alpha=False,float_buffer=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(b[::-1]).ravel());im.scale(OUT,OUT)
  if key=='normal':
   nb=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(nb);na=nb.reshape(-1,4);nn=na[:,:3]*2-1;nn/=np.maximum(np.linalg.norm(nn,axis=-1,keepdims=True),1e-8);na[:,:3]=nn*.5+.5;im.pixels.foreach_set(na.ravel())
  p=M/f'saber_{atlas}_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
 maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
 for key,a in [('height',(h+8)/12),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
 mat=bpy.data.materials.new('Saber_Worn_'+atlas+'_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
 for key,im in maps.items():
  im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT';links.new(uv.outputs[0],tx.inputs[0])
  if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
  else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 materials.append(mat);allmaps[atlas]=records;stats[atlas]=dict(glass_texels=int((glass>.99).sum()),glass_metallic_max=float(metal[glass>.99].max()) if glass.max()>0 else None,glass_roughness=.16 if glass.max()>0 else None,structural_height_min=float(h.min()),height_max=float(h.max()));print('MAPS COMPLETE',atlas,flush=True)
models={};aspects=[]
for o in obs:
 m=o.data;m.materials[0]=materials[0];b=before[o.name];assert b['v']==[list(v.co) for v in m.vertices] and b['f']==[list(p.vertices) for p in m.polygons] and b['n']==[list(n.vector) for n in m.corner_normals]
 for name,values in b['uv'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 models[o.name]={'part_index':o['native_part_index'],'vertices':[list(v.co) for v in m.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':o['native_material_indices'][p.index],'hidden':p.material_index==1} for p in m.polygons]}
 for p in m.polygons:
  if p.material_index==1:continue
  pts=np.array([list(o.matrix_world@m.vertices[i].co) for i in p.vertices]);e=pts[1:]-pts[0];n=np.cross(*e);n/=max(np.linalg.norm(n),1e-9);t=e[0]/np.linalg.norm(e[0]);local=e@np.stack((t,np.cross(n,t)),axis=1);q=np.array([list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices]);sing=np.linalg.svd(np.linalg.solve(local,q[1:]-q[0]),compute_uv=False);aspects.append((o.name,p.index,float(sing[0]/max(sing[1],1e-12))))
assert max(a[2] for a in aspects)<6.1,sorted(aspects,key=lambda a:-a[2])[:10]
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for attempt in range(100):
  prior=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if not all(.07<t.x<.93 and .07<t.y<.93 and t.z>0 for t in q):cam.location=prior;break
scene=D/'saber_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.image_settings.color_depth='8';s.cycles.samples=24;s.render.resolution_x=1440;s.render.resolution_y=1080;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
report=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),active_uv=newuv,parts=2,stored_triangles=612,visible_triangles=sum(1 for o in obs for p in o.data.polygons if p.material_index!=1),original_geometry_normals_and_uv_layers_preserved=True,uv_repairs=repairs,max_visible_uv_anisotropy=max(a[2] for a in aspects),maps=allmaps,models=models,structural_height_only=True,emissives='deferred',runtime_visual_validation='pending_user_review',statistics=stats);(W/'validation.json').write_text(json.dumps(report,indent=2));print('SABER_PBR_COMPLETE',stats,flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
