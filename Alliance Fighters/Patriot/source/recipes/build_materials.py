import bpy,numpy as np,json,hashlib,math
from pathlib import Path
D=Path('local-only://worn');W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
src=D/'patriot_source_review.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];source_sha=hashlib.sha256(src.read_bytes()).hexdigest();bpy.context.view_layer.update()
before={o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'n':[list(n.vector) for n in o.data.corner_normals],'uv':{u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers}} for o in obs}
# Repair the handful of collapsed original islands by reusing quiet matching material areas.
# These are material-only underside/tip walls; canopy, livery and broad faces keep their UVs.
repairs=[];newuv='Patriot_Delivery_UV_v1'
for o in obs:
 m=o.data;u=m.uv_layers.new(name=newuv,do_init=True);m.uv_layers.active=u;u.active_render=True
 groups=[]
 if o.name=='Patriot_Cockpit':groups=[([50,51],(932,367,1003,421))]
 if o.name=='Patriot_Body':groups=[([41,42],(833,143,876,188)),([301,302],(833,143,876,188))]
 for ids,box in groups:
  vert_ids=sorted({v for i in ids for v in m.polygons[i].vertices});pts=np.array([list(o.matrix_world@m.vertices[i].co) for i in vert_ids]);mean=pts.mean(0);_,_,vh=np.linalg.svd(pts-mean);q=(pts-mean)@vh[:2].T;lo=q.min(0);hi=q.max(0);a,b,c,d=box;scale=min((c-a)/(hi[0]-lo[0]),(d-b)/(hi[1]-lo[1]));mapped=(q-(lo+hi)/2)*scale+np.array([(a+c)/2,(b+d)/2]);lookup={i:v for i,v in zip(vert_ids,mapped)}
  for i in ids:
   p=m.polygons[i]
   for k in p.loop_indices:
    x,y=lookup[m.loops[k].vertex_index];u.data[k].uv=(x/N,1-y/N)
  repairs.append({'part':o.name,'faces':ids,'reuse_box_atlas_pixels':box,'projection':'isotropic local plane; no new texture section'})
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=xx+.5;Y=yy+.5
def smooth(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);return r-np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
def poly(p):
 p=np.array(p);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
def roi(points,pad,fn):
 global X,Y
 ox,oy=X,Y;p=np.array(points);lo=np.maximum(0,np.floor(p.min(0)-pad).astype(int));hi=np.minimum(N,np.ceil(p.max(0)+pad).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];X=ox[sl];Y=oy[sl];result=fn();X,Y=ox,oy;return sl,result
glass_polys=[[(71,33),(99,33),(109,43),(109,68),(99,78),(72,78),(63,68),(63,44)],[(70,95),(101,95),(113,108),(113,282),(98,297),(71,297),(58,282),(58,107)],[(71,338),(98,338),(107,349),(107,530),(96,541),(72,541),(62,530),(62,350)],[(18,402),(33,402),(39,413),(39,537),(32,545),(19,545),(13,535),(13,413)],[(145,402),(153,402),(159,413),(159,537),(151,545),(142,539),(139,415)],[(531,542),(576,542),(591,562),(578,576),(509,576),(507,566)]]
flat_boxes=[(0,0,1254,18),(10,136,40,238),(137,155,162,242),(163,78,199,314),(595,90,627,161),(772,91,800,165),(362,85,443,307),(1020,117,1044,178),(1211,118,1241,178),(346,451,436,480),(1034,588,1230,614),(1024,592,1053,806),(1033,783,1232,808),(1209,595,1233,804),(139,654,281,724),(107,610,268,629),(252,1042,530,1087),(541,972,672,992),(694,1170,731,1220),(24,1053,164,1081),(26,1079,83,1141),(22,1156,165,1180),(438,509,510,646),(474,479,630,510),(621,502,687,829),(461,799,641,829),(548,687,564,744)]
vents=[((350,409),(560,409),18,3,'long'),((698,119),(698,293),17,37,'cross'),((749,435),(749,504),17,3,'long'),((850,598),(850,792),8,44,'cross'),((898,598),(898,792),8,44,'cross'),((1002,882),(1002,1163),9,50,'cross'),((587,1028),(789,1028),12,3,'long'),((469,1196),(646,1196),10,2,'long'),((819,1230),(1006,1230),6,2,'long'),((1077,865),(1194,969),10,2,'long'),((1067,917),(1154,994),9,2,'long')]
for x in [1078,1114,1149,1183]:vents.append(((x,349),(x,481),9,25,'cross'))
for y,r in [(576,8),(603,8),(633,8),(662,8),(689,7)]:vents.append(((727,y),(765 if y<680 else 746,y),r,1,'long'))
panels=[[(0,318),(60,318)],[(110,318),(603,318)],[(13,312),(603,312)],[(152,337),(265,337)],[(271,343),(304,343)],[(167,56),(297,56),(297,312)],[(235,79),(235,310)],[(171,239),(345,239)],[(266,75),(266,313)],[(179,82),(291,82)],[(828,87),(1045,87)],[(860,132),(995,132)],[(890,132),(890,253)],[(891,184),(1012,184)],[(818,259),(1048,259)],[(815,307),(1044,307)],[(895,305),(895,544)],[(971,308),(971,544)],[(817,454),(1039,454)],[(806,543),(1249,543)],[(921,548),(921,838)],[(806,647),(1025,647)],[(791,840),(1253,840)],[(106,576),(271,576),(271,740),(132,740)],[(131,638),(131,741)],[(36,765),(110,765)],[(116,762),(203,850),(435,850)],[(25,923),(136,923)],[(176,906),(176,992)],[(26,985),(211,985)],[(235,864),(324,954),(324,1036),(548,1036)],[(455,888),(797,888)],[(551,845),(551,963)],[(550,961),(794,961)],[(691,957),(691,1006)],[(801,892),(838,892)],[(840,845),(840,1178)],[(843,1031),(1047,1031)],[(882,1033),(882,1194)],[(943,1033),(943,1194)],[(884,1098),(985,1098)],[(805,1200),(1047,1200)],[(1053,1026),(1253,1026)],[(175,1121),(441,1121),(441,1253)],[(453,1105),(741,1105)],[(549,1061),(549,1167)],[(644,1061),(644,1167)],[(455,1159),(740,1159)],[(12,1238),(1246,1238)],[(266,486),(339,486)],[(282,550),(433,550)],[(282,601),(433,601)],[(297,648),(433,648)]]
reg={'glass':glass_polys,'flat_caution_and_insignia_boxes':flat_boxes,'vents':vents,'panel_paths':panels,'panel_depth':5.5,'vent_floor':-9,'radiator_floor':-11,'fin_top':.65};(W/'regions.json').write_text(json.dumps(reg,indent=2))
h=np.zeros((N,N),np.float32);glass=h.copy();seal=h.copy();flat=h.copy();structure=h.copy();fin=h.copy();pan=h.copy()
def apply(sl,z,mask,f=None):
 h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask)
 if f is not None:fin[sl]=np.maximum(fin[sl],f)
for p in glass_polys:
 sl,d=roi(p,7,lambda:poly(p));g=smooth(0,1.2,d);glass[sl]=np.maximum(glass[sl],g);seal[sl]=np.maximum(seal[sl],smooth(-5,-3,d)*(1-g))
for a,b,c,d in flat_boxes:
 p=[(a,b),(c,b),(c,d),(a,d)];sl,dst=roi(p,2,lambda:poly(p));flat[sl]=np.maximum(flat[sl],smooth(0,1,dst))
for a,b,r,count,axis in vents:
 def calc():
  d=capsule(a,b,r);v=np.subtract(b,a);length=np.linalg.norm(v);v=v/length;across=-(X-a[0])*v[1]+(Y-a[1])*v[0];along=(X-a[0])*v[0]+(Y-a[1])*v[1];f=np.zeros_like(X)
  pitch=(2*r/(count+1)) if axis=='long' else length/(count+1)
  for i in range(count):f=np.maximum(f,1-smooth(pitch*.12,pitch*.36,np.abs((across if axis=='long' else along)-((i-(count-1)/2)*pitch if axis=='long' else (i+1)*pitch))))
  f*=smooth(1.8,3.7,d);return -9*smooth(0,2.4,d)+9.65*f,smooth(-.6,0,d),f
 sl,(z,mask,f)=roi([a,b],r+2,calc);apply(sl,z,mask,f)
# One clean floor beneath the regular mesh grille. Repeating bars, never luminance pits.
p=[(1054,615),(1207,615),(1207,781),(1054,781)]
def grille():
 d=poly(p);f=np.maximum(1-smooth(.6,1.5,np.abs((X-1057+3.5)%7-3.5)),1-smooth(.5,1.2,np.abs((Y-618+3.5)%7-3.5)));f*=smooth(2,4,d);return -11*smooth(0,2,d)+11.5*f,smooth(-.5,0,d),f
sl,(z,mask,f)=roi(p,2,grille);apply(sl,z,mask,f)
# Machined transverse fin stack and the four rounded exhaust-rib forms.
p=[(799,915),(844,915),(844,1118),(799,1118)]
def finstack():
 d=poly(p);f=(1-smooth(2,5,np.abs((Y-918+9)%18-9)))*smooth(1,3,d);return -9*smooth(0,2,d)+10*f,smooth(-.5,0,d),f
sl,(z,mask,f)=roi(p,2,finstack);apply(sl,z,mask,f)
p=[(194,1189),(218,1157),(251,1141),(361,1141),(388,1169),(390,1224),(193,1224)]
sl,d=roi(p,2,lambda:poly(p));apply(sl,-9*smooth(0,2,d),smooth(0,1,d))
for x in [238,279,323,365]:
 sl,d=roi([(x,1180),(x,1201)],11,lambda:capsule((x,1180),(x,1201),10));f=smooth(0,7,d);h[sl]=h[sl]*(1-f)+1.2*f;fin[sl]=np.maximum(fin[sl],f)
for cx,cy,r in [(857,372,17),(857,437,18),(857,498,17),(589,770,20),(513,770,19),(600,714,27),(1101,1062,15),(1175,1092,14),(234,943,25)]:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);f=1-smooth(r*.35,r*.88,rr);return -2.5*(1-smooth(r-2,r,rr))+4*f,1-smooth(r-1,r,rr),f
 sl,(z,mask,f)=roi([(cx,cy)],r+1,calc);apply(sl,z,mask,f)
for path in panels:
 for a,b in zip(path,path[1:]):
  sl,d=roi([a,b],3,lambda:capsule(a,b,1.85));f=smooth(0,1.4,d);pan[sl]=np.maximum(pan[sl],f)
pan*=1-np.maximum(structure,np.maximum(glass,np.maximum(seal,flat)));h-=5.5*pan;h=h*(1-seal)-.4*seal;h=h*(1-glass)-.55*glass;h*=1-flat
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';im.scale(N,N);a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(N,N,4)[::-1,:,:3].copy()
rgb=load(M/'patriot_worn_basecolor_generated_v1.png');mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6);paint=smooth(.09,.24,sat);metal=(1-paint)*smooth(.15,.45,lum)*.88;metal=metal*(1-structure)+(.08+.78*fin)*structure;metal*=1-np.maximum(flat,np.maximum(glass,seal));metal=metal*(1-pan)+.05*pan
local=(np.roll(lum,3,0)+np.roll(lum,-3,0)+np.roll(lum,3,1)+np.roll(lum,-3,1))*.25;wear=smooth(.02,.16,np.abs(lum-local));variation=np.sin(X*.034)*np.sin(Y*.026)
rough=np.clip(.84*(1-metal)+.48*metal+.065*wear+.018*variation,.44,.94);rough=rough*(1-structure)+(.9-.43*fin+.02*variation)*structure;rough=rough*(1-pan)+.90*pan;rough=rough*(1-flat)+.83*flat;rough=rough*(1-seal)+.9*seal;rough=rough*(1-glass)+(.14+.022*wear)*glass
dy,dx=np.gradient(h);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);records={}
def save(a,key,colorspace='Non-Color'):
 buf=np.ones((N,N,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Patriot '+key,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());im.scale(OUT,OUT);p=M/f'patriot_worn_{key}_4k_v1.png';im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='16' if key!='basecolor' else '8';im.save();bpy.data.images.remove(im);records[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=colorspace;return im
maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic')}
for key,a in [('height',(h+20)/32),('glass',glass),('seal',seal),('flat_graphics',flat),('structure',structure),('fins',fin),('panels',pan),('paint',paint)]:im=save(a,key);bpy.data.images.remove(im)
mat=bpy.data.materials.new('Patriot_Worn_PBR_v1');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newuv;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.38;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
for key,im in maps.items():
 im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;links.new(uv.outputs[0],tx.inputs[0])
 if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newuv;links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
 else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
models={};aspects=[]
for o in obs:
 m=o.data;m.materials[0]=mat;b=before[o.name];assert b['v']==[list(v.co) for v in m.vertices] and b['f']==[list(p.vertices) for p in m.polygons] and b['n']==[list(n.vector) for n in m.corner_normals]
 for name,values in b['uv'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 models[o.name]={'vertices':[list(v.co) for v in m.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
 for p in m.polygons:
  if p.material_index==1:continue
  pts=np.array([list(o.matrix_world@m.vertices[i].co) for i in p.vertices]);e=pts[1:]-pts[0];n=np.cross(*e);n/=max(np.linalg.norm(n),1e-9);t=e[0]/np.linalg.norm(e[0]);local=e@np.stack((t,np.cross(n,t)),axis=1);q=np.array([list(m.uv_layers[newuv].data[i].uv) for i in p.loop_indices]);sing=np.linalg.svd(np.linalg.solve(local,q[1:]-q[0]),compute_uv=False);aspects.append(float(sing[0]/max(sing[1],1e-12)))
assert max(aspects)<4.1;scene=D/'patriot_worn_pbr_v1.blend';s.view_settings.exposure=0;s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
report=dict(source=str(src),source_sha256=source_sha,scene=str(scene),scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),active_uv=newuv,parts=3,stored_triangles=440,visible_triangles=428,original_geometry_normals_and_uvs_preserved=True,uv_repairs=repairs,max_visible_uv_anisotropy=max(aspects),maps=records,models=models,structural_height_only=True,emissives='deferred',runtime_visual_validation='left to user as requested',statistics={'glass_roughness_median':float(np.median(rough[glass>.99])),'glass_metallic_max':float(metal[glass>.99].max()),'height_min':float(h.min()),'height_max':float(h.max()),'steel_roughness_median':float(np.median(rough[(metal>.7)&(structure<.1)]))});(W/'validation.json').write_text(json.dumps(report,indent=2));print('PATRIOT_PBR_COMPLETE',report['statistics'],flush=True)
