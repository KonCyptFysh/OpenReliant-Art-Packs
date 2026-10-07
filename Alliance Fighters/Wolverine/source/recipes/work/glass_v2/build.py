import bpy, json, hashlib, numpy as np
from pathlib import Path
D=Path('authoring://Wolverine/worn')
W=D/'work/glass_v2'; M=D/'maps'; N=4096
bpy.ops.wm.open_mainfile(filepath=str(D/'wolverine_worn_pbr_v1.blend'))
s=bpy.context.scene; obs=[o for o in s.objects if o.type=='MESH']; bpy.context.view_layer.update()
def signature():
 return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest()
original_signature=signature()
records={}
def save_data(data,kind):
 a=np.ones((N,N,4),np.float32); a[:,:,:3]=data[:,:,None] if data.ndim==2 else data
 im=bpy.data.images.new('Wolverine v2 '+kind,N,N,alpha=False,float_buffer=True); im.colorspace_settings.name='Non-Color'
 im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel()); im.filepath_raw=str(M/f'wolverine_worn_{kind}_4k_v2.png'); im.file_format='PNG'; s.render.image_settings.color_depth='16'; im.save(); im.pack()
 records[kind]={'path':im.filepath_raw,'sha256':hashlib.sha256(Path(im.filepath_raw).read_bytes()).hexdigest()}; return im
def read_data(path):
 im=bpy.data.images.load(str(path),check_existing=False); im.colorspace_settings.name='Non-Color'; a=np.empty(N*N*4,np.float32); im.pixels.foreach_get(a); a=a.reshape(N,N,4)[::-1].copy(); bpy.data.images.remove(im); return a
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
# A two-texel transition within the original dark seals; original metal frame lies outside.
mask=np.zeros((N,N),np.float32); polys=json.loads((D/'work/reconstruction_v1/regions.json').read_text())['glass']; scale=1254/N
for points in polys:
 p=np.asarray(points); lo=np.maximum(0,np.floor((p.min(0)-3)/scale).astype(int)); hi=np.minimum(N,np.ceil((p.max(0)+3)/scale).astype(int)); y,x=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]].astype(np.float32); x=(x+.5)*scale; y=(y+.5)*scale
 d=np.full(x.shape,1e6,np.float32); area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  v=b-a; d=np.minimum(d,np.sign(area)*(v[0]*(y-a[1])-v[1]*(x-a[0]))/np.linalg.norm(v))
 sl=np.s_[lo[1]:hi[1],lo[0]:hi[0]]; mask[sl]=np.maximum(mask[sl],smooth(-2,.5,d))
mask_im=save_data(mask,'glass_colour_mask')
mat=obs[0].active_material; mat.name='Wolverine_Worn_PBR_v2'; n=mat.node_tree.nodes; l=mat.node_tree.links; bs=n['Worn physical surface']; uv=n['Atlas UV']; out=next(q for q in n if q.type=='OUTPUT_MATERIAL'); old=n['Delivered basecolor']; old.name='Preserved v1 basecolor'
generated=bpy.data.images.load(str(M/'wolverine_glass_generated_v2.png')); generated.colorspace_settings.name='sRGB'; generated.pack()
gen=n.new('ShaderNodeTexImage'); gen.name='Glass repair generated v2'; gen.image=generated; l.new(uv.outputs[0],gen.inputs[0])
mt=n.new('ShaderNodeTexImage'); mt.name='Glass-only colour repair mask'; mt.image=mask_im; mt.interpolation='Closest'; l.new(uv.outputs[0],mt.inputs[0])
mix=n.new('ShaderNodeMixRGB'); mix.name='Glass-only colour repair'; l.new(mt.outputs[0],mix.inputs[0]); l.new(old.outputs[0],mix.inputs[1]); l.new(gen.outputs[0],mix.inputs[2])
# Bake the colour-only composite over a full atlas proxy, without altering the ship.
bpy.ops.object.select_all(action='DESELECT'); bpy.ops.mesh.primitive_plane_add(size=2); proxy=bpy.context.object; proxy.data.uv_layers.active.name=uv.uv_map; proxy.data.materials.append(mat)
colour=bpy.data.images.new('Wolverine delivered basecolor v2',N,N,alpha=False); colour.colorspace_settings.name='sRGB'; tx=n.new('ShaderNodeTexImage'); tx.image=colour; tx.name='Delivered basecolor'
for q in n:q.select=False
tx.select=True; n.active=tx; em=n.new('ShaderNodeEmission'); l.new(mix.outputs[0],em.inputs[0]); l.new(em.outputs[0],out.inputs[0]); s.render.engine='CYCLES'; s.cycles.samples=1; s.render.threads_mode='FIXED'; s.render.threads=2; s.render.bake.margin=0; s.render.bake.use_clear=True; s.render.bake.use_selected_to_active=False; s.render.image_settings.color_depth='8'; bpy.ops.object.bake(type='EMIT')
colour.filepath_raw=str(M/'wolverine_worn_basecolor_4k_v2.png'); colour.file_format='PNG'; colour.save(); colour.pack(); records['basecolor']={'path':colour.filepath_raw,'sha256':hashlib.sha256(Path(colour.filepath_raw).read_bytes()).hexdigest()}
l.new(bs.outputs[0],out.inputs[0]); n.remove(em); l.new(uv.outputs[0],tx.inputs[0]); l.new(tx.outputs[0],bs.inputs['Base Color']); bpy.data.objects.remove(proxy,do_unlink=True)
# Smooth dielectric panes with restrained roughness variation from repaired glass wear.
glass=read_data(M/'wolverine_worn_glass_4k_v1.png')[:,:,0]; rough=read_data(M/'wolverine_worn_roughness_4k_v1.png')[:,:,0]; rgb=read_data(M/'wolverine_worn_basecolor_4k_v2.png')[:,:,:3]; lum=rgb.mean(-1); local=(np.roll(lum,5,0)+np.roll(lum,-5,0)+np.roll(lum,5,1)+np.roll(lum,-5,1))*.25; wear=smooth(.005,.055,np.abs(lum-local)); target=.245+.065*wear
rough=rough*(1-glass)+target*glass; rough_im=save_data(rough,'roughness'); n['Delivered roughness'].image=rough_im
s.cycles.samples=32; s.cycles.use_denoising=True; s['pbr_status']='Wolverine v2: masked smoked-green glass repair; original hull, frame, UV, mesh and normal maps retained.'
assert signature()==original_signature
bpy.context.preferences.filepaths.save_version=0; bpy.ops.wm.save_as_mainfile(filepath=str(D/'wolverine_worn_pbr_v2.blend'))
(W/'validation.json').write_text(json.dumps({'geometry_uv_native_normals_preserved':True,'geometry_signature':original_signature,'parts':len(obs),'glass_regions':len(polys),'maps':records,'glass_roughness_median':float(np.median(rough[glass>.99])),'glass_roughness_range':[float(rough[glass>.99].min()),float(rough[glass>.99].max())],'normal_map':'unchanged v1','imagegen_mode':'built-in','prompt':str(W/'prompt.txt'),'engine_validation':'pending'},indent=2)); print('GLASS_V2_BUILT',flush=True)
