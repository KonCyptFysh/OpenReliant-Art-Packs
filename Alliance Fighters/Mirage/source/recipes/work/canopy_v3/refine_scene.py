from pathlib import Path
import bpy,numpy as np,json,hashlib,shutil
D=Path(__file__).resolve().parents[2];W=D/'work/canopy_v3';M=D/'maps/canopy_v3';prior=json.loads((W/'prior_project_state.json').read_text());bpy.ops.wm.open_mainfile(filepath=prior['latest_scene']);s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];bpy.context.view_layer.update();N=4096

def signature():return hashlib.sha256(json.dumps({o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(q.vector) for q in o.data.corner_normals],{u.name:[list(q.uv) for q in u.data] for u in o.data.uv_layers},[list(r) for r in o.matrix_world]) for o in obs},sort_keys=True).encode()).hexdigest()
sig=signature();assert sig==json.loads((D/'work/refinement_v2/validation.json').read_text())['geometry_signature'];records={k:dict(v) for k,v in prior['maps'].items()}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path,channels=1):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color';assert list(im.size)==[N,N];a=np.empty(N*N*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(N,N,4)[::-1,:,:channels].copy();bpy.data.images.remove(im);return a if channels>1 else a[:,:,0]
def save(a,kind):
 data=np.ones((N,N,4),np.float32);data[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new('Mirage v3 '+kind,N,N,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(data[::-1]).ravel());im.filepath_raw=str(M/f'mirage_worn_{kind}_4k_v3.png');im.file_format='PNG';s.render.image_settings.color_depth='16';im.save();path=im.filepath_raw;bpy.data.images.remove(im);records[kind]={'path':path,'sha256':sha(path)};return path
oldglass=load(prior['maps']['glass']['path']);extension=load(M/'canopy_glass_extension_4k_v3.png');glass=np.maximum(oldglass,extension);delta=np.clip((glass-oldglass)/np.maximum(1-oldglass,1e-6),0,1);active=delta>0;stats={'glass_extension_pixels':int(active.sum()),'map_outside_extension_changed_pixels':{}}
save(glass,'glass')
for kind,target in [('metallic',0.),('roughness',.144),('specular',.5),('coat',.24),('height',24/36),('normal',None)]:
 a=load(prior['maps'][kind]['path'],3 if kind=='normal' else 1);b=a.copy()
 if kind=='normal':
  vectors=a[active]*2-1;vectors=vectors*(1-delta[active,None])+np.array([0,0,1],np.float32)*delta[active,None];vectors/=np.linalg.norm(vectors,axis=-1,keepdims=True);b[active]=vectors*.5+.5
 else:b[active]=a[active]*(1-delta[active])+target*delta[active]
 path=save(b,kind);check=load(path,3 if kind=='normal' else 1);oldq=np.rint(a*65535).astype(np.uint16);newq=np.rint(check*65535).astype(np.uint16)
 outside=int(np.count_nonzero(np.any(oldq[~active]!=newq[~active],axis=1))) if kind=='normal' else int(np.count_nonzero(oldq[~active]!=newq[~active]));stats['map_outside_extension_changed_pixels'][kind]=outside;assert outside==0,(kind,outside)
 del a,b,check,oldq,newq
base=M/'mirage_worn_basecolor_4k_v3.png';records['basecolor']={'path':str(base),'sha256':sha(base)}
oldmat=obs[0].data.materials[0];mat=oldmat.copy();mat.name='Mirage_Worn_PBR_v3'
for kind in ['basecolor','normal','metallic','roughness','specular','coat']:
 im=bpy.data.images.load(records[kind]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color';im.pack();mat.node_tree.nodes['Delivered '+kind].image=im
for o in obs:
 for i,m in enumerate(o.data.materials):
  if m==oldmat:o.data.materials[i]=mat
assert signature()==sig
s['pbr_status']='Mirage v3: original-style flush front glazing restored; generated extra trim removed locally. Geometry, UVs and structural relief preserved.';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'mirage_worn_pbr_v3.blend'))
r={'source_scene':prior['latest_scene'],'scene':str(D/'mirage_worn_pbr_v3.blend'),'geometry_signature':sig,'geometry_uv_native_normals_preserved':True,'maps':records,'material_statistics':stats,'height_decode':'height PNG * 36 - 24; baked into tangent normal, no displacement','parts':len(obs),'stored_LOD0_triangles':sum(len(o.data.polygons) for o in obs),'intact_visible_LOD0_triangles':sum(p.material_index==0 for o in obs for p in o.data.polygons),'engine_validation':'not_tested','local_edit_validation':json.loads((W/'local_edit_validation.json').read_text()),'imagegen_prompt':str(W/'texture_prompt.txt')};(W/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('CANOPY_V3_SAVED',stats,flush=True)
