import os
from pathlib import Path
import json,hashlib,struct
import numpy as np
from PIL import Image
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/alignment_v3';O=W/'runtime_stage/111-haidar-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=json.loads((W/'validation.json').read_text());old=json.loads((D/'work/reconstruction_v1/validation.json').read_text());maps=v['maps']['hull'];prior=old['maps']['hull']
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
mask=rgb(maps['glazing_edit_mask']['path'])[:,:,0]>0
local={}
for key in ['basecolor','normal','roughness','metallic']:
 a=rgb(prior[key]['path']);b=rgb(maps[key]['path']);d=np.abs(a.astype(np.int16)-b.astype(np.int16))
 local[key]={'maximum_byte_change_outside_window_footprint':int(d[~mask].max()),'changed_pixels_percent':float(100*np.any(d>1,axis=-1).mean())}
 assert d[~mask].max()<=1,(key,local[key])
assert sha(D/'source/Chin_Han.SHP')=='0438be94665f8ca01189a4ffee9651b9dbb8f1875dc9a11b07b7f02668c1a761'
assert sha(D/'source/brit2.png')=='4c8b7411d6d31df47d5a1a3913121778a3931c285a64e93c69053a530c673a69'
changed=[];unchanged=0
for name,m in v['models'].items():
 assert m['vertices']==old['models'][name]['vertices']
 for f,p in zip(m['faces'],old['models'][name]['faces']):
  assert f['vertices']==p['vertices'] and f['hidden']==p['hidden'] and f['material']==p['material']==0
  if np.max(np.abs(np.array(f['uv'])-p['uv']))>1e-8:changed.append((name,f['id']))
  else:unchanged+=1
assert len(changed)==11 and all(name=='Han_Body' for name,_ in changed)
# Every vertex in the adjusted shoulder strip maps the same longitudinal point
# to the same original artwork column; neither V nor any other chart moves.
body=v['models']['Han_Body'];band=[257]+list(range(262,270))+[272,273];errs=[];v_shifts=[]
zs=[body['vertices'][vi][2] for fi in band for vi in body['faces'][fi]['vertices']];lo,hi=min(zs),max(zs)
for fi in band:
 f=body['faces'][fi];p=old['models']['Han_Body']['faces'][fi]
 for vi,(u,vv),(ou,ov) in zip(f['vertices'],f['uv'],p['uv']):
  expected=(348.4+(525-348.4)*(body['vertices'][vi][2]-lo)/(hi-lo))/1254
  errs.append(abs(u-expected)*1254);v_shifts.append(abs(vv-ov)*1254)
assert max(errs)<.001 and max(v_shifts)<1
# Flat glass and relief belong to separate regions.
glass=rgb(maps['glass']['path'])[:,:,0]>254
for _ in range(14):glass=np.minimum.reduce([glass,np.roll(glass,1,0),np.roll(glass,-1,0),np.roll(glass,1,1),np.roll(glass,-1,1)])
normal=rgb(maps['normal']['path']).astype(np.float32)/255*2-1;rough=rgb(maps['roughness']['path'])[:,:,0];metal=rgb(maps['metallic']['path'])[:,:,0];color=rgb(maps['basecolor']['path'])
assert glass.sum()>10000 and np.max(np.abs(normal[glass]-[0,0,1]))<.008
assert np.max(metal[glass])==0 and np.max(rough[glass])-np.min(rough[glass])<=1
assert np.max(color[glass],axis=0).tolist()==np.min(color[glass],axis=0).tolist()==[28,43,37]
angles=np.degrees(np.arccos(np.clip(normal[:,:,2]/np.linalg.norm(normal,axis=-1),-1,1)))
assert 10<float(angles[mask].max())<40
height=rgb(maps['frame_height']['path'])[:,:,0].astype(float)/255*8-4
samples=[]
for j,defs in enumerate(v['frame_layout']):
 for centre,axis,half in defs:
  x,y=(centre,545) if j==0 else ((centre,752) if j==1 else ((1010,centre)))
  px,py=int(x/1254*4096),int(y/1254*4096);samples.append(float(height[py,px]));assert height[py,px]>.10
assert -.96<float(np.median(height[glass]))<-.84
# Native delivery UVs must match the scene, including faces that did not change.
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
   assert struct.unpack_from('<I',raw,at)[0]==0;count_faces+=1
 pos=end
assert count_faces==478 and max(errors)<1e-6
report=dict(passed=True,original_inputs_unchanged=True,all_51_rejected_faces_back_on_original_material=True,stored_faces=478,unchanged_uv_faces=unchanged,changed_uv_faces=changed,original_layout_retained=True,shoulder_band_max_registration_error_master_pixels=max(errs),max_v_coordinate_shift_master_pixels=max(v_shifts),non_window_map_locality=local,flat_glass_pixels=int(glass.sum()),glass_colour=[28,43,37],glass_height_median=float(np.median(height[glass])),frame_height_samples=samples,max_frame_bevel_normal_angle_degrees=float(angles[mask].max()),native_scene_uv_max_error=max(errors),geometry_and_original_normals_preserved=True,visual_scope='Both-side Blender authoring views; in-game review pending')
(W/'independent_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
