from pathlib import Path
import json,struct,hashlib
D=Path('authoring://Patriot/worn');W=D/'work/audit_v3';R=Path('asset://Patriot');out=R/'mods/96-patriot-worn-v1';r=json.loads((W/'validation.json').read_text());names=['Patriot_Cockpit','Patriot_Rear_Gun','Patriot_Body']
def chunks(p):
 d=p.read_bytes();off=0;result=[]
 while off<len(d):
  tag,size,count=struct.unpack_from('<HHH',d,off);end=off+6+size*count;result.append((tag,size,count,d[off+6:end]));off=end
 assert off==len(d);return result
reports=[]
for name in ['USMF_Pat.SHP','t_USMF_Pat.SHP']:
 old=chunks(D/'source'/name);new=chunks(out/name);assert len(old)==len(new);part=-1;lod=-1;faces=0;untouched=0;maxdelta=0
 for a,b in zip(old,new):
  t,z,c,buf=b;assert (t,z)==a[:2]
  if t==2:part+=1;lod=-1
  if t==4:lod+=1
  if lod==0 and t==3:
   assert c==a[2];model=r['models'][names[part]];lookup={tuple(sorted(f['vertices'])):f for f in model['faces']}
   for i in range(c):
    offset=i*z;idx=struct.unpack_from('<3I',buf,offset+12);f=lookup[tuple(sorted(idx))];uv=struct.unpack_from('<6f',buf,offset+24);mat=struct.unpack_from('<I',buf,offset)[0];assert mat==(f['material']-1 if f['material']>=2 else 0)
    for j,vi in enumerate(idx):
     q=f['uv'][f['vertices'].index(vi)];delta=max(abs(q[0]-uv[j]),abs(q[1]-(1-uv[j+3])));assert delta<1e-6;maxdelta=max(delta,maxdelta)
    faces+=1
  elif lod==0 and t==6:assert c==3 and [buf[i:i+64].split(b'\0')[0] for i in range(0,192,64)]==[b'orpa1_hull',b'orpa2_fix',b'orpa3_wrap']
  else:assert a==b;untouched+=1
 assert faces==440 and part==2;reports.append({'file':name,'matched_LOD0_faces':faces,'maximum_corner_uv_error':maxdelta,'unchanged_other_chunks':untouched,'all_geometry_attachments_animation_lower_LODs_identical':True,'material_slots_match_scene':True})
(W/'native_roundtrip.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
