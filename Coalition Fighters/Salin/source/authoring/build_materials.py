from pathlib import Path
import os,json,hashlib
import bpy,numpy as np
from bpy_extras.object_utils import world_to_camera_view
D=Path(os.environ['SALIN_WORKSPACE']);W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'salin_source_review.blend';original_sha=sha(src);bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(n.vector) for n in o.data.corner_normals],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
newuv='Salin_Delivery_UV_v1'
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
regions={'glass': [[[226, 616], [265, 576], [275, 574], [291, 590], [294, 605], [233, 624]], [[317, 562], [434, 532], [441, 557], [439, 562], [339, 589], [332, 587]], [[440, 902], [452, 891], [541, 891], [552, 902], [552, 931], [537, 947], [463, 947], [440, 923]], [[593, 902], [604, 891], [725, 891], [736, 902], [736, 935], [725, 946], [604, 946], [593, 935]]], 'vents': [[[150, 311], [187, 311], 5], [[150, 326], [187, 326], 5], [[43, 765], [130, 765], 5], [[43, 780], [130, 780], 5], [[43, 891], [133, 891], 5], [[43, 908], [133, 908], 5], [[763, 519], [884, 519], 5], [[763, 537], [884, 537], 5], [[766, 575], [873, 575], 5], [[766, 590], [873, 590], 5], [[1009, 425], [1009, 553], 7], [[934, 686], [934, 785], 5], [[835, 825], [835, 872], 8], [[900, 825], [900, 872], 8], [[1179, 765], [1179, 794], 7], [[1167, 1154], [1167, 1194], 8], [[470, 818], [514, 818], 5], [[470, 832], [514, 832], 5], [[516, 685], [564, 685], 5], [[516, 701], [564, 701], 5]], 'circles': [[90, 536, 15], [165, 527, 12], [237, 535, 16], [135, 572, 11], [190, 572, 11], [899, 184, 13], [899, 254, 13], [1207, 535, 13], [1207, 592, 13], [1207, 651, 13], [260, 899, 12], [314, 899, 12], [367, 899, 12]], 'flat': [[557, 122, 682, 242], [136, 317, 299, 464], [0, 288, 75, 453], [0, 1055, 401, 1225], [751, 984, 842, 1158], [15, 115, 40, 181], [177, 112, 220, 174], [392, 60, 434, 138], [1033, 48, 1109, 76], [579, 14, 806, 50], [445, 215, 493, 295], [742, 218, 813, 265], [563, 318, 666, 355], [752, 338, 892, 480], [964, 146, 990, 289], [863, 194, 925, 239], [1037, 90, 1135, 124], [15, 574, 67, 657], [234, 650, 311, 680], [365, 638, 440, 679], [560, 526, 685, 579], [1123, 582, 1164, 630], [153, 447, 375, 479], [23, 153, 40, 180], [191, 740, 310, 800], [189, 868, 217, 926], [498, 655, 517, 727], [724, 630, 897, 656], [813, 805, 943, 894], [1129, 1040, 1181, 1105], [939, 1007, 981, 1077]], 'panels': [[[0, 195], [231, 195], [313, 252], [446, 252]], [[0, 227], [48, 227], [87, 273], [228, 273], [419, 460], [472, 460], [521, 413]], [[137, 278], [137, 365], [196, 365]], [[228, 274], [231, 235]], [[31, 475], [127, 475], [127, 487], [315, 487], [315, 518]], [[0, 731], [389, 731], [415, 755], [415, 795], [395, 815], [39, 815], [23, 799], [23, 755], [42, 735]], [[42, 860], [393, 860], [416, 885], [416, 922], [393, 946], [42, 946], [23, 926], [23, 883], [42, 860]], [[171, 738], [171, 812]], [[172, 862], [172, 941]], [[58, 820], [389, 820]], [[441, 738], [441, 878]], [[0, 958], [246, 958], [272, 985], [603, 985]], [[0, 997], [43, 997], [91, 1042], [250, 1042], [422, 1219]], [[264, 1037], [264, 997]], [[327, 969], [573, 1211]], [[417, 1251], [509, 1251], [547, 1215]], [[336, 0], [336, 14], [435, 14], [483, 63], [483, 211]], [[390, 0], [390, 30]], [[392, 174], [408, 190], [408, 244]], [[532, 63], [532, 201], [577, 245], [727, 245]], [[584, 9], [532, 63]], [[578, 11], [838, 11], [851, 30], [851, 213], [823, 242]], [[537, 151], [592, 151]], [[776, 95], [776, 207]], [[843, 70], [849, 70]], [[706, 251], [706, 312], [559, 312]], [[850, 149], [954, 149]], [[960, 170], [960, 282], [944, 313], [715, 313]], [[1036, 0], [1036, 32]], [[1012, 87], [1160, 87], [1160, 37], [1245, 37]], [[1024, 91], [1024, 135]], [[1075, 85], [1075, 133]], [[1117, 165], [1174, 165]], [[1179, 153], [1190, 142], [1216, 142], [1225, 151], [1225, 281], [1215, 295], [1186, 295], [1176, 284], [1176, 154]], [[1201, 169], [1201, 276]], [[1190, 301], [1190, 397], [1152, 433], [1117, 433]], [[950, 297], [950, 385], [1070, 385], [1105, 417]], [[944, 588], [1041, 588], [1041, 729]], [[1041, 648], [1170, 648]], [[1180, 696], [1251, 696]], [[1180, 697], [1180, 725]], [[1118, 523], [1118, 697]], [[1090, 697], [1090, 921], [972, 921], [952, 901]], [[1119, 922], [1191, 922], [1191, 969]], [[1240, 920], [1236, 1095]], [[1229, 1116], [1160, 1116], [1121, 1080], [1121, 963], [1110, 949]], [[778, 800], [778, 903], [950, 903], [950, 800], [778, 800]], [[715, 592], [715, 664], [903, 664], [903, 714]], [[731, 612], [949, 612]], [[903, 716], [821, 716], [821, 789]], [[915, 678], [925, 663], [944, 663], [953, 677], [953, 791]], [[489, 649], [536, 649], [646, 709], [614, 736], [489, 736], [489, 649]], [[487, 601], [700, 601]], [[535, 580], [479, 580]], [[331, 617], [331, 712], [394, 712], [442, 756]], [[459, 489], [459, 643]], [[340, 625], [427, 625], [459, 648], [459, 671], [431, 699], [361, 699], [347, 685], [347, 642]], [[573, 882], [573, 973], [835, 973]], [[434, 881], [434, 938], [459, 960], [562, 960]], [[584, 990], [723, 990], [749, 1018], [749, 1139], [721, 1171], [605, 1171], [565, 1132], [565, 1032], [584, 990]], [[590, 1026], [590, 1150]], [[848, 908], [848, 1175], [876, 1175], [876, 908]], [[878, 950], [921, 950]], [[983, 955], [1008, 984], [1008, 1088], [976, 1115], [940, 1115], [913, 1088], [913, 1010], [936, 986]], [[854, 1175], [1107, 1175]], [[946, 1119], [946, 1171]], [[1041, 931], [1041, 1167]], [[1095, 952], [1095, 1233]], [[853, 1214], [941, 1214]]]}
(W/'regions.json').write_text(json.dumps({'coordinate_resolution':N,'regions':regions,'normal_source':'Traced physical seams, bounded radiator recesses and inset glazing only; no albedo-noise bump'},indent=2)+'\n')
h=np.zeros((N,N),np.float32);structure=h.copy();fins=h.copy();pan=h.copy();flat=h.copy()
signed=np.maximum.reduce([poly(p) for p in regions['glass']]);glass=smooth(0,2,signed);seal=smooth(-7,-2,signed)
for a,b,c,d in regions['flat']:flat=np.maximum(flat,smooth(0,2,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['vents']:
 d=capsule(a,b,r);mask=smooth(0,2,d);h-=.9*smooth(0,5,d);structure=np.maximum(structure,mask)
# Recess and ribs are bounded by their actual atlas housings.
for points,axis,centres in [([[582, 59], [805, 59], [816, 70], [816, 83], [805, 93], [583, 93], [574, 83], [574, 69]], 'y', [70, 83]), ([[985, 196], [997, 187], [1084, 187], [1095, 196], [1095, 235], [1083, 247], [997, 247], [985, 234]], 'y', [207, 226]), ([[576, 386], [653, 386], [653, 483], [576, 483]], 'x', [593, 617, 640]), ([[593, 1052], [598, 1039], [610, 1027], [625, 1021], [651, 1018], [677, 1026], [696, 1042], [704, 1061], [704, 1088], [692, 1107], [673, 1120], [650, 1123], [624, 1118], [605, 1103], [594, 1080]], 'y', [1031, 1041, 1051, 1061, 1071, 1081, 1091, 1101, 1111])]:
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
im=bpy.data.images.load(str(M/'salin_hull_glazing_v1.png'),check_existing=False);im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.12,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.15,.48,lum)*.65;metal=metal*(1-structure)+(.08+.62*fins)*structure;metal*=1-np.maximum(flat,seal);metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.03,.18,np.abs(lum-local));rough=np.clip(.8*(1-metal)+.54*metal+.04*wear,.52,.89);rough=rough*(1-structure)+(.89-.3*fins)*structure;rough=rough*(1-pan)+.86*pan;rough=rough*(1-flat)+.8*flat;rough=rough*(1-seal)+.81*seal;rough=rough*(1-glass)+.15*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal[signed>3]=[0,0,1]
records={}
def save(a,key,colorspace='Non-Color'):
 rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Salin '+key,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
 if key=='normal':
  b=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(b);n=b.reshape(-1,4);v=n[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);n[:,:3]=v*.5+.5;im.pixels.foreach_set(n.ravel())
 p=M/f'salin_hull_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':sha(p),'dimensions':[OUT,OUT]};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+4)/8),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fins),('panels',pan),('paint',paint)]:bpy.data.images.remove(save(a,key))
mat=bpy.data.materials.new('Salin_Worn_Hull_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
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
# Inspected native narrow intake-lip faces sample plain metal; preserve their intentional anisotropy.
assert {(name,face) for name,face,ratio in aspects if ratio>=10}=={('Salin',221),('Salin',222)}
assert max(a[2] for a in aspects)<20
(W/'uv_audit.json').write_text(json.dumps({'passed':True,'visible_faces_checked':len(aspects),'all_uv_triangles_non_degenerate':True,'maximum_anisotropy':max(a[2] for a in aspects),'reviewed_exceptions':[{'face':face,'anisotropy':ratio,'location':'narrow upper intake lip','decision':'Preserve original UVs; these faces sample plain metal, without decals or rib detail.'} for name,face,ratio in aspects if ratio>=10],'coordinates_changed':False},indent=2)+'\n')
for cam in [o for o in s.objects if o.type=='CAMERA' and o.name!='Cockpit']:
 for _ in range(100):
  prior=cam.location.copy();cam.location*=.97;bpy.context.view_layer.update();q=[world_to_camera_view(s,cam,o.matrix_world@v.co) for o in obs for v in o.data.vertices]
  if not all(.08<t.x<.92 and .08<t.y<.92 and t.z>0 for t in q):cam.location=prior;break
scene=D/'salin_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;s.camera=bpy.data.objects['Front'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==original_sha
report={'source':str(src),'source_sha256':original_sha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newuv,'parts':1,'stored_triangles':456,'original_geometry_normals_and_uv_layers_preserved':True,'uv_repairs':repairs,'max_visible_uv_anisotropy':max(a[2] for a in aspects),'maps':{'hull':records},'models':models,'structural_height_only':True,'window_recess':{'depth':1.7,'bevel_width_master_pixels':7,'glass_interiors_flat':True,'no_raised_rim':True},'emissives':'deferred','runtime_visual_validation':'pending_user_review'}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('SALIN_MATERIALS_VALIDATED',flush=True)
for name in ['Front','Opposite','Belly','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/reconstruction_v1'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
