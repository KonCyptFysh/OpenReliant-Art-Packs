import os
from pathlib import Path
import bpy,json,hashlib,numpy as np
D=Path(os.environ['BASILISK_WORKSPACE']).resolve()
W=D/'work/nose_finish_v2';M=D/'maps';R=D/'review/nose_finish_v2';R.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=D/'basilisk_worn_pbr_v1.blend';prior=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
def signature():
    return sha_data({o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],normals=[list(n.vector) for n in o.data.corner_normals],uv={u.name:[list(x.uv) for x in u.data] for u in o.data.uv_layers},matrix=[list(r) for r in o.matrix_world]) for o in s.objects if o.type=='MESH'})
def sha_data(data):return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before=signature();N=1254
y,x=np.mgrid[:N,:N].astype(np.float32);X=x+.5;Y=y+.5
def smooth(a,b,t):
    f=np.clip((t-a)/(b-a),0,1);return f*f*(3-2*f)
def polygon(points):
    p=np.asarray(points,np.float32);d=np.full((N,N),1e6,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
    if abs(area)<1e-4:return np.zeros((N,N),np.float32)
    for a,b in zip(p,np.roll(p,-1,axis=0)):
        v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(Y-a[1])-v[1]*(X-a[0]))/max(np.linalg.norm(v),1e-8))
    return smooth(-1.5,2,d)
faces={'Basalisk':list(range(178,189))+[195]+list(range(208,219))+[225]+list(range(226,230)), 'Basalisk_Cpit':list(range(14,19))+list(range(22,27))+list(range(32,48))}
scope=np.zeros((N,N),np.float32)
for name,ids in faces.items():
    obj=bpy.data.objects[name];uv=obj.data.uv_layers['Basilisk_Delivery_UV_v1']
    for idx in ids:
        p=obj.data.polygons[idx];q=[(uv.data[i].uv.x*N,(1-uv.data[i].uv.y)*N) for i in p.loop_indices]
        scope=np.maximum(scope,polygon(q))
OUT=4096
def rgba(path,scale=None):
    im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
    if scale:im.scale(scale,scale)
    w,h=im.size;v=np.empty(w*h*4,np.float32);im.pixels.foreach_get(v);bpy.data.images.remove(im)
    return v.reshape(h,w,4)[::-1].copy()
def upscale(a):
    im=bpy.data.images.new('Nose control temporary',N,N,alpha=False);im.colorspace_settings.name='Non-Color';data=np.ones((N,N,4),np.float32);data[:,:,:3]=a[:,:,None];im.pixels.foreach_set(np.ascontiguousarray(data[::-1]).ravel());im.scale(OUT,OUT);v=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(v);bpy.data.images.remove(im);return v.reshape(OUT,OUT,4)[::-1,:,0].copy()
scope=upscale(scope)
seal=rgba(M/'basilisk_hull_seal_v1.png')[:,:,0];structure=rgba(M/'basilisk_hull_structure_v1.png')[:,:,0];flat=rgba(M/'basilisk_hull_flat_graphics_v1.png')[:,:,0];panels=rgba(M/'basilisk_hull_panels_v1.png')[:,:,0]
control=scope*(1-np.maximum.reduce([seal,structure,flat]))
paint=rgba(M/'basilisk_hull_paint_v1.png')[:,:,0]
oldbase=rgba(M/'basilisk_hull_basecolor_v1.png');newbase=rgba(M/'basilisk_nose_generated_v2.png',OUT)
# The generated edit is applied only as a local material layer. Protect the
# exact existing dark seam cores and markings; all other atlas regions retain
# their original samples.
basefactor=.72*control*smooth(.12,.27,oldbase[:,:,:3].max(-1))*(1-panels)
base=oldbase.copy();base[:,:,:3]=oldbase[:,:,:3]*(1-basefactor[:,:,None])+newbase[:,:,:3]*basefactor[:,:,None]
assert np.array_equal(base[basefactor==0],oldbase[basefactor==0])
oldrough=rgba(M/'basilisk_hull_roughness_v1.png')[:,:,0]
roughfactor=control*(1-panels)
target=.33+.07*paint
rough=oldrough*(1-roughfactor)+target*roughfactor
oldnormal=rgba(M/'basilisk_hull_normal_v1.png')[:,:,:3];normal=oldnormal*2-1
normal[:,:,:2]*=(1-.55*control[:,:,None]);normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-8);normal=normal*.5+.5
normal[control==0]=oldnormal[control==0]
records={}
def save(a,key):
    data=np.ones((OUT,OUT,4),np.float32);data[:,:,:3]=a[:,:,:3] if a.ndim==3 else a[:,:,None]
    im=bpy.data.images.new('Basilisk hull '+key+' v2',OUT,OUT,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(data[::-1]).ravel());p=M/('basilisk_hull_'+key+'_v2.png');im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im)
    records[key]=dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT]);im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();return im
images={k:save(a,k) for k,a in [('basecolor',base),('roughness',rough),('normal',normal),('nose_mask',control)]}
for mat in list(bpy.data.materials):
    if not mat.name.startswith('Basilisk_Worn_') or not mat.use_nodes:continue
    mat.name='Basilisk_Worn_hull_PBR_v2'
    for key in ['basecolor','roughness','normal']:mat.node_tree.nodes['Delivered '+key].image=images[key]
    tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.name='Authoring nose finish mask';tx.label='Nose only: smoother skin, panel gaps preserved';tx.image=images['nose_mask']
    mat['nose_bare_surface_roughness']=.33;mat['nose_painted_surface_roughness']=.40;mat['nose_relief_strength']=.45;mat['nose_face_selection']=json.dumps(faces)
assert signature()==before
scene=D/'basilisk_worn_pbr_v2.blend';bpy.context.preferences.filepaths.save_version=0;s.render.resolution_x=1440;s.render.resolution_y=1080;s.cycles.samples=24;bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==prior
oldreport=json.loads((D/'work/reconstruction_v1/validation.json').read_text());oldmaps=oldreport['maps']['hull'];maps={**oldmaps,**records}
report=dict(source=str(src),source_sha256=prior,scene=str(scene),scene_sha256=sha(scene),geometry_signature=before,geometry_normals_uvs_unchanged=True,base_colour_outside_nose_unchanged=True,nose_face_selection=faces,maps={'hull':maps},material_changes=dict(bare_roughness=.33,paint_roughness=.4,normal_relief_scale=.45,base_imagegen_layer_opacity=.72),protected_regions=['window glazing and seals','vents and radiator structures','flat graphics','dark panel seam cores'],nose_texels=int((control>.5).sum()),roughness_before_median=float(np.median(oldrough[roughfactor>.9])),roughness_after_median=float(np.median(rough[roughfactor>.9])),runtime_review='pending_user_review')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BASILISK_NOSE_FINISH_SAVED',json.dumps(report['material_changes']),flush=True)
for name in ['Front','Opposite','Cockpit']:
    s.camera=bpy.data.objects[name];s.render.filepath=str(R/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
