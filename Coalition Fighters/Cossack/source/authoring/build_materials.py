from pathlib import Path
import os,json,hashlib
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['COSSACK_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'cossack_source_review.blend';original_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Cossack_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# Repair collapsed UVs under both cockpit pods, with a matched metric scale.
repairs=[]
for name,ids in [('Kossac_Co-pilot_pod',[44,45]),('Kossac_Pilot_Pod',[43,44])]:
 o=bpy.data.objects[name];uv=o.data.uv_layers[newuv];loops=[i for f in ids for i in o.data.polygons[f].loop_indices];pts=np.array([o.data.vertices[o.data.loops[i].vertex_index].co[:] for i in loops]);old=np.array([uv.data[i].uv[:] for i in loops]);_,_,axes=np.linalg.svd(pts-pts.mean(0),full_matrices=False);xy=(pts-pts.mean(0))@axes[:2].T
 if axes[0,2]<0:xy[:,0]*=-1
 px=np.column_stack((435+(xy[:,1]-xy[:,1].min())*.65,505+(xy[:,0]-xy[:,0].min())*.65));q=px/[N,-N]+[0,1]
 for i,v in zip(loops,q):uv.data[i].uv=v
 repairs.append({'part':o.name,'faces':ids,'method':'Metric planar cockpit underside strip, matched scale on both pods; grey metal sample','original_uv':old.tolist(),'uv':q.tolist()})
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def poly(points):
 p=np.array(points);inside=np.zeros((N,N),bool);d=np.full((N,N),1e6,np.float32)
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  d=np.minimum(d,-capsule(a,b,0));inside^=((a[1]>Y)!=(b[1]>Y))&(X<(b[0]-a[0])*(Y-a[1])/(b[1]-a[1]+1e-10)+a[0])
 return np.where(inside,d,-d)
regions={'glass': [[[521, 163], [613, 163], [615, 168], [615, 299], [611, 303], [521, 303], [518, 299], [518, 168]], [[522, 334], [611, 334], [615, 338], [615, 381], [611, 385], [522, 385], [518, 381], [518, 339]], [[656, 207], [777, 207], [783, 212], [783, 294], [774, 303], [656, 303], [651, 298], [651, 212]], [[658, 336], [727, 336], [731, 342], [698, 370], [657, 370], [652, 365], [652, 343]], [[1167, 359], [1201, 324], [1244, 324], [1248, 329], [1248, 351], [1220, 369], [1218, 407], [1223, 417], [1223, 435], [1186, 435], [1167, 417]]], 'vents': [[[96, 360], [287, 360], 13], [[852, 87], [942, 87], 12], [[564, 28], [564, 120], 7], [[777, 941], [777, 941], 18], [[942, 850], [942, 850], 20]], 'circles': [[115, 223, 39], [263, 223, 39], [200, 70, 11], [263, 70, 11], [328, 70, 11], [464, 154, 10], [464, 192, 10], [464, 246, 10], [464, 285, 10], [582, 554, 18], [582, 673, 18], [466, 943, 17], [466, 1009, 17], [466, 1083, 17], [466, 1152, 17], [466, 1217, 17]], 'flat': [[138, 444, 348, 638], [164, 835, 364, 1021], [41, 739, 374, 768], [1149, 47, 1252, 279], [21, 146, 55, 305], [333, 144, 363, 311], [826, 298, 886, 368], [176, 1164, 232, 1239], [871, 680, 994, 753], [389, 37, 426, 103], [1066, 72, 1113, 143], [886, 310, 936, 367], [451, 603, 507, 637], [1061, 449, 1219, 597], [382, 128, 498, 307], [132, 150, 176, 180], [211, 150, 254, 180], [210, 265, 253, 299], [133, 265, 177, 299]], 'panels': [[[170, 0], [170, 144]], [[352, 0], [352, 133]], [[51, 158], [339, 158], [339, 307], [51, 307], [51, 158]], [[629, 0], [629, 465]], [[710, 50], [710, 126]], [[813, 0], [813, 420]], [[946, 132], [946, 465]], [[635, 191], [947, 191]], [[635, 420], [947, 420]], [[994, 0], [994, 460]], [[996, 237], [1143, 237]], [[996, 375], [1143, 375]], [[1034, 430], [1254, 430]], [[1148, 284], [1254, 284]], [[8, 473], [48, 443], [341, 443], [409, 484], [409, 706], [374, 739], [53, 739], [8, 706], [8, 473]], [[12, 649], [353, 649]], [[414, 472], [530, 472]], [[414, 474], [414, 733]], [[424, 755], [646, 755]], [[668, 468], [903, 468]], [[901, 470], [901, 646]], [[668, 650], [852, 650]], [[714, 659], [714, 752]], [[918, 649], [1029, 649]], [[1030, 447], [1030, 790]], [[1080, 693], [1203, 693]], [[1205, 640], [1205, 787]], [[51, 769], [374, 769]], [[7, 833], [7, 1156]], [[143, 856], [143, 1150]], [[50, 865], [50, 1151]], [[7, 938], [144, 938]], [[144, 1030], [381, 1030]], [[7, 1152], [241, 1152]], [[378, 835], [378, 1254]], [[421, 911], [421, 1254]], [[522, 768], [522, 1254]], [[606, 769], [606, 928]], [[638, 802], [638, 1229]], [[650, 822], [650, 1254]], [[529, 931], [632, 931]], [[529, 1174], [632, 1174]], [[659, 1168], [900, 1168]], [[890, 804], [998, 804]], [[1005, 804], [1005, 1254]], [[1058, 830], [1058, 1254]], [[1065, 939], [1249, 939]], [[1065, 1151], [1249, 1151]], [[1139, 832], [1139, 933]], [[1250, 833], [1250, 1249]]]}
(W/'regions.json').write_text(json.dumps({'coordinate_resolution':N,'regions':regions,'normal_source':'Traced physical seams, bounded radiator recesses and inset glazing only; no albedo-noise bump'},indent=2)+'\n')
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
signed=np.maximum.reduce([poly(p) for p in regions['glass']]);glass=smooth(0,2,signed);seal=smooth(-7,-2,signed)
for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,2,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['vents']:
 d=capsule(a,b,r);mask=smooth(0,2,d);h-=.9*smooth(0,5,d);structure=np.maximum(structure,mask)
# Structural radiator ribs remain inside their painted housings.
for rect,axis,centres in [([672,473,897,510],'x',range(680,896,20)),([921,502,1009,623],'x',range(932,1005,19)),([889,932,998,1244],'x',range(899,993,18)),([699,849,725,1000],'x',[705,717]),([817,849,843,1000],'x',[823,836]),([547,958,600,1139],'x',range(552,600,9)),([76,477,132,638],'x',[89,108,125]),([250,1085,282,1222],'x',[258,271]),([318,1085,349,1222],'x',[326,339]),([1134,961,1198,1069],'x',range(1140,1195,12)),([1050,47,1111,64],'y',[51,59]),([1050,168,1111,188],'y',[174,182])]:
 a,b,c,d=rect;dist=poly([[a,b],[c,b],[c,d],[a,d]]);mask=smooth(0,2,dist);pos=X if axis=='x' else Y;rib=np.maximum.reduce([1-smooth(1.5,3,np.abs(pos-v)) for v in centres])*smooth(3,6,dist)
 h=h*(1-mask)+(-.9*smooth(0,4,dist)+.8*rib)*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,rib)
for cx,cy,r in regions['circles']:
 d=r-np.hypot(X-cx,Y-cy);mask=smooth(0,2,d);h=h*(1-mask)-.8*smooth(0,4,d)*mask;structure=np.maximum(structure,mask)
for path in regions['panels']:
 for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.3,capsule(a,b,2.0)))
pan*=1-np.maximum.reduce([flat,seal,structure]);h-=.32*pan;h*=1-np.maximum(flat,seal)
# No raised rim: zero-height frame slopes down into a flat recessed pane.
window_h=-1.7*smooth(-6,1,signed)
for axis in (0,1):window_h=(np.roll(window_h,2,axis)+4*np.roll(window_h,1,axis)+6*window_h+4*np.roll(window_h,-1,axis)+np.roll(window_h,-2,axis))/16
window_h[signed>3]=-1.7;window_h[signed<-9]=0;h+=window_h
im=bpy.data.images.load(str(M/'cossack_hull_glazing_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.15,.48,lum)*.72;metal=metal*(1-structure)+(.08+.62*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.03,.18,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.54*metal+.04*wear,.52,.89);rough=rough*(1-structure)+(.89-.3*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.15*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[signed>3]=[0,0,1]
records={}
def save(a,key,colorspace='Non-Color'):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Cossack '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);n=b.reshape(-1,4);v=n[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);n[:,:3]=v*.5+.5;im.pixels.foreach_set(n.ravel())
 p=M/f'cossack_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':sha(p),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
mat=bpy.data.materials.new('Cossack_Worn_Hull_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
for key,im in maps.items():
 im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT';links.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
models={};aspects=[]
for o in obs:
 m=o.data;m.materials[0]=mat;b=before[o.name];assert b[0]==[list(v.co) for v in m.vertices] and b[1]==[list(p.vertices) for p in m.polygons] and b[2]==[list(n.vector) for n in m.corner_normals]
 for name,values in b[3].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 models[o.name]={'part_index':o['native_part_index'],'vertices':[list(v.co) for v in m.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':o['native_material_indices'][p.index],'hidden':p.material_index==1} for p in m.polygons]}
 for p in m.polygons:
  if p.material_index==1:continue
  pts=np.array([m.vertices[i].co[:] for i in p.vertices]);e=pts[1:]-pts[0];n=np.cross(*e);area=np.linalg.norm(n)
  if area<1e-7:continue
  n/=area;t=e[0]/np.linalg.norm(e[0]);xy=e@np.stack((t,np.cross(n,t)),axis=1);q=np.array([m.uv_layers[newuv].data[i].uv[:] for i in p.loop_indices]);sing=np.linalg.svd(np.linalg.solve(xy,q[1:]-q[0]),compute_uv=False);aspects.append((o.name,p.index,float(sing[0]/max(sing[1],1e-12))))
assert max(a[2] for a in aspects)<10,sorted(aspects,key=lambda a:-a[2])[:10]
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for _ in range(100):
  prior=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if not all(.08<t.x<.92 and .08<t.y<.92 and t.z>0 for t in q):cam.location=prior;break
scene=D/'cossack_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_sha
report={'source':str(src),'source_sha256':original_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':4,'stored_triangles':808,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repairs,'max_visible_uv_anisotropy':max(a[2] for a in aspects),'maps':{'hull':records},'models':models,'structural_height_only':True,'window_recess':{'depth':1.7,'bevel_width_master_pixels':7,'glass_interiors_flat':True,'no_raised_rim':True},'emissives':'deferred','runtime_visual_validation':'pending_user_review'}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('COSSACK_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
