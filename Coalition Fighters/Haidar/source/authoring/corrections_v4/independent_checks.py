import os
from pathlib import Path
import json,hashlib,struct
import numpy as np
from PIL import Image,ImageFilter
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/corrections_v4';O=W/'runtime_stage/111-haidar-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=json.loads((W/'validation.json').read_text());old=json.loads((D/'work/alignment_v3/validation.json').read_text());maps=v['maps']['hull']
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
gm=rgb(maps['glazing_edit_mask']['path'])[:,:,0]>0;pm=rgb(maps['panel_edit_mask']['path'])[:,:,0]>0;bm=rgb(maps['border_edit_mask']['path'])[:,:,0]>0
local={}
for key in ['basecolor','normal','roughness','metallic']:
 a=rgb(old['maps']['hull'][key]['path']);b=rgb(maps[key]['path']);mask=gm.copy()
 if key in ['basecolor','normal']:mask|=pm
 if key=='basecolor':mask|=bm
 d=np.abs(a.astype(np.int16)-b.astype(np.int16));local[key]={'maximum_byte_change_outside_allowed_footprints':int(d[~mask].max()),'changed_pixels_percent':float(100*np.any(d>1,axis=-1).mean())};assert d[~mask].max()<=1,(key,local[key])
 if key=='basecolor':
  # Arrow centre must never be composited from the generated reference.
  ys=slice(int(99/1254*4096),int(133/1254*4096));xs=slice(int(124/1254*4096),int(387/1254*4096));arrow_max=int(d[ys,xs].max());assert arrow_max==0,arrow_max
assert sha(D/'source/Chin_Han.SHP')=='0438be94665f8ca01189a4ffee9651b9dbb8f1875dc9a11b07b7f02668c1a761'
assert sha(D/'source/brit2.png')=='4c8b7411d6d31df47d5a1a3913121778a3931c285a64e93c69053a530c673a69'
changed=[];unchanged=0;patch_count=0
for name,m in v['models'].items():
 assert m['vertices']==old['models'][name]['vertices']
 for f,p in zip(m['faces'],old['models'][name]['faces']):
  assert f['vertices']==p['vertices'] and f['hidden']==p['hidden']
  if np.max(np.abs(np.array(f['uv'])-p['uv']))>1e-8:changed.append((name,f['id']))
  else:unchanged+=1
  if f['material']==1:
   patch_count+=1;assert np.min(f['uv'])>0 and np.max(f['uv'])<1
assert patch_count==7
g=rgb(maps['glass']['path'])[:,:,0];glass=np.asarray(Image.fromarray((g==255).astype(np.uint8)*255).filter(ImageFilter.MinFilter(29)))==255
normal=rgb(maps['normal']['path']).astype(np.float32)/255*2-1;rough=rgb(maps['roughness']['path'])[:,:,0];metal=rgb(maps['metallic']['path'])[:,:,0];color=rgb(maps['basecolor']['path']);height=rgb(maps['frame_height']['path'])[:,:,0].astype(float)/255*8-4
assert glass.sum()>10000 and np.max(np.abs(normal[glass]-[0,0,1]))<.008
assert metal[glass].max()==0 and np.ptp(rough[glass])<=1 and np.ptp(color[glass],axis=0).max()==0
assert len(v['frame_layout'][0])==2 and len(v['frame_layout'][1])==2 and not v['frame_layout'][3] and not v['frame_layout'][4]
samples=[]
for j,defs in enumerate(v['frame_layout']):
 for centre,axis,half in defs:
  x,y=(centre,545) if j==0 else (centre,752);px,py=int(x/1254*4096),int(y/1254*4096);samples.append(float(height[py,px]));assert height[py,px]>.1
for x,y in [(1010,998),(1010,1164)]:
 px,py=int(x/1254*4096),int(y/1254*4096);assert height[py,px]<-.84 and g[py,px]==255
assert -.96<float(np.median(height[glass]))<-.84
# Scene-to-native parity: every LOD0 triangle, including unchanged triangles.
raw=(O/'Chin_Han.SHP').read_bytes();pos=0;part=lod=-1;names=[];errors=[];count_faces=0
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count
 if tag==1:names=[raw[start+i*size:start+i*size+64].split(b'\0')[0].decode().replace(' ','_') for i in range(count)]
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==3 and lod==0:
  for i in range(count):
   at=start+i*size;ids=list(struct.unpack_from('<3I',raw,at+12));vals=struct.unpack_from('<6f',raw,at+24);f=v['models'][names[part]]['faces'][i]
   for k,vi in enumerate(ids):errors.append(float(np.max(np.abs(np.array([vals[k],1-vals[k+3]])-f['uv'][f['vertices'].index(vi)]))))
   assert struct.unpack_from('<I',raw,at)[0]==f['material'];count_faces+=1
 pos=end
assert count_faces==478 and max(errors)<1e-6
assert sha(v['source'])==v['source_sha256']
report=dict(passed=True,original_inputs_and_prior_scene_unchanged=True,stored_faces=478,unchanged_uv_faces=unchanged,changed_uv_faces=changed,face_local_repairs=7,map_locality=local,herringbone_centre_max_byte_difference=arrow_max,flat_glass_pixels=int(glass.sum()),glass_colour=color[glass][0].tolist(),glass_height_median=float(np.median(height[glass])),frame_height_samples=samples,roof_side_alignment=v['roof_side_alignment'],front_and_rear_divider_colour_and_relief_removed=True,native_scene_uv_max_error=max(errors),geometry_and_original_normals_preserved=True,visual_scope='Both-side and roof/belly Blender authoring views; in-game review pending')
(W/'independent_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
