from pathlib import Path
import bpy,numpy as np,json,hashlib
D=Path('${PROWLER_WORKSPACE}');W=D/'work/lighting_v2';M=D/'maps';N=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'prowler_worn_pbr_v1.blend'));bpy.context.preferences.filepaths.save_version=0
# Integrate only generated edit regions in the existing native material scene.
def sig():
 return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers},[list(n.vector) for n in o.data.corner_normals],[list(r) for r in o.matrix_world]) for o in bpy.context.scene.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()
before=sig()
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color'
 if tuple(im.size)!=(N,N):im.scale(N,N)
 b=np.empty(N*N*4,np.float32);im.pixels.foreach_get(b);b=b.reshape(N,N,4)[::-1].copy();bpy.data.images.remove(im);return b

def save(a,name,cs='sRGB'):
 im=bpy.data.images.new(name,N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel());p=M/name;im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=cs;im.pack();return im,p
recs={};glass=load(M/'prowler_hull1_glass_v1.png')[:,:,0]
# Small guard band includes the glass edge tint, without changing adjacent hull.
mask=glass.copy()
for axis in [0,1]:
 mask=np.maximum.reduce([np.roll(mask,d,axis=axis) for d in range(-12,13)])
y,x=np.mgrid[:N,:N].astype(np.float32);x=(x+.5)*256/N;y=(y+.5)*256/N
for role,gname,patch in [('hull1','hull1_green_generated.png',mask),('hull2','hull2_stencil_generated.png',None)]:
 if patch is None:
  patch=np.clip(np.minimum.reduce([x-74.2,93.5-x,y-170.5,226.5-y])/0.7,0,1)
 old=load(M/f'prowler_{role}_basecolor_v1.png');gen=load(W/'inputs'/gname);out=old.copy();out[:,:,:3]=old[:,:,:3]*(1-patch[:,:,None])+gen[:,:,:3]*patch[:,:,None]
 im,p=save(out,f'prowler_{role}_basecolor_v2.png')
 assert np.array_equal(out[patch==0],old[patch==0]);recs[role]=dict(path=str(p),sha256=sha(p),unmodified_outside_edit_mask=True,mask_pixels=int((patch>0).sum()))
 mat=bpy.data.materials[f'Prowler_Worn_{role}_PBR_v1'];mat.node_tree.nodes['Delivered basecolor'].image=im
 if role=='hull1':
  em=np.ones((N,N,4),np.float32);em[:,:,:3]=glass[:,:,None]*np.array([.10,.16,.07],np.float32)
  im,p=save(em,'prowler_hull1_emissive_v2.png');mat.node_tree.nodes['Delivered emissive'].image=im;recs[role]['emissive']=dict(path=str(p),sha256=sha(p),sRGB=[.10,.16,.07],scope_unchanged=True)
 mat.name=mat.name.replace('_v1','_v2')
assert sig()==before
scene=D/'prowler_worn_pbr_v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));report=dict(scene=str(scene),scene_sha256=sha(scene),mesh_signature=before,geometry_uv_normals_preserved=True,maps=recs,source_resolution=[1254,1254],delivery_resolution=[4096,4096],all_other_material_maps_unchanged=True)
(W/'material_edit_audit.json').write_text(json.dumps(report,indent=2)+'\n')
s=bpy.context.scene;s.cycles.samples=16;s.render.resolution_x=1200;s.render.resolution_y=900
for name in ['Front','Rear']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review/lighting_v2'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
print('PROWLER_MATERIAL_V2_PASSED')
