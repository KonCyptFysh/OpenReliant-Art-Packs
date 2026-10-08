import os
from pathlib import Path
import json,struct,hashlib
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v7';O=D/'exports/openreliant_v7/mods/98-phoenix-worn-v1';previous=D/'exports/openreliant_v6/mods/98-phoenix-worn-v1';r=json.loads((W/'validation.json').read_text());want_changes=len(r['audit_changes']['surface_faces'])
def chunks(path):
 data=path.read_bytes();pos=0;part=lod=-1;out=[]
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos)
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  end=pos+6+size*count;out.append((tag,size,count,part,lod,data[pos+6:end]));pos=end
 assert pos==len(data);return out
def key(r):return tuple(sorted(struct.unpack_from('<3I',r,12)))
reports=[]
for name in ['USPF_Phx.SHP','t_USPF_Phx.SHP','Phoenix_gun.SHP']:
 orig=chunks(D/'source'/name);prev=chunks(previous/name);new=chunks(O/name);expected=json.loads((W/(name+'.exported_faces.json')).read_text());lookup={(f['part'],tuple(sorted(f['vertex_ids']))):f for f in expected};assert len(orig)==len(prev)==len(new);total=unchanged=changed=materials=0;error=0;slots={}
 for a,b,c in zip(orig,new,prev):
  tag,size,count,part,lod,old=a;assert a[:2]==b[:2]==c[:2] and a[3:5]==b[3:5]==c[3:5];payload=b[-1]
  if tag==6 and lod==0:
   added=part in [1,2];assert b[2]==count+int(added) and payload[:len(c[-1])]==c[-1]
   if added:assert payload[-size:].split(b'\0')[0]==b'orpx7_fix'
   slots[part]=b[2];continue
  assert a[2]==b[2]==c[2]
  if tag==3 and lod==0 and part<3:
   originals={key(old[i*size:(i+1)*size]):old[i*size:(i+1)*size] for i in range(count)};prior={key(c[-1][i*size:(i+1)*size]):c[-1][i*size:(i+1)*size] for i in range(count)}
   for i in range(count):
    record=payload[i*size:(i+1)*size];k=key(record);o=originals[k];p=prior[k];f=lookup[(part,k)];assert record[4:12]==o[4:12] and record[48:72]==o[48:72];assert record[4:24]==p[4:24] and record[48:]==p[48:]
    ids=struct.unpack_from('<3I',record,12);uv=struct.unpack_from('<6f',record,24)
    for j,vi in enumerate(ids):
     q=f['uv'][f['vertex_ids'].index(vi)];error=max(error,abs(uv[j]-q[0]),abs(1-uv[j+3]-q[1]))
    assert struct.unpack_from('<I',record,0)[0]==f['native_material_slot']
    if f['blender_material']==2:assert record[0:4]!=p[0:4];materials+=1;assert record[24:48]!=p[24:48]
    else:assert record==p
    changed+=record[24:48]!=p[24:48];total+=1
  else:assert payload==old==c[-1];unchanged+=1
 assert total==494 and changed==materials==want_changes and error<1e-6
 for f in expected:assert f['native_material_slot']<slots[f['part']]
 reports.append({'file':name,'matched_lod0_faces':total,'changed_uv_faces_since_v6':changed,'repair_material_faces':materials,'max_corner_uv_error':error,'unchanged_other_chunks':unchanged,'unselected_faces_exactly_preserved':True,'geometry_normals_attachments_animation_damage_flags_and_lower_lods_preserved':True,'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest()})
(W/'native_roundtrip.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps(reports,indent=2))
