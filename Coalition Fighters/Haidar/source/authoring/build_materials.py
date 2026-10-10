from pathlib import Path
import os,json,hashlib
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'haidar_source_review.blend';original_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Haidar_Delivery_UV_v1'
for o in obs:
 u=o.data.uv_layers.new(name=newuv,do_init=True);o.data.uv_layers.active=u;u.active_render=True
# The native visible UVs are non-degenerate; retain all coordinates.
repairs=[]
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
regions={'glass': [[[17, 523], [81, 512], [81, 578], [17, 568]], [[87, 513], [97, 511], [97, 580], [87, 578]], [[104, 511], [116, 509], [116, 581], [104, 581]], [[123, 507], [169, 501], [179, 508], [179, 580], [170, 589], [124, 583]], [[428, 738], [486, 731], [486, 767], [428, 767]], [[495, 731], [550, 731], [550, 768], [495, 768]], [[560, 734], [611, 742], [612, 768], [560, 768]], [[634, 752], [713, 771], [713, 778], [634, 772]], [[975, 935], [1046, 963], [1046, 993], [975, 993]], [[976, 1003], [1048, 1003], [1048, 1068], [976, 1102]], [[976, 1142], [1047, 1113], [1047, 1239], [1034, 1238], [975, 1207]]], 'vents': [[[184, 254], [432, 254], 11], [[185, 297], [397, 297], 10], [[639, 294], [798, 294], 10], [[647, 453], [647, 594], 11], [[692, 453], [692, 594], 11], [[737, 453], [737, 594], 11], [[840, 200], [1071, 200], 9]], 'circles': [[488, 468, 24], [488, 520, 23], [873, 63, 11], [873, 102, 11], [1192, 965, 21], [1139, 1016, 28], [720, 1131, 68], [377, 1214, 17], [439, 1214, 17], [265, 887, 37], [264, 1007, 36], [264, 1128, 36]], 'flat': [[112, 343, 320, 433], [48, 670, 96, 699], [592, 466, 619, 506], [836, 441, 889, 472], [252, 697, 294, 749], [1139, 710, 1179, 767], [14, 828, 127, 1208], [346, 1120, 414, 1150], [114, 57, 399, 173], [838, 898, 946, 1150]], 'panels': [[[80, 0], [81, 498]], [[140, 0], [142, 58]], [[304, 0], [305, 67]], [[397, 173], [471, 173], [471, 4]], [[474, 24], [558, 24]], [[585, 0], [585, 423]], [[0, 249], [81, 249]], [[0, 359], [80, 359]], [[206, 329], [206, 608]], [[329, 329], [329, 608]], [[79, 439], [553, 439]], [[347, 587], [473, 587], [473, 710]], [[346, 613], [346, 790]], [[348, 793], [613, 793]], [[347, 902], [472, 902]], [[346, 1147], [472, 1147]], [[348, 1234], [475, 1234]], [[471, 798], [471, 1253]], [[80, 644], [80, 665]], [[0, 757], [226, 757], [280, 807], [345, 807]], [[154, 758], [154, 831]], [[144, 832], [144, 1233]], [[205, 808], [205, 1233]], [[0, 913], [20, 913]], [[115, 913], [144, 913]], [[287, 927], [324, 927]], [[325, 807], [325, 1233]], [[80, 583], [80, 607]], [[29, 658], [99, 658]], [[224, 634], [272, 634], [272, 688]], [[346, 710], [417, 639], [417, 617]], [[486, 588], [568, 588], [568, 643], [530, 677], [486, 677]], [[619, 0], [619, 255]], [[622, 85], [756, 85]], [[688, 86], [688, 250]], [[768, 0], [768, 253]], [[818, 0], [818, 183]], [[914, 0], [914, 177], [1092, 177]], [[919, 103], [957, 103]], [[998, 103], [1044, 103]], [[1092, 3], [1092, 164]], [[1118, 0], [1118, 174], [1253, 174]], [[1130, 86], [1199, 86], [1199, 3]], [[1199, 89], [1199, 172]], [[978, 219], [978, 294], [1199, 294]], [[1200, 223], [1253, 223]], [[1077, 224], [1077, 321]], [[829, 254], [829, 320]], [[829, 596], [949, 596]], [[840, 658], [911, 658]], [[908, 531], [908, 628], [857, 679], [838, 679]], [[798, 793], [798, 879], [823, 891], [1073, 891]], [[894, 840], [894, 888]], [[955, 725], [955, 815]], [[1013, 578], [1013, 716]], [[1087, 612], [1151, 612]], [[1076, 718], [1128, 718]], [[1116, 817], [1187, 817]], [[1199, 808], [1199, 933]], [[953, 926], [953, 1253]], [[842, 1171], [951, 1171]], [[589, 929], [837, 929]], [[622, 1011], [622, 1253]], [[125, 614], [272, 614]], [[824, 124], [824, 244]]]}
(W/'regions.json').write_text(json.dumps({'coordinate_resolution':N,'regions':regions,'normal_source':'Traced physical seams, bounded radiator recesses and inset glazing only; no albedo-noise bump'},indent=2)+'\n')
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
signed=np.maximum.reduce([poly(p) for p in regions['glass']]);glass=smooth(0,2,signed);seal=smooth(-7,-2,signed)
for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,2,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['vents']:
 d=capsule(a,b,r);mask=smooth(0,2,d);h-=.9*smooth(0,5,d);structure=np.maximum(structure,mask)
# Recess and ribs are bounded by their actual atlas housings.
for points,axis,centres in [([[641, 22], [731, 22], [744, 35], [735, 52], [641, 52], [632, 41]], 'y', [30, 40, 49]), ([[130, 638], [204, 638], [207, 718], [129, 720]], 'y', [672, 686]), ([[665, 823], [725, 823], [726, 873], [665, 873]], 'y', [838, 854]), ([[401, 1070], [448, 1070], [454, 1108], [402, 1108]], 'y', [1081, 1094]), ([[1091, 1084], [1113, 1070], [1176, 1075], [1191, 1096], [1220, 1207], [1202, 1216], [1092, 1143]], 'y', [1091, 1111, 1131, 1151, 1171, 1191]), ([[499, 799], [529, 799], [529, 870], [499, 870]], 'y', [803, 808, 813, 818, 823, 828, 833, 838, 843, 848, 853, 858, 863]), ([[643, 940], [658, 940], [658, 995], [643, 995]], 'x', [650]), ([[677, 940], [693, 940], [693, 995], [677, 995]], 'x', [685]), ([[713, 940], [728, 940], [728, 995], [713, 995]], 'x', [720]), ([[748, 940], [763, 940], [763, 995], [748, 995]], 'x', [756]), ([[783, 940], [797, 940], [797, 995], [783, 995]], 'x', [790]), ([[819, 940], [831, 940], [831, 995], [819, 995]], 'x', [825])]:
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
im=bpy.data.images.load(str(M/'haidar_hull_glazing_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.15,.48,lum)*.65;metal=metal*(1-structure)+(.08+.62*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.03,.18,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.54*metal+.04*wear,.52,.89);rough=rough*(1-structure)+(.89-.3*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.15*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[signed>3]=[0,0,1]
records={}
def save(a,key,colorspace='Non-Color'):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Haidar '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);n=b.reshape(-1,4);v=n[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);n[:,:3]=v*.5+.5;im.pixels.foreach_set(n.ravel())
 p=M/f'haidar_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':sha(p),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
mat=bpy.data.materials.new('Haidar_Worn_Hull_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
scene=D/'haidar_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_sha
report={'source':str(src),'source_sha256':original_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':6,'stored_triangles':478,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repairs,'max_visible_uv_anisotropy':max(a[2] for a in aspects),'maps':{'hull':records},'models':models,'structural_height_only':True,'window_recess':{'depth':1.7,'bevel_width_master_pixels':7,'glass_interiors_flat':True,'no_raised_rim':True},'emissives':'deferred','runtime_visual_validation':'pending_user_review'}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('HAIDAR_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
