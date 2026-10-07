import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path('authoring://Coyote/worn');M=D/'maps/pbr_v4';W=D/'work/pbr_v4'
bpy.ops.wm.open_mainfile(filepath=str(D/'coyote_worn_normals_v3.blend'));s=bpy.context.scene;s.frame_set(13);obs=[o for o in s.objects if o.type=='MESH'];mat=obs[0].active_material;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Worn PBR from delivered maps'];uv=n['Corrected canopy UV'];N=4096;S=1600/N

def signature():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(q.vector) for q in o.data.corner_normals],[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest()
sig=signature();preserved={i:hashlib.sha256(bytes(n[i].image.packed_file.data)).hexdigest() for i in ['Final basecolor','Smooth cockpit glazing selection']}
def load(path):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(N,N,4)[::-1].copy()
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def blur(a):
 for axis in (0,1):
  b=np.zeros_like(a)
  for k,w in [(-3,1),(-2,6),(-1,15),(0,20),(1,15),(2,6),(3,1)]:b+=np.roll(a,k,axis)*w/64
  a=b
 return a
records={}
def save(a,kind):
 data=np.ones((N,N,4),np.float32);data[:,:,:3]=a[:,:,None] if a.ndim==2 else a
 im=bpy.data.images.new('Coyote v4 '+kind,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(data[::-1]).ravel());im.filepath_raw=str(M/f'coyote_{kind}_4k_v4.png');im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();im.pack();records[kind]={'path':im.filepath_raw,'sha256':hashlib.sha256(Path(im.filepath_raw).read_bytes()).hexdigest()};return im
def tex(im,kind):
 t=n.new('ShaderNodeTexImage');t.name='Delivered v4 '+kind;t.image=im;l.new(uv.outputs[0],t.inputs[0]);return t
# This is manufactured height data, not colour luminance. Remove the older photographic normal layer.
h=blur(load(D.parent/'new/maps/authored_height_4k.png')[:,:,0]);glass=load(D/'maps/coyote_worn_glass_4k.png')[:,:,0];sign=load(D.parent/'new/maps/flat_graphics_4k.png')[:,:,0]
y,x=np.mgrid[:N,:N].astype(np.float32);x=(x+.5)*S;y=(y+.5)*S
# Extra caution labels absent from the old mask; interiors only, retaining their mounting plates.
boxes=[(629,944,686,1040),(758,1063,819,1080),(1207,886,1257,969),(481,1535,582,1553)]
for a,b,c,d in boxes:sign=np.maximum(sign,smooth(0,1.5,np.minimum.reduce([x-a,c-x,y-b,d-y])))
# Vent/radiator domains: suppress all noisy micro-normal detail here.
structure=np.zeros_like(h)
def box(a,b,c,d):return smooth(0,2,np.minimum.reduce([x-a,c-x,y-b,d-y]))
for r in [(668,33,925,80),(722,80,925,125),(722,203,925,253),(666,253,925,299),(1030,501,1488,540),(974,803,1010,1113),(176,881,274,1063),(384,1445,593,1495),(770,1168,940,1211),(663,1402,1308,1600)]:structure=np.maximum(structure,box(*r))
# Normal slopes from the clean height; rounded radiator section stays cylindrical.
dy,dx=np.gradient(h*13,S);v=np.stack((-dx,dy,np.ones_like(h)),-1);v/=np.linalg.norm(v,axis=-1,keepdims=True);del dx,dy
old=load(D/'maps/normals_v3/coyote_worn_normal_4k_v3.png')[:,:,:3]*2-1
v[:,:,:2]+=old[:,:,:2]*(.025*(1-structure)*(1-sign)*(1-glass))[:,:,None];del old
protect=np.maximum(sign,glass);v=v*(1-protect[:,:,None])+np.array([0,0,1],np.float32)*protect[:,:,None]
# Real panel cuts continue through painted insignia and striped panels.
seams=[((257,1379),(612,1379)),((380,1200),(380,1440)),((91,762),(91,851)),((0,852),(320,852))]
for a,b in seams:
 a=np.array(a);delta=np.array(b)-a;t=np.clip(((x-a[0])*delta[0]+(y-a[1])*delta[1])/np.dot(delta,delta),0,1);dist=np.sqrt((x-a[0]-t*delta[0])**2+(y-a[1]-t*delta[1])**2);z=-2.2*(1-smooth(.65,2.2,dist));dy,dx=np.gradient(z,S);nv=np.stack((-dx,dy,np.ones_like(h)),-1);nv/=np.linalg.norm(nv,axis=-1,keepdims=True);fac=(1-smooth(2.4,3.5,dist))*sign*(1-glass);v=v*(1-fac[:,:,None])+nv*fac[:,:,None]
v/=np.linalg.norm(v,axis=-1,keepdims=True);normal=save(v*.5+.5,'normal');del v,nv,dx,dy
save(h,'structural_height');save(sign,'flat_graphics');save(structure,'vent_mask')
# Approved paint/metal and glass settings already match the later approach. Correct sign and radiator domains.
statistics={}
for kind,path,socket in [('metallic',D/'maps/coyote_worn_metallic_4k.png','Metallic'),('roughness',D/'maps/material_refinement_v2/coyote_worn_roughness_refined_4k.png','Roughness'),('specular',D/'maps/material_refinement_v2/coyote_worn_specular_refined_4k.png','Specular IOR Level')]:
 arr=load(path)[:,:,0];original=arr.copy()
 if kind=='metallic':arr=arr*(1-sign);arr=arr*(1-glass)
 elif kind=='roughness':arr=arr*(1-sign)+.8*sign;arr=arr*(1-structure)+(.51+.045*np.sin(x*.021)*np.sin(y*.029))*structure;arr=arr*(1-glass)+original*glass
 else:arr=arr*(1-sign)+.3*sign
 statistics[kind]={'glass_median':float(np.median(arr[glass>.99])),'sign_median':float(np.median(arr[sign>.99])),'glass_max_change':float(np.max(np.abs(arr-original)[glass>.99]))};tx=tex(save(arr,kind),kind);l.new(tx.outputs[0],bs.inputs[socket])
tx=tex(normal,'normal');nm=n.new('ShaderNodeNormalMap');nm.name='Clean manufactured relief v4';nm.uv_map=uv.uv_map;nm.inputs['Strength'].default_value=1;l.new(tx.outputs[0],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
mat.name='Coyote_Worn_PBR_v4';audit=[]
for o in obs:
 assert o.data.uv_layers.get(uv.uv_map)
 for p in o.data.polygons:assert o.material_slots[p.material_index].material==mat
 audit.append({'part':o.name,'faces':len(o.data.polygons),'material':mat.name,'uv':uv.uv_map})
assert signature()==sig
for i,hsh in preserved.items():assert hashlib.sha256(bytes(n[i].image.packed_file.data)).hexdigest()==hsh
s['pbr_status']='v4 clean structural normals, smooth rounded radiator fins, paint-only signage, approved glass retained. Engine pending.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'coyote_worn_pbr_v4.blend'))
(W/'validation.json').write_text(json.dumps({'geometry_uv_corner_normals_transforms_preserved':True,'geometry_signature':sig,'basecolour_and_glass_byte_identical':True,'material_assignments':audit,'material_statistics':statistics,'maps':records,'engine_validation':'not_tested'},indent=2));print('BUILD_COMPLETE',flush=True)
