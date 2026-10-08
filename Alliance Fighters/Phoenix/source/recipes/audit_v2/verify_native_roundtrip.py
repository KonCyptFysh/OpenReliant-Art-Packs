import os
from pathlib import Path
import json,struct,hashlib,numpy as np
from PIL import Image
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v2';O=D/'exports/openreliant_v2/mods/98-phoenix-worn-v1';V1=D/'exports/openreliant_v1/mods/98-phoenix-worn-v1'
def chunks(path):
 data=path.read_bytes();pos=0;part=lod=-1;result=[]
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos)
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  end=pos+6+size*count;result.append((tag,size,count,part,lod,data[pos+6:end]));pos=end
 assert pos==len(data);return result
def facekey(r):return tuple(sorted(struct.unpack_from('<3I',r,12)))
reports=[]
for name in ['USPF_Phx.SHP','t_USPF_Phx.SHP','Phoenix_gun.SHP']:
 orig=chunks(D/'source'/name);new=chunks(O/name);prev=chunks(V1/name);expected=json.loads((W/(name+'.exported_faces.json')).read_text());lookup={(f['part'],tuple(sorted(f['vertex_ids']))):f for f in expected}
 total=unchanged=changed=0;error=0
 assert len(orig)==len(new)==len(prev)
 for a,b,c in zip(orig,new,prev):
  assert a[:5]==b[:5]==c[:5];tag,size,count,part,lod,old=a;payload=b[-1]
  if tag==3 and lod==0 and part<3:
   oldfaces={facekey(old[i*size:(i+1)*size]):old[i*size:(i+1)*size] for i in range(count)}
   prevfaces={facekey(c[-1][i*size:(i+1)*size]):c[-1][i*size:(i+1)*size] for i in range(count)}
   for i in range(count):
    r=payload[i*size:(i+1)*size];key=facekey(r);oldr=oldfaces[key];pr=prevfaces[key]
    assert r[:12]==oldr[:12] and r[48:72]==oldr[48:72]
    assert r[:24]==pr[:24] and r[48:]==pr[48:]
    f=lookup[(part,key)];ids=struct.unpack_from('<3I',r,12);uv=struct.unpack_from('<6f',r,24)
    for j,k in enumerate(ids):
     want=f['uv'][f['vertex_ids'].index(k)];error=max(error,abs(uv[j]-want[0]),abs(1-uv[j+3]-want[1]))
    changed+=r[24:48]!=pr[24:48];total+=1
  elif tag==6 and lod==0:
   assert payload==c[-1]
   for i in range(count):
    oldname=old[i*size:(i+1)*size].split(b'\0')[0].lower()
    if oldname in [b'yank_4',b't_yank_4']:assert payload[i*size:(i+1)*size].split(b'\0')[0]==b'orpx1_hull'
    else:assert payload[i*size:(i+1)*size]==old[i*size:(i+1)*size]
  else:assert old==payload==c[-1];unchanged+=1
 assert total==494 and changed==4 and error<1e-6
 reports.append({'file':name,'matched_lod0_faces':total,'changed_uv_faces_since_v1':changed,'max_corner_uv_error':error,'unchanged_other_chunks':unchanged,'geometry_normals_attachments_animation_damage_flags_and_lower_lods_preserved':True})
mask=np.asarray(Image.open(D/'maps/phoenix_worn_glass_4k_v1.png').convert('RGB'))[:,:,0];outside=mask==0;core=mask==255;maps=[]
for key in ['basecolor','normal','roughness','metallic']:
 a=np.asarray(Image.open(D/f'maps/phoenix_worn_{key}_4k_v1.png').convert('RGB'));b=np.asarray(Image.open(D/f'maps/phoenix_worn_{key}_4k_v2.png').convert('RGB'))
 # Quantized mask pixels below 1/255 can produce one least-significant-level
 # rounding change along the antialiased pane boundary, not beyond it.
 diff=np.abs(b.astype(int)-a.astype(int));changed=diff.max(-1)>1
 assert not np.any(changed&outside)
 maps.append({'map':key,'changed_pixels_outside_glass_mask_over_one_level':int(np.count_nonzero(changed&outside)),'glass_core_min':b[core].min(0).tolist(),'glass_core_max':b[core].max(0).tolist()})
(W/'native_roundtrip.json').write_text(json.dumps(reports,indent=2)+'\n');(W/'map_locality.json').write_text(json.dumps(maps,indent=2)+'\n')
print(json.dumps({'native':reports,'map_locality':maps},indent=2))
