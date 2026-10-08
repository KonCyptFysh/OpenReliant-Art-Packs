
def resolve_record(v):
    if isinstance(v,dict):return {k:resolve_record(x) for k,x in v.items()}
    if isinstance(v,list):return [resolve_record(x) for x in v]
    if isinstance(v,str) and v.startswith('source/'):return str(Path(__file__).resolve().parents[2]/v[7:])
    return v
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
D=Path(__file__).resolve().parents[2];W=D/'recipes/audit_v2';O=D/'exports/openreliant_v2/mods/99-crusader-worn-v1'
r=resolve_record(json.loads((W/'validation.json').read_text()));old=resolve_record(json.loads((D/'recipes/reconstruction_v1/validation.json').read_text()))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGB'))
def erosion(a,n=8):return np.array(Image.fromarray(a.astype(np.uint8)*255).filter(ImageFilter.MinFilter(2*n+1)))>0
allowed=arr(r['audit_changes']['edit_mask']['path'])[:,:,0]>0
outside=[]
for key in ['basecolor','normal','roughness','metallic']:
    a=arr(r['maps'][key]['path']);b=arr(old['maps'][key]['path']);delta=np.abs(a.astype(np.int16)-b.astype(np.int16));outside_delta=int(delta[~allowed].max());assert outside_delta<=1,(key,outside_delta)
    outside.append(dict(map=key,max_byte_difference_outside_repair_mask=outside_delta))
glass=erosion(arr(r['maps']['glass']['path'])[:,:,0]>250)
normal=arr(r['maps']['normal']['path']);rough=arr(r['maps']['roughness']['path'])[:,:,0];metal=arr(r['maps']['metallic']['path'])[:,:,0]
assert glass.sum()>1000
assert np.abs(normal[glass,:2].astype(float)-127.5).max()<=.51 and normal[glass,2].min()==255
assert metal[glass].max()==0 and np.abs(rough[glass].astype(float)/255-.16).max()<.005
orm=arr(O/'orcr1_hull_orm.png');assert (orm[:,:,0]==255).all() and np.array_equal(orm[:,:,1],rough) and np.array_equal(orm[:,:,2],metal)
for family,key in [('orcr1_hull','maps'),('orcr2_collar','repair_maps')]:
    for suffix in ['','_normal','_orm']:assert sha(O/f'{family}{suffix}.png')==sha(O/f'g{family}{suffix}.png')
    for k,suffix in [('basecolor',''),('normal','_normal')]:assert sha(O/f'{family}{suffix}.png')==r[key][k]['sha256']
    data=arr(O/f'{family}_orm.png');assert (data[:,:,0]==255).all() and np.array_equal(data[:,:,1],arr(r[key]['roughness']['path'])[:,:,0]) and np.array_equal(data[:,:,2],arr(r[key]['metallic']['path'])[:,:,0])
    if key=='repair_maps':
        for k in ['basecolor','normal','roughness','metallic']:
            a=arr(r[key][k]['path']);assert np.array_equal(a[:,0],a[:,-1]),k
uvs=r['audit_changes']['collar_shared_edges'];assert len(uvs)==24 and max(x['max_periodic_uv_gap'] for x in uvs)<1e-6
for f in r['models']['Crusader_Body']['faces']:
    if f['material']==2:
        uv=np.array(f['uv']);assert abs(np.cross(uv[1]-uv[0],uv[2]-uv[0]))>1e-7
assert r['audit_changes']['original_geometry_normals_and_prior_uv_layers_preserved']
images=[]
for maps in [r['maps'],r['repair_maps']]:
    for k,m in maps.items():
        p=Path(m['path']);assert sha(p)==m['sha256']
        with Image.open(p) as im:size=im.size;im.verify()
        assert size==((2048,512) if maps is r['repair_maps'] else (4096,4096)),(k,size)
        images.append(dict(file=p.name,dimensions=size,sha256=sha(p)))
assert sha(r['scene'])==r['scene_sha256'] and sha(r['source'])==r['source_sha256']
report=dict(passed=True,maps=images,outside_repair_mask=outside,glass_flat_normals=True,glass_roughness=.16,glass_metallic=0,collar_texture_periodic_edges_identical=True,collar_shared_edges=len(uvs),max_collar_uv_gap=max(x['max_periodic_uv_gap'] for x in uvs),collar_uv_triangles_nonzero=True,orm_channel_packing_verified=True,matching_loadout_maps=True,original_geometry_normals_and_prior_uvs_preserved=True,source_scene_hash_preserved=True,runtime_visual_review='pending_user_review')
(W/'map_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('Map validation passed: local edits, flat glass, exact collar wrap, native UVs, ORM and loadout copies.')
