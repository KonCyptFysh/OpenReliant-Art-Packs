import os
from pathlib import Path
import bpy,numpy as np,json,hashlib
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/reconstruction_v1';M=D/'maps';N=1254
src=D/'basilisk_source_review.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];source_sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.context.view_layer.update()
before={o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'n':[list(n.vector) for n in o.data.corner_normals],'uv':{u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers}} for o in obs};newuv='Basilisk_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# Restore the missing transverse coordinate on the thin edge strips. Fit a
# metric plane to each strip while retaining its original location/long axis.
repairs=[]
# Expand collapsed transverse coordinates on small machinery strips only.
groups=[[244,245],[260,261],[286,287],[318,319],[324,325],[349,350],[355,356],[402,403],[434,435]]
o=bpy.data.objects['Basalisk'];m=o.data;uv=m.uv_layers[newuv]
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
regions={'hull': {'glass': [[(838, 39), (889, 39), (892, 44), (892, 70), (887, 73), (838, 73)], [(930, 58), (971, 79), (1008, 103), (1008, 106), (944, 106), (930, 93)], [(847, 354), (883, 354), (889, 360), (889, 402), (883, 407), (847, 407), (842, 402), (842, 360)], [(847, 445), (883, 445), (889, 452), (889, 552), (883, 558), (849, 558), (843, 551), (843, 452)]], 'glass_capsules': [], 'flat': [(90, 52, 183, 115), (637, 348, 682, 424), (961, 118, 1020, 150), (577, 690, 786, 867), (1159, 1080, 1233, 1115), (161, 393, 564, 435), (162, 558, 563, 588), (911, 344, 1014, 378), (467, 1166, 720, 1204), (116, 463, 153, 524), (42, 108, 66, 138), (190, 106, 220, 136), (46, 649, 124, 678)], 'vents': [((230, 489), (501, 489), 23, 3), ((437, 775), (437, 957), 17, 1), ((510, 775), (510, 958), 17, 1), ((47, 1144), (47, 1186), 9, 1), ((77, 1119), (77, 1177), 9, 1), ((112, 1118), (112, 1170), 9, 1), ((146, 1118), (146, 1162), 9, 1), ((181, 1118), (181, 1155), 9, 1), ((102, 219), (115, 219), 22, 3), ((99, 309), (112, 309), 19, 2), ((731, 101), (751, 101), 17, 1), ((731, 165), (751, 165), 16, 1), ((731, 237), (751, 237), 16, 1), ((731, 310), (751, 310), 16, 1), ((895, 194), (909, 194), 13, 1), ((895, 249), (909, 249), 13, 1), ((1091, 411), (1091, 548), 8, 1), ((861, 603), (861, 635), 7, 1), ((860, 755), (860, 798), 7, 1), ((941, 784), (941, 820), 6, 1), ((941, 882), (941, 925), 6, 1)], 'circles': [(1097, 943, 17), (1097, 995, 17), (1098, 1050, 16), (1213, 1194, 22)], 'panels': [[(231, 39), (231, 168)], [(51, 142), (505, 142)], [(167, 145), (167, 395)], [(269, 55), (269, 131)], [(366, 39), (367, 176)], [(320, 57), (320, 130)], [(51, 350), (508, 350)], [(322, 330), (322, 392)], [(44, 399), (558, 399)], [(113, 404), (113, 580)], [(45, 455), (112, 455)], [(45, 541), (112, 541)], [(50, 590), (564, 590)], [(619, 82), (619, 563)], [(690, 63), (690, 449)], [(632, 177), (792, 177)], [(632, 228), (792, 228)], [(633, 321), (794, 321)], [(626, 450), (795, 450)], [(626, 486), (792, 486)], [(689, 486), (689, 600)], [(727, 486), (727, 600)], [(53, 864), (113, 864)], [(51, 961), (113, 961)], [(195, 656), (195, 1036)], [(259, 658), (259, 1035)], [(145, 981), (342, 981)], [(385, 815), (565, 815)], [(488, 665), (488, 753)], [(576, 722), (790, 722)], [(630, 664), (630, 704)], [(722, 666), (722, 717)], [(577, 872), (789, 872)], [(577, 926), (789, 926)], [(626, 932), (626, 991), (719, 991), (719, 934)], [(1021, 112), (1021, 242)], [(937, 169), (937, 295)], [(1018, 269), (1171, 269)], [(1015, 307), (1015, 357)], [(914, 425), (984, 425)], [(911, 509), (978, 509)], [(985, 671), (1186, 671)], [(1187, 749), (1232, 749)], [(1184, 809), (1232, 809)], [(1185, 936), (1232, 936)], [(920, 699), (955, 699), (955, 1027), (920, 1027), (920, 699)], [(387, 1116), (790, 1116)], [(473, 1089), (473, 1170)], [(712, 1089), (712, 1170)], [(578, 1089), (578, 1170)]]}}
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
 # Keep radiator normal relief inside the dark traced recesses.
 for points,axis,positions,width in [([(1065,41),(1192,41),(1236,84),(1236,314),(1065,149)],'y',range(53,309,24),2), ([(1072,595),(1127,595),(1127,750),(1072,750)],'y',range(605,747,16),1.6), ([(1069,782),(1128,782),(1128,915),(1069,915)],'y',range(795,910,24),2.0), ([(488,1210),(778,1210),(778,1254),(488,1254)],'x',range(494,776,27),2.0)]:
  d=poly(points);mask=smooth(0,2,d);f=np.zeros_like(X)
  for position in positions:f=np.maximum(f,1-smooth(width,width+3,np.abs((X if axis=='x' else Y)-position)))
  f*=smooth(5,8,d);z=-.7*smooth(0,4,d)+1.1*f;h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,f)
 for cx,cy,r in reg['circles']:
  rr=np.hypot(X-cx,Y-cy);mask=1-smooth(r,r+2,rr);z=-1.2*(1-smooth(r-3,r,rr));h=h*(1-mask)+z*mask;structure=np.maximum(structure,mask)
 for path in reg['panels']:
  for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.3,capsule(a,b,1.6)))
 protected=np.maximum(flat,seal);pan*=1-np.maximum(protected,structure);h-=.6*pan;h*=1-protected
 im=bpy.data.images.load(str(M/f'basilisk_{atlas}_generated_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
 mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);paint=smooth(.12,.3,sat);metal=(1-paint)*smooth(.15,.48,lum)*.78;metal=metal*(1-structure)+(.08+.74*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.04*pan
 local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.53*metal+.05*wear,.49,.91);rough=rough*(1-structure)+(.9-.38*fins)*structure;rough=rough*(1-pan)+.87*pan;rough=rough*(1-flat)+.81*flat;rough=rough*(1-seal)+.83*seal;rough=rough*(1-glass)+.16*glass
 dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[seal>.05]=(0,0,1);records={}
 def save(a,key,colorspace='Non-Color'):
  b=np.ones((N,N,4),np.float32);b[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Basilisk '+atlas+' '+key,N,N,alpha=False,float_buffer=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(b[::-1]).ravel());im.scale(OUT,OUT)
  if key=='normal':
   nb=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(nb);na=nb.reshape(-1,4);nn=na[:,:3]*2-1;nn/=np.maximum(np.linalg.norm(nn,axis=-1,keepdims=True),1e-8);na[:,:3]=nn*.5+.5;im.pixels.foreach_set(na.ravel())
  p=M/f'basilisk_{atlas}_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
 maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
 for key,a in [('height',(h+8)/12),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
 mat=bpy.data.materials.new('Basilisk_Worn_'+atlas+'_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
assert max(a[2] for a in aspects)<6.4,sorted(aspects,key=lambda a:-a[2])[:10]
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for attempt in range(100):
  prior=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if not all(.07<t.x<.93 and .07<t.y<.93 and t.z>0 for t in q):cam.location=prior;break
scene=D/'basilisk_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.image_settings.color_depth='8';s.cycles.samples=24;s.render.resolution_x=1440;s.render.resolution_y=1080;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
report=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),active_uv=newuv,parts=2,stored_triangles=526,visible_triangles=sum(1 for o in obs for p in o.data.polygons if p.material_index!=1),original_geometry_normals_and_uv_layers_preserved=True,uv_repairs=repairs,max_visible_uv_anisotropy=max(a[2] for a in aspects),maps=allmaps,models=models,structural_height_only=True,emissives='deferred',runtime_visual_validation='pending_user_review',statistics=stats);(W/'validation.json').write_text(json.dumps(report,indent=2));print('BASILISK_PBR_COMPLETE',stats,flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
