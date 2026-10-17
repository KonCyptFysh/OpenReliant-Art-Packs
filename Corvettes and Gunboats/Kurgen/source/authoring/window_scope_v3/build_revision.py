from pathlib import Path
import bpy, numpy as np, json, hashlib, math

D=Path('${KURGEN_WORKSPACE}')
W=D/'work/window_scope_v3'; M=D/'maps/window_scope_v3'; V=D/'review/window_scope_v3'
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
    im=bpy.data.images.new('Kurgen v3 '+key,OUT,OUT,alpha=False); im.colorspace_settings.name='Non-Color'; q=np.ones((OUT,OUT,4),np.float32); q[:,:,:3]=a; im.pixels.foreach_set(np.ascontiguousarray(q[::-1]).ravel()); p=M/('kurgen_hull_'+key+'_v3.png'); im.filepath_raw=str(p); im.file_format='PNG'; im.save(); bpy.data.images.remove(im)
    records[key]=dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT]); im=bpy.data.images.load(str(p),check_existing=False); im.colorspace_settings.name='sRGB' if color else 'Non-Color'; return im

src=D/'kurgen_worn_pbr_v2.blend'; srcsha=sha(src); bpy.ops.wm.open_mainfile(filepath=str(src)); before=signature(); s=bpy.context.scene
protected={}
for o in s.objects:
    if o.type=='MESH':
        protected[o.name]=dict(matrix=[list(r) for r in o.matrix_world],vertices=[list(v.co) for v in o.data.vertices],normals=[list(n.vector) for n in o.data.corner_normals],faces=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons],uvs={u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers})
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
# Only the four side strips explicitly highlighted by the user. The front pair
# needs a separate 512-square material because its UVs are reused on the rear.
original_windows=json.loads((D/'work/windows_relief_v2/window_regions.json').read_text())['windows']
allowed_names=['side_bank_long','side_bank_short','forward_bank_short','forward_bank_long']
windows=[w for w in original_windows if w['name'] in allowed_names]
assert len(windows)==4
# Restore long vents with lengthwise ribs, rather than the rejected window mullions.
vent_ribs=np.zeros_like(h)
for cy,a,b,centres in [(14.1,176,238,[14.1]),(44.1,176,238,[44.1]),(82.4,68,180,[81.0,83.3]),(95.4,68,180,[94.0,96.3])]:
    width=2.65 if a==176 else 3.35
    interior=smooth(.75,1.25,capsule([a,cy],[b,cy],width))
    ribs=np.maximum.reduce([1-smooth(.17,.46,np.abs(Y-v)) for v in centres])*interior
    h+=.66*ribs;vent_ribs=np.maximum(vent_ribs,ribs)
aperture=h*0; distance=np.full((N,N),-1000,np.float32)
for win in windows:
    if win['shape']=='capsule': dist=capsule(win['a'],win['b'],win['radius'])
    else:
        a,b,c,d=win['box']; dist=np.minimum.reduce([X-a,c-X,Y-b,d-Y])
    distance=np.maximum(distance,dist); aperture=np.maximum(aperture,smooth(-.12,.15,dist))
art=load_raw(D/'maps/windows_relief_v2/window_artwork_generated.png',N)
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
for key,a in [('height',(h+4)/8),('window_aperture',aperture),('window_glass',glass),('flat_graphics',flat),('panels',pan),('structure',structure),('vent_ribs',vent_ribs)]: bpy.data.images.remove(save(a,key))
dump(W/'window_regions.json',dict(coordinate_size=[256,256],windows=windows,policy='Only these aperture pixels may change in the accepted hull albedo; no other base-colour editing. Frames excluded from emission.',height_encoding='height = (stored * 8) - 4',panel_depth_multiplier=4.2,mechanical_recess_multiplier=2.8,radiator_rib_multiplier=3.0))

mat=next(m for m in bpy.data.materials if m.name.startswith('Kurgen_Worn_hull_PBR'))
mat.name='Kurgen_Worn_hull_PBR_v3'; nodes=mat.node_tree.nodes; links=mat.node_tree.links; bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED'); uv=next(n for n in nodes if n.type=='UVMAP')
for key,im in maps.items():
    im.pack(); tx=nodes.get('Delivered '+key)
    if not tx:tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;links.new(uv.outputs[0],tx.inputs[0])
    tx.image=im;tx.extension='REPEAT'
    if key=='emissive':links.new(tx.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
# Preserve the front window pair without lighting their reused rear texture patch.
selection=json.loads((W/'bridge_face_selection.json').read_text());crop=selection['atlas_crop']
bridge_maps={};bridge_records={}
for key in ['basecolor','normal','roughness','metallic','emissive']:
    raw=load_raw(D/'maps/windows_relief_v2'/('kurgen_hull_'+key+'_v2.png'))
    pixels=raw[crop[1]*16:crop[3]*16,crop[0]*16:crop[2]*16].copy();assert pixels.shape==(512,512,3)
    im=bpy.data.images.new('Kurgen bridge '+key,512,512,alpha=False);im.colorspace_settings.name='Non-Color'
    rgba=np.ones((512,512,4),np.float32);rgba[:,:,:3]=pixels;im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    path=M/('kurgen_bridge_'+key+'_v3.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();bpy.data.images.remove(im)
    im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='sRGB' if key in ['basecolor','emissive'] else 'Non-Color';im.pack();bridge_maps[key]=im
    bridge_records[key]=dict(path=str(path),sha256=sha(path),dimensions=[512,512])
bridge=mat.copy();bridge.name='Kurgen_Front_Bridge_Windows_v3';patchuv='Kurgen_Front_Bridge_UV_v3'
for key,im in bridge_maps.items():bridge.node_tree.nodes['Delivered '+key].image=im
for node in bridge.node_tree.nodes:
    if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=patchuv
body=next(o for o in s.objects if o.type=='MESH' and o.get('native_part_index')==0)
assert len(body.data.polygons)==388
uv=body.data.uv_layers.new(name=patchuv,do_init=True);old_uv=body.data.uv_layers['Kurgen_Delivery_UV_v1']
for a,b in zip(uv.data,old_uv.data):a.uv=b.uv
newmatindex=len(body.data.materials);body.data.materials.append(bridge)
for fi in selection['selected_faces_by_lod'][0]:
    f=body.data.polygons[fi];f.material_index=newmatindex
    for li in f.loop_indices:
        u,v=old_uv.data[li].uv;uv.data[li].uv=((u*256-crop[0])/32,1-((1-v)*256-crop[1])/32)
body.data.uv_layers.active=old_uv;old_uv.active_render=True
for o in (o for o in s.objects if o.type=='MESH'):
    old=protected[o.name];m=o.data
    assert old['matrix']==[list(r) for r in o.matrix_world] and old['vertices']==[list(v.co) for v in m.vertices]
    assert old['normals']==[list(n.vector) for n in m.corner_normals] and old['faces']==[list(p.vertices) for p in m.polygons]
    for name,uvs in old['uvs'].items():assert uvs==[list(v.uv) for v in m.uv_layers[name].data]
    changed=[i for i,(a,b) in enumerate(zip(old['materials'],[p.material_index for p in m.polygons])) if a!=b]
    assert changed==(selection['selected_faces_by_lod'][0] if o==body else [])
assert sha(src)==srcsha

bpy.context.preferences.filepaths.save_version=0; s.camera=bpy.data.objects['Front']; s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=24
scene=D/'kurgen_worn_pbr_v3.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
report=dict(source_scene=str(src),source_sha256=srcsha,scene=str(scene),scene_sha256=sha(scene),mesh_signature=before,original_scene_preserved=True,geometry_normals_mounts_and_original_uv_layers_unchanged=True,front_bridge_uv_layer_added=True,bridge_selection=selection,bridge_maps=bridge_records,turret_materials_unchanged=True,basecolor_preserved_outside_windows=True,window_atlas_regions=len(windows),restored_regions=[w['name'] for w in original_windows if w['name'] not in allowed_names],bridge_front_exception='Front faces only use their own 512-square crop; reused rear faces stay non-emissive',maps=records,normal_depth=dict(panel_seams=4.2,machinery_recesses=2.8,radiator_ribs=3.0),emission='Warm amber panes only; black hull, seals and frame mask; linear engine emission strength 1',runtime_visual_review='pending_user')
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
print('KURGEN_WINDOW_SCOPE_V3_SAVED',flush=True)
