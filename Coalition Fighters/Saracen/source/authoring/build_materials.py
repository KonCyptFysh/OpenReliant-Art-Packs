from pathlib import Path
import os,json,hashlib
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['SARACEN_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'saracen_source_review.blend';original_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Saracen_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# The native visible UVs are non-degenerate; retain all coordinates.
repairs=[]
# Two native wing-edge triangles have coincident UV corners. Remap their paired
# quads to the same unmarked alloy strip, keeping the original UV layers intact.
o=bpy.data.objects['Saracen'];m=o.data;uv=m.uv_layers[newuv]
for ids in [(66,73),(78,83)]:
 verts={i for fi in ids for i in m.polygons[fi].vertices}
 xs=[abs(m.vertices[i].co.x-17.834373474121094) for i in verts]
 ys=[m.vertices[i].co.y for i in verts];lo_x,hi_x=min(xs),max(xs);lo_y,hi_y=min(ys),max(ys)
 for fi in ids:
  for li in m.polygons[fi].loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co
   px=910+24*(v.y-lo_y)/(hi_y-lo_y);py=425+110*(abs(v.x-17.834373474121094)-lo_x)/(hi_x-lo_x)
   uv.data[li].uv=(px/1254,1-py/1254)
 repairs.append({'part':'Saracen','faces':list(ids),'reason':'Collapsed native UV triangle on front wing edge; paired coplanar triangles projected continuously to plain alloy strip','atlas_rectangle_master_pixels':[910,425,934,535]})

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
regions={'glass': [[[53, 20], [221, 20], [230, 28], [230, 35], [222, 42], [53, 42], [45, 35], [45, 28]], [[52, 67], [222, 67], [230, 74], [230, 82], [222, 88], [53, 88], [45, 81], [45, 74]], [[282, 23], [409, 23], [428, 41], [428, 80], [420, 88], [282, 88], [274, 80], [274, 31]], [[977, 49], [998, 41], [1030, 41], [1033, 47], [1033, 59], [1027, 65], [978, 65], [973, 60], [973, 52]], [[1082, 22], [1189, 22], [1201, 36], [1201, 49], [1187, 63], [1082, 63], [1074, 56], [1074, 30]]], 'vents': [[[679, 215], [840, 215], 10], [[710, 857], [831, 857], 8], [[710, 935], [831, 935], 8], [[1090, 156], [1090, 262], 9], [[1169, 156], [1169, 262], 9], [[1075, 726], [1075, 753], 6], [[1141, 726], [1141, 753], 6], [[416, 506], [492, 506], 7], [[195, 347], [220, 347], 5], [[789, 1047], [820, 1047], 5]], 'circles': [[427, 343, 37], [507, 343, 35], [984, 240, 32], [984, 377, 32], [433, 673, 14], [487, 673, 14]], 'flat': [[10, 127, 178, 169], [25, 219, 75, 310], [183, 137, 225, 160], [200, 121, 230, 168], [609, 36, 669, 78], [684, 37, 745, 79], [389, 195, 470, 244], [174, 315, 249, 383], [293, 313, 332, 381], [540, 311, 845, 378], [44, 369, 66, 500], [191, 449, 307, 558], [529, 473, 702, 531], [38, 550, 78, 583], [678, 769, 716, 800], [594, 822, 625, 984], [969, 579, 985, 810], [1058, 604, 1096, 674], [1104, 275, 1159, 312], [943, 289, 1022, 322], [292, 1028, 330, 1159], [535, 993, 578, 1058], [675, 1001, 717, 1030], [1040, 1032, 1225, 1060]], 'panels': [[[24, 108], [352, 108], [352, 276]], [[249, 0], [249, 107]], [[255, 0], [255, 107]], [[472, 0], [472, 108], [488, 108], [488, 271]], [[503, 107], [503, 275]], [[631, 92], [631, 271]], [[627, 98], [626, 119]], [[627, 161], [627, 275]], [[883, 162], [883, 271]], [[470, 53], [512, 12], [749, 12], [766, 42], [821, 42], [856, 10], [856, 0]], [[894, 0], [894, 111], [931, 111], [931, 211]], [[1053, 0], [1053, 91], [1028, 116], [931, 116]], [[1225, 0], [1225, 92], [1244, 92]], [[1059, 319], [1205, 319], [1245, 344]], [[1053, 121], [1053, 556], [897, 556]], [[4, 196], [78, 196], [95, 215], [95, 312], [77, 332], [24, 332], [7, 316]], [[5, 357], [23, 339], [76, 339], [94, 360], [94, 508], [74, 527], [25, 527], [6, 509]], [[137, 295], [286, 295]], [[363, 279], [910, 279], [929, 299], [929, 391], [897, 421]], [[370, 294], [370, 395], [551, 395], [551, 281]], [[130, 417], [855, 417], [875, 437], [875, 569], [854, 591], [134, 591]], [[169, 419], [169, 592]], [[333, 423], [333, 586]], [[464, 419], [464, 444]], [[99, 538], [2, 538]], [[16, 596], [161, 596], [161, 616], [0, 616]], [[214, 591], [214, 710], [5, 710]], [[214, 674], [327, 674]], [[327, 591], [327, 783], [212, 783], [212, 734]], [[555, 593], [555, 714], [792, 714], [839, 768], [894, 768]], [[554, 724], [554, 815]], [[347, 731], [386, 773], [386, 821], [495, 821]], [[346, 599], [346, 731]], [[588, 733], [607, 716], [782, 716], [833, 781], [892, 781]], [[584, 817], [1019, 817]], [[668, 820], [668, 985]], [[867, 819], [867, 986]], [[1042, 580], [1042, 810]], [[14, 734], [67, 734], [67, 939], [137, 1024], [137, 1120], [118, 1148], [0, 1148]], [[126, 783], [345, 783], [383, 822], [383, 970], [345, 1008], [207, 1008], [118, 918], [118, 824], [126, 783]], [[69, 828], [115, 828]], [[68, 939], [0, 939]], [[19, 971], [103, 971]], [[227, 1013], [227, 1164], [207, 1180], [14, 1180]], [[340, 1014], [340, 1234], [285, 1234], [234, 1186]], [[345, 975], [457, 975]], [[526, 993], [526, 1165], [606, 1241], [814, 1241], [834, 1221], [834, 1085], [884, 1031], [946, 1031]], [[522, 1131], [441, 1131]], [[1041, 1065], [1041, 1192], [1254, 1192]], [[1100, 876], [1100, 819]], [[581, 1080], [760, 1080]], [[603, 1231], [787, 1231]], [[798, 1087], [798, 1217]], [[891, 1134], [991, 1134], [1017, 1108]], [[891, 1191], [980, 1191], [980, 1254]]]}
(W/'regions.json').write_text(json.dumps({'coordinate_resolution':N,'regions':regions,'normal_source':'Traced physical seams, bounded radiator recesses and inset glazing only; no albedo-noise bump'},indent=2)+'\n')
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
signed=np.maximum.reduce([poly(p) for p in regions['glass']]);glass=smooth(0,2,signed);seal=smooth(-7,-2,signed)
for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,2,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['vents']:
 d=capsule(a,b,r);mask=smooth(0,2,d);h-=.9*smooth(0,5,d);structure=np.maximum(structure,mask)
# Recess and ribs are bounded by their actual atlas housings.
for points,axis,centres in [([[142, 283], [142, 241], [169, 213], [270, 213], [291, 238], [291, 283]], 'x', [161, 182, 203, 224, 245, 266, 285]), ([[597, 658], [788, 658], [799, 669], [788, 687], [595, 687]], 'y', [667, 678]), ([[159, 839], [339, 839], [350, 850], [350, 866], [161, 866]], 'y', [847, 859]), ([[210, 909], [341, 909], [350, 919], [350, 935], [208, 935]], 'y', [918, 930]), ([[1046, 1029], [1046, 929], [1082, 888], [1224, 888], [1224, 1029]], 'x', [1051, 1070, 1089, 1108, 1127, 1146, 1165, 1184, 1203, 1220]), ([[656, 1110], [713, 1110], [735, 1135], [735, 1173], [715, 1198], [657, 1198], [632, 1174], [632, 1136]], 'y', [1118, 1128, 1138, 1148, 1158, 1168, 1178, 1188])]:
 dist=poly(points);mask=smooth(0,2,dist);pos=X if axis=='x' else Y;rib=np.maximum.reduce([1-smooth(1.2,2.5,np.abs(pos-v)) for v in centres])*smooth(3,6,dist)
 h=h*(1-mask)+(-.9*smooth(0,4,dist)+.75*rib)*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,rib)
for cx,cy,r in regions['circles']:
 d=r-np.hypot(X-cx,Y-cy);mask=smooth(0,2,d);h=h*(1-mask)-.8*smooth(0,4,d)*mask;structure=np.maximum(structure,mask)
for path in regions['panels']:
 for a,b in zip(path,path[1:]):pan=np.maximum(pan,smooth(0,1.3,capsule(a,b,2.0)))
pan*=1-np.maximum.reduce([flat,seal,structure]);h-=.32*pan;h*=1-np.maximum(flat,seal)
# No raised rim: zero-height frame slopes down into a flat recessed pane.
window_h=-1.7*smooth(-6,1,signed)
for axis in (0,1):window_h=(np.roll(window_h,2,axis)+4*np.roll(window_h,1,axis)+6*window_h+4*np.roll(window_h,-1,axis)+np.roll(window_h,-2,axis))/16
window_h[signed>3]=-1.7;window_h[signed<-9]=0;h+=window_h
im=bpy.data.images.load(str(M/'saracen_hull_glazing_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.15,.48,lum)*.65;metal=metal*(1-structure)+(.08+.62*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.03,.18,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.54*metal+.04*wear,.52,.89);rough=rough*(1-structure)+(.89-.3*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.15*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[signed>3]=[0,0,1]
records={}
def save(a,key,colorspace='Non-Color'):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Saracen '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);n=b.reshape(-1,4);v=n[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);n[:,:3]=v*.5+.5;im.pixels.foreach_set(n.ravel())
 p=M/f'saracen_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':sha(p),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
mat=bpy.data.materials.new('Saracen_Worn_Hull_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
scene=D/'saracen_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_sha
report={'source':str(src),'source_sha256':original_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':2,'stored_triangles':616,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repairs,'max_visible_uv_anisotropy':max(a[2] for a in aspects),'maps':{'hull':records},'models':models,'structural_height_only':True,'window_recess':{'depth':1.7,'bevel_width_master_pixels':7,'glass_interiors_flat':True,'no_raised_rim':True},'emissives':'deferred','runtime_visual_validation':'pending_user_review'}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('SARACEN_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
