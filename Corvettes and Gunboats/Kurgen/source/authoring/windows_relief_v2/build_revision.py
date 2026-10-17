from pathlib import Path
import bpy, numpy as np, json, hashlib, math

D=Path('${KURGEN_WORKSPACE}')
W=D/'work/windows_relief_v2'; M=D/'maps/windows_relief_v2'; V=D/'review/windows_relief_v2'
N=1254; OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d): p.write_text(json.dumps(d,indent=2)+'\n')
def signature():
    rows=[]
    for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name):
        m=o.data; rows.append(dict(name=o.name,matrix=[list(x) for x in o.matrix_world],vertices=[list(v.co) for v in m.vertices],faces=[(list(p.vertices),p.material_index) for p in m.polygons],normals=[list(x.vector) for x in m.corner_normals],uvs={u.name:[list(v.uv) for v in u.data] for u in m.uv_layers},hidden=o.hide_render))
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
def load_raw(path,size=None):
    im=bpy.data.images.load(str(path),check_existing=False); im.colorspace_settings.name='Non-Color'
    if size and tuple(im.size)!=(size,size): im.scale(size,size)
    w,h=im.size; a=np.empty(w*h*4,np.float32); im.pixels.foreach_get(a); a=a.reshape(h,w,4)[::-1,:,:3].copy(); bpy.data.images.remove(im); return a
def upscale(a,size=OUT):
    h,w=a.shape[:2]; im=bpy.data.images.new('temporary resize',width=w,height=h,alpha=False,float_buffer=True); im.colorspace_settings.name='Non-Color'
    q=np.ones((h,w,4),np.float32); q[:,:,:3]=a if a.ndim==3 else a[:,:,None]; im.pixels.foreach_set(np.ascontiguousarray(q[::-1]).ravel()); im.scale(size,size)
    b=np.empty(size*size*4,np.float32); im.pixels.foreach_get(b); b=b.reshape(size,size,4)[::-1,:,:3].copy(); bpy.data.images.remove(im); return b
records={}
def save(a,key,color=False):
    if a.shape[:2]!=(OUT,OUT): a=upscale(a)
    if a.ndim==2:a=np.repeat(a[:,:,None],3,axis=2)
    if key=='normal':
        v=a*2-1; v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8); a=v*.5+.5
    im=bpy.data.images.new('Kurgen v2 '+key,OUT,OUT,alpha=False); im.colorspace_settings.name='Non-Color'; q=np.ones((OUT,OUT,4),np.float32); q[:,:,:3]=a; im.pixels.foreach_set(np.ascontiguousarray(q[::-1]).ravel()); p=M/('kurgen_hull_'+key+'_v2.png'); im.filepath_raw=str(p); im.file_format='PNG'; im.save(); bpy.data.images.remove(im)
    records[key]=dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT]); im=bpy.data.images.load(str(p),check_existing=False); im.colorspace_settings.name='sRGB' if color else 'Non-Color'; return im

src=D/'kurgen_worn_pbr_v1.blend'; srcsha=sha(src); bpy.ops.wm.open_mainfile(filepath=str(src)); before=signature(); s=bpy.context.scene
regions=json.loads((D/'work/reconstruction_v1/regions.json').read_text())['regions']['hull']
yy,xx=np.mgrid[:N,:N].astype(np.float32); X=(xx+.5)*256/N; Y=(yy+.5)*256/N
def smooth(a,b,z):
    t=np.clip((z-a)/(b-a),0,1); return t*t*(3-2*t)
def capsule(a,b,r):
    v=np.subtract(b,a); t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1); return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def poly(points):
    p=np.array(points); inside=np.zeros((N,N),bool); d=np.full((N,N),1e6,np.float32)
    for a,b in zip(p,np.roll(p,-1,axis=0)):
        d=np.minimum(d,-capsule(a,b,0)); inside^=((a[1]>Y)!=(b[1]>Y))&(X<(b[0]-a[0])*(Y-a[1])/(b[1]-a[1]+1e-10)+a[0])
    return np.where(inside,d,-d)

# Structural depth only: no luminance-derived bumps from worn paint or decals.
h=np.zeros((N,N),np.float32); flat=h.copy(); structure=h.copy(); fins=h.copy(); pan=h.copy()
for a,b,c,d in regions['flat']: flat=np.maximum(flat,smooth(0,.4,poly([[a,b],[c,b],[c,d],[a,d]])))
for a,b,r in regions['slots']:
    dist=capsule(a,b,r); mask=smooth(0,.4,dist); h-=.45*2.8*smooth(0,.8,dist); structure=np.maximum(structure,mask)
for cx,cy,r in regions['circles']:
    dist=r-np.hypot(X-cx,Y-cy); mask=smooth(0,.4,dist); h=h*(1-mask)-.3*2.8*smooth(0,.8,dist)*mask; structure=np.maximum(structure,mask)
for rad in regions['radiators']:
    dist=poly(rad['polygon']); mask=smooth(0,.35,dist); pos=X if rad['axis']=='x' else Y
    rib=np.maximum.reduce([1-smooth(.15,.4,np.abs(pos-c)) for c in rad['centres']])*smooth(.5,1,dist)
    h=h*(1-mask)+(-.4*2.8*smooth(0,.8,dist)+.22*3.0*rib)*mask; structure=np.maximum(structure,mask); fins=np.maximum(fins,rib)
for path in regions['panels']:
    for a,b in zip(path,path[1:]): pan=np.maximum(pan,smooth(0,.25,capsule(a,b,.42)))
pan*=1-np.maximum(flat,structure); h-=.12*4.2*pan; h*=1-flat

# Apertures traced against the accepted atlas; generated changes outside them are discarded.
# Rectangular banks include only the glass and their existing dark seals.
windows=[
    dict(name='upper_bank',shape='capsule',a=[176,14.1],b=[238,14.1],radius=2.65),
    dict(name='lower_bank',shape='capsule',a=[176,44.1],b=[238,44.1],radius=2.65),
    dict(name='long_bank_a',shape='capsule',a=[68,82.4],b=[180,82.4],radius=3.35),
    dict(name='long_bank_b',shape='capsule',a=[68,95.4],b=[180,95.4],radius=3.35),
    dict(name='end_bank',shape='rect',box=[39.3,103.0,44.8,122.3]),
    dict(name='side_bank_long',shape='rect',box=[98.2,131.0,104.1,167.6]),
    dict(name='side_bank_short',shape='rect',box=[98.2,172.0,104.1,180.6]),
    dict(name='short_bridge_bank',shape='capsule',a=[67.2,177.5],b=[88.0,177.5],radius=2.8),
    dict(name='forward_bank_short',shape='rect',box=[184.9,195.7,190.7,207.0]),
    dict(name='forward_bank_long',shape='rect',box=[184.9,212.2,191.0,236.8])]
aperture=h*0; distance=np.full((N,N),-1000,np.float32)
for win in windows:
    if win['shape']=='capsule': dist=capsule(win['a'],win['b'],win['radius'])
    else:
        a,b,c,d=win['box']; dist=np.minimum.reduce([X-a,c-X,Y-b,d-Y])
    distance=np.maximum(distance,dist); aperture=np.maximum(aperture,smooth(-.12,.15,dist))
art=load_raw(M/'window_artwork_generated.png',N)
# Colour plus spatial gate keeps metal mullions, black seals, stars and lamps non-emissive.
warm=smooth(.055,.18,art[:,:,0]-art[:,:,2])*smooth(.09,.22,art[:,:,1])*smooth(.13,.30,art[:,:,0])
glass=warm*smooth(.22,.66,distance)
# Keep the frame at the hull surface and sink panes behind it, with a smooth bevel.
window_height=-.80*glass-.10*smooth(-.10,.40,distance)
h=h*(1-aperture)+window_height*aperture
dy,dx=np.gradient(h); normal=np.stack((-dx,dy,np.ones_like(h)),-1); normal/=np.linalg.norm(normal,axis=-1,keepdims=True)

oldbase=load_raw(D/'maps/kurgen_hull_basecolor_v1.png')
newart=upscale(art); mask4=upscale(aperture)[:,:,0]; g4=upscale(glass)[:,:,0]
# Lower the unlit albedo of the window artwork; the separate emission supplies its interior light.
base=oldbase*(1-mask4[:,:,None])+newart*(1-.36*g4[:,:,None])*mask4[:,:,None]
assert np.array_equal(base[mask4==0],oldbase[mask4==0])
emission=art*glass[:,:,None]*.83
rough=load_raw(D/'maps/kurgen_hull_roughness_v1.png')[:,:,0]; metal=load_raw(D/'maps/kurgen_hull_metallic_v1.png')[:,:,0]
rough=rough*(1-g4)+.31*g4; metal*=1-g4
maps={'basecolor':save(base,'basecolor',True),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic'),'emissive':save(emission,'emissive',True)}
for key,a in [('height',(h+4)/8),('window_aperture',aperture),('window_glass',glass),('flat_graphics',flat),('panels',pan),('structure',structure)]: bpy.data.images.remove(save(a,key))
dump(W/'window_regions.json',dict(coordinate_size=[256,256],windows=windows,policy='Only these aperture pixels may change in the accepted hull albedo; no other base-colour editing. Frames excluded from emission.',height_encoding='height = (stored * 8) - 4',panel_depth_multiplier=4.2,mechanical_recess_multiplier=2.8,radiator_rib_multiplier=3.0))

mat=next(m for m in bpy.data.materials if m.name.startswith('Kurgen_Worn_hull_PBR'))
mat.name='Kurgen_Worn_hull_PBR_v2'; nodes=mat.node_tree.nodes; links=mat.node_tree.links; bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED'); uv=next(n for n in nodes if n.type=='UVMAP')
for key,im in maps.items():
    im.pack(); tx=nodes.get('Delivered '+key)
    if not tx:tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;links.new(uv.outputs[0],tx.inputs[0])
    tx.image=im;tx.extension='REPEAT'
    if key=='emissive':links.new(tx.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
assert signature()==before and sha(src)==srcsha
bpy.context.preferences.filepaths.save_version=0; s.camera=bpy.data.objects['Front']; s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=24
scene=D/'kurgen_worn_pbr_v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
report=dict(source_scene=str(src),source_sha256=srcsha,scene=str(scene),scene_sha256=sha(scene),mesh_signature=before,original_scene_preserved=True,geometry_uv_normals_mounts_unchanged=True,turret_materials_unchanged=True,basecolor_preserved_outside_windows=True,window_atlas_regions=len(windows),maps=records,normal_depth=dict(panel_seams=4.2,machinery_recesses=2.8,radiator_ribs=3.0),emission='Warm amber panes only; black hull, seals and frame mask; linear engine emission strength 1',runtime_visual_review='pending_user')
dump(W/'validation.json',report)
for name in ['Front','Opposite','Belly','Rear']:
    s.camera=bpy.data.objects[name];s.render.filepath=str(V/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
# Dark-side proof, with no lights or world illumination. Not an engine capture.
for o in s.objects:
    if o.type=='LIGHT':o.hide_render=True
if s.world and s.world.use_nodes:
    for n in s.world.node_tree.nodes:
        if n.type=='BACKGROUND':n.inputs['Strength'].default_value=0
s.camera=bpy.data.objects['Front'];s.render.filepath=str(V/'emissive_dark.png');bpy.ops.render.render(write_still=True)
print('KURGEN_WINDOWS_RELIEF_V2_SAVED',flush=True)
