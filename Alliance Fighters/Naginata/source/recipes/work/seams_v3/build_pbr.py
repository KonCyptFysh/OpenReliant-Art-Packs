import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2];W=D/'work/seams_v3';M=D/'maps/seams_v3';prior=json.loads((W/'prior_project_state.json').read_text());reg=json.loads((W/'regions.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'naginata_worn_aligned_v3.blend'));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];base=obs[0].active_material.node_tree.nodes['Delivered basecolor'].image;bpy.context.view_layer.update()
def signature():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest()
sig=signature();N=4096;S=1254/N;yy,xx=np.mgrid[:N,:N].astype(np.float32);X=(xx+.5)*S;Y=(yy+.5)*S;del xx,yy;records=dict(prior['maps'])
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def poly(points):
 p=np.array(points);d=np.full(X.shape,1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/np.linalg.norm(v))
 return d
def capsule(a,b,r):
 a=np.array(a);v=np.array(b)-a;t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/np.dot(v,v),0,1);return r-np.sqrt((X-a[0]-t*v[0])**2+(Y-a[1]-t*v[1])**2)
def roi(points,pad,func):
 global X,Y
 ox,oy=X,Y;p=np.array(points);lo=np.maximum(0,np.floor((p.min(0)-pad)/S).astype(int));hi=np.minimum(N,np.ceil((p.max(0)+pad)/S).astype(int));sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]];X=ox[sl];Y=oy[sl];v=func();X,Y=ox,oy;return sl,v
def load(path,channels=1):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(N,N,4)[::-1,:,:channels].copy();bpy.data.images.remove(im);return a if channels>1 else a[:,:,0]
def save(data,kind,keep=False):
 a=np.ones((N,N,4),np.float32);a[:,:,:3]=data if data.ndim==3 else data[:,:,None];im=bpy.data.images.new('Naginata v3 '+kind,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());path=M/f'naginata_worn_{kind}_4k_v3.png';im.filepath_raw=str(path);im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();bpy.data.images.remove(im);records[kind]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 if keep:im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';im.pack();return im
h=np.zeros_like(X);glass=np.zeros_like(X);seal=np.zeros_like(X);flat=np.zeros_like(X);structure=np.zeros_like(X);fin=np.zeros_like(X);panel=np.zeros_like(X);panel_mask=np.zeros_like(X)
for p in reg['glass']:
 sl,d=roi(p,10,lambda:poly(p));g=smooth(-.2,1,d);glass[sl]=np.maximum(glass[sl],g);seal[sl]=np.maximum(seal[sl],smooth(-8,-6,d)*(1-g))
for a,b,c,d in reg['flat_caution_boxes']:
 p=[(a,b),(c,b),(c,d),(a,d)];sl,dist=roi(p,2,lambda:poly(p));flat[sl]=np.maximum(flat[sl],smooth(-.5,.8,dist))
def apply(sl,z,mask,f=None):
 h[sl]=h[sl]*(1-mask)+z*mask;structure[sl]=np.maximum(structure[sl],mask)
 if f is not None:fin[sl]=np.maximum(fin[sl],f)
# Equipment recess and its solid inset cover.
p=reg['equipment_bay'];sl,d=roi(p,3,lambda:poly(p));mask=smooth(-1,0,d);apply(sl,-8*smooth(0,3,d),mask)
p=reg['equipment_plate'];sl,d=roi(p,3,lambda:poly(p));mask=smooth(0,2,d);h[sl]=h[sl]*(1-mask)-1.4*mask;fin[sl]=np.maximum(fin[sl],mask*.65)
# Straight, smooth machined channels and their raised longitudinal fins.
for f in reg['vents']:
 a,b,r,n,depth=f['a'],f['b'],f['radius'],f['rails'],f['depth']
 def calc():
  d=poly(f['polygon']) if 'polygon' in f else capsule(a,b,r);inside=smooth(0,min(2.5,r*.55),d);v=np.array(b)-a;v=v/np.linalg.norm(v);across=-(X-a[0])*v[1]+(Y-a[1])*v[0];ribs=np.zeros_like(X);pitch=2*r/(n+1)
  for i in range(n):ribs=np.maximum(ribs,1-smooth(pitch*.13,pitch*.39,np.abs(across-(i-(n-1)/2)*pitch)))
  ribs*=smooth(2,4,d);return -depth*inside+(depth+1.0)*ribs,smooth(-1,0,d),ribs
 sl,(z,mask,ribs)=roi([a,b],r+3,calc);apply(sl,z,mask,ribs)
# Belly radiator: four aligned rows of rounded metal fins above one clean dark floor.
bank=reg['radiator'];p=bank['polygon'];sl,d=roi(p,3,lambda:poly(p));apply(sl,bank['floor']*smooth(0,2,d),smooth(-1,0,d))
for y in bank['fin_y_centres']:
 for x in bank['fin_x_centres']:
  sl,d=roi([(x-7,y),(x+7,y)],6,lambda:capsule((x-7,y),(x+7,y),4));f=smooth(0,2.5,d);h[sl]=h[sl]*(1-f)+bank['fin_top']*f;fin[sl]=np.maximum(fin[sl],f);structure[sl]=np.maximum(structure[sl],f)
for y in [1097,1129]:
 sl,d=roi([(142,y),(508,y)],3,lambda:capsule((142,y),(508,y),1.6));f=smooth(0,1.3,d);h[sl]=h[sl]*(1-f)+.5*f;fin[sl]=np.maximum(fin[sl],f)
# Circular fittings keep shaped rims and solid centres, without colour-derived pitting.
for cx,cy,r in reg['sockets']:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);d=r-rr;mask=smooth(-1,0,d);rim=(1-smooth(1,3,np.abs(rr-(r-3))))*smooth(0,2,d);boss=(1-smooth(r*.45,r*.6,rr));return -7*smooth(0,2.4,d)+8*rim+5.4*boss,mask,np.maximum(rim,boss*.6)
 sl,(z,mask,f)=roi([(cx,cy)],r+3,calc);apply(sl,z,mask,f)
for cx,cy,r in reg['round_louvres']:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);d=r-rr;f=np.zeros_like(X)
  for y in [-14,-7,0,7,14]:f=np.maximum(f,1-smooth(.6,2.3,np.abs(Y-cy-y)))
  f*=smooth(2,4,d);return -10*smooth(0,2,d)+11*f,smooth(-1,0,d),f
 sl,(z,mask,f)=roi([(cx,cy)],r+3,calc);apply(sl,z,mask,f)
for cx,cy in reg['fasteners']:
 def calc():
  rr=np.sqrt((X-cx)**2+(Y-cy)**2);outer=1-smooth(2.8,4.2,rr);boss=1-smooth(.9,2.4,rr);return -.8*outer+1.7*boss,outer,boss
 sl,(z,mask,f)=roi([(cx,cy)],5,calc);apply(sl,z,mask,f)
for path in reg['panel_paths']:
 for a,b in zip(path,path[1:]):
  sl,d=roi([a,b],4,lambda:capsule(a,b,reg['panel_half_width']));f=smooth(0,1.8,d);panel[sl]=np.minimum(panel[sl],-reg['panel_depth']*f);panel_mask[sl]=np.maximum(panel_mask[sl],f)
allow=(1-structure)*(1-glass)*(1-seal)*(1-flat);h+=panel*allow;panel_mask*=allow
h=h*(1-seal)-.45*seal;h=h*(1-glass)-.8*glass;h*=1-flat;structure=np.maximum(structure,seal);fin*=1-np.maximum(glass,seal)
assert h.min()>-24 and h.max()<12
# Slope-to-normal conversion uses the authored height only. No displacement or noisy albedo bump.
dy,dx=np.gradient(h,S);normal=np.stack((-dx,dy,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);ni=save(normal*.5+.5,'normal',True);save((h+24)/36,'height');save(glass,'glass');save(seal,'seal');save(flat,'flat_graphics');save(structure,'structure_mask');save(fin,'fin_mask');save(panel_mask,'panel_mask');del normal,dx,dy
paint=load(D/'maps/pbr_v2/naginata_painted_graphics_mask_4k_v2.png');rgb=load(prior['basecolour'],3);mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);sat=(mx-mn)/(mx+1e-6)
metal=(1-smooth(.10,.28,sat))*smooth(.20,.55,lum)*.88;metal*=1-paint;metal=metal*(1-structure)+(.12+.76*fin)*structure;metal*=1-np.maximum(glass,np.maximum(flat,seal));metal=metal*(1-panel_mask)+.1*panel_mask
local=(np.roll(lum,5,0)+np.roll(lum,-5,0)+np.roll(lum,5,1)+np.roll(lum,-5,1))*.25;wear=smooth(.015,.10,np.abs(lum-local));variation=np.sin(X*.028)*np.sin(Y*.031)
rough=np.clip(.82*(1-metal)+.46*metal+.028*variation+.08*wear,.43,.95);rough=rough*(1-paint)+(.8+.04*wear)*paint;rough=rough*(1-structure)+(.82-.42*fin+.018*variation)*structure;rough=rough*(1-panel_mask)+.85*panel_mask;rough=rough*(1-flat)+.82*flat;rough=rough*(1-seal)+.87*seal;rough=rough*(1-glass)+(.14+.018*wear)*glass
spec=.30*(1-glass)+.5*glass;spec=spec*(1-panel_mask)+.22*panel_mask;spec=spec*(1-seal)+.22*seal;coat=.24*glass
maps={'basecolor':base,'normal':ni,'metallic':save(metal,'metallic',True),'roughness':save(rough,'roughness',True),'specular':save(spec,'specular',True),'coat':save(coat,'coat',True)}
mat=bpy.data.materials.new('Naginata_Worn_PBR_v3');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();uv=n.new('ShaderNodeUVMap');uv.name='Atlas UV';uv.uv_map='Naginata_Aligned_UV_v3';bs=n.new('ShaderNodeBsdfPrincipled');bs.name='Worn physical surface';bs.inputs['IOR'].default_value=1.46;out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs[0])
for name,image in maps.items():
 q=n.new('ShaderNodeTexImage');q.name='Delivered '+name;q.image=image;q.extension='REPEAT';l.new(uv.outputs[0],q.inputs[0])
 if name=='normal':
  nm=n.new('ShaderNodeNormalMap');nm.uv_map=uv.uv_map;nm.inputs['Strength'].default_value=1;l.new(q.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
 else:l.new(q.outputs[0],bs.inputs[{'basecolor':'Base Color','metallic':'Metallic','roughness':'Roughness','specular':'Specular IOR Level','coat':'Coat Weight'}[name]])
for o in obs:o.data.materials[0]=mat
assert signature()==sig;assert bytes(base.packed_file.data)==Path(prior['basecolour']).read_bytes();s['pbr_status']='Finished Naginata worn material authoring: clean structural-only normals, lightly weathered smoked glass, matte paint and varied metal.';bpy.context.preferences.filepaths.save_version=0;s.view_settings.exposure=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'naginata_worn_aligned_v3.blend'))
stats={'glass_roughness_median':float(np.median(rough[glass>.999])),'glass_metallic_max':float(metal[glass>.999].max()),'paint_roughness_median':float(np.median(rough[(metal<.1)&(glass<.1)&(structure<.1)&(panel_mask<.1)])),'steel_roughness_median':float(np.median(rough[(metal>.75)&(structure<.1)])),'height_min':float(h.min()),'height_max':float(h.max()),'panel_depth':reg['panel_depth'],'radiator_floor':bank['floor'],'radiator_fin_top':bank['fin_top']}
r={'source_scene':prior['latest_scene'],'scene':str(D/'naginata_worn_aligned_v3.blend'),'geometry_signature':sig,'geometry_uv_native_normals_preserved':True,'basecolor_unchanged':True,'maps':records,'material_statistics':stats,'height_decode':'normalized PNG * 36 - 24 in 1254-atlas pixel units; height baked into normal, no displacement','parts':2,'stored_LOD0_triangles':400,'visible_intact_LOD0_triangles':376,'engine_validation':'not_tested'};(W/'validation.json').write_text(json.dumps(r,indent=2));print('PBR_AUTHORED',stats,flush=True)
