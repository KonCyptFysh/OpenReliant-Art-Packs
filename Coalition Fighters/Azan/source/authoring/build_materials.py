from pathlib import Path
import os,json,hashlib
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['AZAN_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'azan_source_review.blend';original_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Azan_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# Four inner tail-edge triangles have placeholder/collapsed UV coordinates.
# A metric planar map uses a clear strip of existing grey metal on each side.
o=bpy.data.objects['Houjian_Tail'];uv=o.data.uv_layers[newuv];repairs=[]
for ids in [[36,37],[38,39]]:
 loops=[i for f in ids for i in o.data.polygons[f].loop_indices];pts=np.array([o.data.vertices[o.data.loops[i].vertex_index].co[:] for i in loops]);old=np.array([uv.data[i].uv[:] for i in loops]);_,_,axes=np.linalg.svd(pts-pts.mean(0),full_matrices=False);xy=(pts-pts.mean(0))@axes[:2].T
 if axes[0,2]<0:xy[:,0]*=-1
 if axes[1,1]<0:xy[:,1]*=-1
 px=np.column_stack((396+(xy[:,1]-xy[:,1].min())*.7,1000+(xy[:,0]-xy[:,0].min())*.7));q=px/[N,-N]+[0,1]
 for i,v in zip(loops,q):uv.data[i].uv=v
 repairs.append({'part':o.name,'faces':ids,'method':'Metric planar inner tail edge, sampled from plain grey metal; both sides use the same scale','original_uv':old.tolist(),'uv':q.tolist()})
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
regions={
 'glass':[[[38,526],[65,505],[93,506],[106,521],[82,553],[52,566],[39,552]],[[78,583],[121,548],[174,519],[249,519],[265,529],[250,541],[104,609],[82,618],[77,613]],[[540,477],[554,463],[796,464],[809,475],[809,524],[798,534],[568,534],[541,504]],[[839,476],[850,465],[889,466],[901,476],[901,524],[889,534],[850,534],[839,522]]],
 'vents':[[[391,39],[485,39],16],[[219,167],[392,167],18],[[686,359],[745,359],12],[[1019,94],[1150,94],15],[[1016,234],[1137,234],15],[[79,725],[295,725],18],[[929,650],[1042,650],15],[[931,704],[1050,704],15],[[1092,704],[1092,779],11],[[1240,705],[1240,780],10],[[817,1037],[967,1037],13],[[1144,1096],[1144,1193],11],[[1184,1094],[1184,1193],11]],
 'circles':[[89,134,29],[87,214,29],[232,71,24],[299,71,24],[231,291,12],[231,341,12],[506,161,13],[506,216,13],[506,266,13],[616,125,13],[705,112,13],[630,190,12],[689,190,12],[703,679,12],[750,679,12],[804,679,12],[280,434,13],[882,1156,12],[940,1156,12],[996,1156,12],[1162,936,15],[1159,996,15]],
 'flat':[[727,1090,845,1202],[212,190,411,224],[797,969,981,1001],[35,429,97,460],[1131,726,1185,761],[196,30,217,53],[253,31,281,58],[313,31,337,56],[1190,73,1220,124],[1190,203,1220,251],[631,365,780,386],[198,489,244,505],[392,407,435,428],[28,848,80,903],[326,847,366,898]],
 'panels':[[[170,0],[170,52],[0,52]],[[942,0],[942,327]],[[1141,0],[1141,51]],[[184,26],[343,26],[343,115],[183,115],[183,26]],[[13,55],[157,55],[157,382],[14,382],[13,55]],[[445,142],[461,124],[548,124],[566,142],[566,392],[550,412],[462,412],[443,394],[443,142]],[[444,343],[565,343]],[[590,263],[613,239],[789,239],[818,259],[818,291],[790,316],[609,316],[590,299],[590,263]],[[590,393],[801,393],[801,432],[590,432],[590,393]],[[361,566],[361,620],[493,620],[493,676],[359,676],[359,776]],[[290,556],[290,662],[359,662]],[[498,643],[642,643],[642,723]],[[139,791],[139,880],[293,880]],[[138,937],[138,1223],[106,1223],[90,1207],[90,963],[118,937],[138,937]],[[378,838],[378,963],[426,963]],[[381,989],[381,1182],[463,1182]],[[669,658],[688,645],[810,645],[830,661],[830,706],[684,706],[669,690],[669,658]],[[716,950],[988,950]],[[772,951],[772,1078]],[[713,961],[713,1240]],[[844,1103],[1015,1103]],[[850,1141],[1028,1141]],[[1052,797],[1052,1237]],[[1110,904],[1121,891],[1201,891],[1212,905],[1212,1028],[1200,1044],[1121,1044],[1110,1030],[1110,904]]]
}
(W/'regions.json').write_text(json.dumps({'coordinate_resolution':N,'regions':regions,'normal_source':'Traced physical seams, bounded radiator recesses and inset glazing only; no albedo-noise bump'},indent=2)+'\n')
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
signed=np.maximum.reduce([poly(p) for p in regions['glass']]);glass=smooth(0,2,signed);seal=smooth(-7,-2,signed)
for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,2,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['vents']:
 d=capsule(a,b,r);mask=smooth(0,2,d);h-=1.3*smooth(0,5,d);structure=np.maximum(structure,mask)
# Trace only existing radiator rib interiors; all relief is clipped before the painted frames.
for points,ys in [([[464,945],[600,945],[600,1210],[464,1210]],range(956,1207,20)),([[377,449],[440,449],[451,468],[451,518],[435,539],[379,539],[367,523],[367,468]],range(457,531,14))]:
 d=poly(points);mask=smooth(0,2,d);rib=np.maximum.reduce([1-smooth(2,4,np.abs(Y-y)) for y in ys])*smooth(4,8,d);h=h*(1-mask)+(-1.25*smooth(0,5,d)+1.35*rib)*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,rib)
for cx,cy,r in regions['circles']:
 d=r-np.hypot(X-cx,Y-cy);mask=smooth(0,2,d);h=h*(1-mask)-.8*smooth(0,4,d)*mask;structure=np.maximum(structure,mask)
for path in regions['panels']:
 for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.3,capsule(a,b,2.0)))
pan*=1-np.maximum.reduce([flat,seal,structure]);h-=.4*pan;h*=1-np.maximum(flat,seal)
# No raised rim: zero-height frame slopes down into a flat recessed pane.
window_h=-1.7*smooth(-6,1,signed)
for axis in (0,1):window_h=(np.roll(window_h,2,axis)+4*np.roll(window_h,1,axis)+6*window_h+4*np.roll(window_h,-1,axis)+np.roll(window_h,-2,axis))/16
window_h[signed>3]=-1.7;window_h[signed<-9]=0;h+=window_h
im=bpy.data.images.load(str(M/'azan_hull_glazing_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.15,.48,lum)*.72;metal=metal*(1-structure)+(.08+.62*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.03,.18,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.54*metal+.04*wear,.52,.89);rough=rough*(1-structure)+(.89-.3*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.15*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[signed>3]=[0,0,1]
records={}
def save(a,key,colorspace='Non-Color'):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Azan '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);n=b.reshape(-1,4);v=n[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);n[:,:3]=v*.5+.5;im.pixels.foreach_set(n.ravel())
 p=M/f'azan_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':sha(p),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
mat=bpy.data.materials.new('Azan_Worn_Hull_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
assert max(a[2] for a in aspects)<8,sorted(aspects,key=lambda a:-a[2])[:10]
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for _ in range(100):
  prior=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if not all(.08<t.x<.92 and .08<t.y<.92 and t.z>0 for t in q):cam.location=prior;break
scene=D/'azan_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_sha
report={'source':str(src),'source_sha256':original_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':2,'stored_triangles':528,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repairs,'max_visible_uv_anisotropy':max(a[2] for a in aspects),'maps':{'hull':records},'models':models,'structural_height_only':True,'window_recess':{'depth':1.7,'bevel_width_master_pixels':7,'glass_interiors_flat':True,'no_raised_rim':True},'emissives':'deferred','runtime_visual_validation':'pending_user_review'}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('AZAN_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
