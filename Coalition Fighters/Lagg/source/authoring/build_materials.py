from pathlib import Path
import os,json,hashlib
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['LAGG_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'lagg_source_review.blend';original_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Lagg_Delivery_UV_v1'
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
regions={'glass': [[[23, 144], [51, 144], [57, 151], [57, 315], [51, 323], [23, 323], [17, 315], [17, 153]], [[111, 149], [130, 158], [132, 317], [124, 323], [108, 323], [98, 315], [98, 158]], [[23, 362], [50, 362], [56, 369], [56, 449], [48, 457], [23, 457], [17, 449], [17, 372]], [[127, 362], [136, 371], [136, 399], [129, 402], [120, 383], [120, 371]], [[20, 790], [55, 758], [59, 759], [59, 797], [52, 803], [20, 803]], [[103, 779], [130, 779], [135, 785], [135, 813], [130, 818], [101, 818], [96, 812], [96, 786]]], 'vents': [[[113, 591], [113, 697], 9], [[268, 399], [268, 554], 8], [[651, 261], [651, 351], 8], [[582, 517], [582, 740], 11], [[724, 517], [724, 741], 11], [[68, 916], [68, 1085], 10], [[138, 916], [138, 1085], 10], [[909, 1008], [1067, 1008], 11], [[1059, 119], [1059, 156], 6], [[1130, 119], [1130, 156], 6], [[1197, 119], [1197, 156], 6]], 'circles': [[549, 132, 22], [549, 229, 22], [749, 132, 22], [749, 229, 22], [372, 229, 14], [372, 306, 14], [372, 382, 14], [536, 1021, 23], [898, 622, 25], [898, 727, 26], [882, 795, 16], [878, 841, 16], [786, 1203, 12], [843, 1203, 12], [1065, 800, 25], [1156, 800, 25]], 'flat': [[0, 40, 81, 116], [100, 35, 153, 132], [808, 48, 1004, 279], [695, 154, 816, 273], [496, 150, 605, 274], [183, 200, 292, 295], [429, 276, 472, 333], [603, 334, 700, 374], [514, 325, 581, 430], [720, 333, 772, 427], [1187, 393, 1240, 529], [323, 440, 369, 552], [1046, 217, 1238, 268], [1051, 302, 1117, 389], [1017, 592, 1076, 682], [785, 295, 1254, 618], [31, 410, 132, 479], [28, 518, 65, 691], [387, 605, 521, 665], [389, 702, 519, 792], [513, 867, 751, 934], [773, 835, 817, 884], [737, 1082, 982, 1136], [979, 1083, 1111, 1136], [898, 1176, 975, 1234], [399, 880, 466, 950], [390, 821, 484, 871], [1144, 1099, 1230, 1160], [342, 899, 386, 1238], [814, 930, 930, 1064], [469, 1101, 716, 1244]], 'panels': [[[0, 25], [159, 25]], [[167, 23], [169, 325]], [[305, 27], [305, 324]], [[0, 342], [167, 342]], [[155, 25], [156, 837]], [[173, 196], [302, 196]], [[295, 342], [317, 364], [317, 607], [211, 607], [192, 582], [192, 397], [226, 347], [295, 342]], [[423, 9], [424, 77], [474, 77], [514, 42], [514, 11], [423, 9]], [[478, 115], [478, 284]], [[481, 293], [603, 293]], [[432, 557], [531, 557], [531, 474]], [[323, 561], [535, 561]], [[514, 614], [521, 618], [522, 663], [385, 663]], [[540, 474], [609, 474]], [[541, 809], [559, 838], [607, 838], [621, 823]], [[685, 472], [752, 472]], [[689, 837], [754, 837], [769, 817]], [[626, 0], [626, 163], [640, 177], [659, 177], [675, 162], [675, 0]], [[625, 793], [625, 829]], [[673, 793], [673, 829]], [[692, 293], [811, 293]], [[814, 54], [814, 294]], [[814, 204], [1242, 204]], [[1012, 0], [1012, 89], [1248, 89]], [[1035, 205], [1035, 398]], [[1062, 409], [1160, 409], [1160, 521]], [[770, 453], [861, 453]], [[989, 455], [989, 703], [1210, 703]], [[1009, 617], [1009, 886], [1210, 886], [1210, 614]], [[773, 709], [836, 709]], [[841, 869], [974, 869]], [[776, 889], [1022, 889]], [[1, 850], [157, 850]], [[200, 912], [200, 1139]], [[232, 991], [328, 991]], [[201, 1232], [347, 1232]], [[18, 1145], [18, 1231], [101, 1231], [18, 1145]], [[18, 990], [60, 990]], [[150, 990], [190, 990]], [[14, 929], [14, 1107]], [[240, 852], [308, 922], [308, 960], [273, 976], [240, 976], [226, 963], [226, 863], [240, 852]], [[457, 949], [457, 1247]], [[477, 1197], [715, 1197]], [[739, 961], [726, 980], [726, 1034], [741, 1050], [785, 1050], [792, 1036], [792, 981], [778, 962], [739, 961]], [[730, 1081], [1108, 1081], [1108, 1138], [752, 1138], [732, 1123], [732, 1081]], [[1094, 916], [1094, 1056]], [[1137, 935], [1137, 1173], [1160, 1196], [1208, 1196], [1242, 1169], [1242, 935], [1211, 906], [1168, 906], [1137, 935]], [[748, 1161], [1005, 1161], [1030, 1182], [1030, 1212], [1007, 1240], [748, 1240], [728, 1222], [728, 1181], [748, 1161]]]}
(W/'regions.json').write_text(json.dumps({'coordinate_resolution':N,'regions':regions,'normal_source':'Traced physical seams, bounded radiator recesses and inset glazing only; no albedo-noise bump'},indent=2)+'\n')
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
signed=np.maximum.reduce([poly(p) for p in regions['glass']]);glass=smooth(0,2,signed);seal=smooth(-7,-2,signed)
for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,2,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['vents']:
 d=capsule(a,b,r);mask=smooth(0,2,d);h-=.9*smooth(0,5,d);structure=np.maximum(structure,mask)
# Recess and ribs are bounded by their actual atlas housings.
for points,axis,centres in [
 ([[205,74],[227,58],[256,58],[274,77],[274,147],[257,163],[224,163],[205,145]],'y',[90,101,114,127]),
 ([[637,964],[680,964],[693,977],[693,1068],[680,1083],[635,1083],[626,1069],[626,978]],'y',[978,995,1012,1029,1046,1063]),
 ([[407,748],[436,721],[478,721],[498,745],[480,780],[436,780]],'y',[736,746,756,766]),
 ([[260,728],[288,693],[305,728],[293,769],[278,769]],'x',[279,291]),
 ([[410,1060],[430,1060],[435,1228],[408,1228]],'y',[1080,1110,1140,1170,1200])]:
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
im=bpy.data.images.load(str(M/'lagg_hull_glazing_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.15,.48,lum)*.65;metal=metal*(1-structure)+(.08+.62*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.03,.18,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.54*metal+.04*wear,.52,.89);rough=rough*(1-structure)+(.89-.3*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.15*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[signed>3]=[0,0,1]
records={}
def save(a,key,colorspace='Non-Color'):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Lagg '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);n=b.reshape(-1,4);v=n[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);n[:,:3]=v*.5+.5;im.pixels.foreach_set(n.ravel())
 p=M/f'lagg_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':sha(p),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
mat=bpy.data.materials.new('Lagg_Worn_Hull_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
scene=D/'lagg_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_sha
report={'source':str(src),'source_sha256':original_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':2,'stored_triangles':688,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repairs,'max_visible_uv_anisotropy':max(a[2] for a in aspects),'maps':{'hull':records},'models':models,'structural_height_only':True,'window_recess':{'depth':1.7,'bevel_width_master_pixels':7,'glass_interiors_flat':True,'no_raised_rim':True},'emissives':'deferred','runtime_visual_validation':'pending_user_review'}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('LAGG_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
