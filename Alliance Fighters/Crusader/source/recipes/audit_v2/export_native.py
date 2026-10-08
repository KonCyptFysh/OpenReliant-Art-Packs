
def resolve_record(v):
    if isinstance(v,dict):return {k:resolve_record(x) for k,x in v.items()}
    if isinstance(v,list):return [resolve_record(x) for x in v]
    if isinstance(v,str) and v.startswith('source/'):return str(Path(__file__).resolve().parents[2]/v[7:])
    return v
from pathlib import Path
import json,hashlib,struct,shutil,subprocess
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parents[2];W=D/'recipes/audit_v2';O=D/'exports/openreliant_v2/mods/99-crusader-worn-v1';P=D/'recipes/audit_v2/native_baseline';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=resolve_record(json.loads((W/'validation.json').read_text()));assert sha(r['scene'])==r['scene_sha256'];model=r['models']['Crusader_Body'];sv=np.array(model['vertices']);sv-=.5*(sv.min(0)+sv.max(0));canonical=np.linalg.norm(sv[:,None,:]-sv[None,:,:],axis=-1).argmin(1);lookup={tuple(sorted(canonical[f['vertices']])):f for f in model['faces']};reports=[]
def chunks(p):
 data=p.read_bytes();pos=0;part=lod=-1;out=[]
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos);end=pos+6+size*count
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  out.append((tag,size,count,part,lod,data[pos+6:end]));pos=end
 assert pos==len(data);return out
for name in ['British_Crusader.SHP','t_British_Crusader.SHP','Crusader_gun.SHP']:
 original=chunks(P/name);mat_count=next(c for t,z,c,p,l,a in original if t==6 and p==0 and l==0);out=[];changed=[];maxerr=0
 for tag,size,count,part,lod,data in original:
  payload=bytearray(data)
  if part==0 and lod==0 and tag==4:
   dv=np.array([struct.unpack_from('<3f',data,i*size) for i in range(count)]);dv-=.5*(dv.min(0)+dv.max(0));dist=np.linalg.norm(dv[:,None,:]-sv[None,:,:],axis=-1);near=dist.argmin(1);assert dist.min(1).max()<3
  if part==0 and lod==0 and tag==3:
   for i in range(count):
    off=i*size;record=bytearray(data[off:off+size]);idx=list(struct.unpack_from('<3I',record,12));f=lookup[tuple(sorted(near[idx]))]
    if f['material']!=2:continue
    cu=[canonical[j] for j in f['vertices']];uv=[f['uv'][cu.index(near[j])] for j in idx];struct.pack_into('<I',record,0,mat_count)
    # Standalone triangles prevent the legacy fan/strip merger from changing
    # the new periodic texture interpolation. Preserve their geometric front.
    if size>=80 and struct.unpack_from('<I',record,72)[0]==3:idx[1],idx[2]=idx[2],idx[1];uv[1],uv[2]=uv[2],uv[1]
    struct.pack_into('<3I',record,12,*idx);struct.pack_into('<6f',record,24,*[q[0] for q in uv],*[1-q[1] for q in uv])
    if size>=80:struct.pack_into('<2I',record,72,0,0)
    assert record[4:12]==data[off+4:off+12] and record[48:72]==data[off+48:off+72]
    payload[off:off+size]=record;changed.append(dict(native_face=i,canonical_face=f['id'],vertex_ids=idx,uv=uv,material_slot=mat_count))
   assert len(changed)==24
  elif part==0 and lod==0 and tag==6:payload.extend(b'orcr2_collar'.ljust(size,b'\0'));count+=1
  else:assert payload==data
  out.append(struct.pack('<HHH',tag,size,count)+payload)
 (O/name).write_bytes(b''.join(out));new=chunks(O/name)
 for a,b in zip(original,new):
  tag,size,count,part,lod,data=a
  if (part,lod,tag)==(0,0,6):assert b[-1][:-size]==data and b[2]==count+1;continue
  assert a[:5]==b[:5]
  if (part,lod,tag)==(0,0,3):
   used={q['native_face']:q for q in changed}
   for i in range(count):
    o=data[i*size:(i+1)*size];n=b[-1][i*size:(i+1)*size]
    if i not in used:assert o==n
    else:
     f=used[i];assert sorted(struct.unpack_from('<3I',o,12))==sorted(struct.unpack_from('<3I',n,12));assert o[4:12]==n[4:12] and o[48:72]==n[48:72];uv=struct.unpack_from('<6f',n,24);err=max(max(abs(uv[k]-f['uv'][k][0]),abs(1-uv[k+3]-f['uv'][k][1])) for k in range(3));maxerr=max(maxerr,err)
  else:assert data==b[-1]
 assert maxerr<1e-6
 reports.append(dict(file=name,previous_sha256=sha(P/name),sha256=sha(O/name),changed_uv_faces=24,appended_material='orcr2_collar',max_uv_roundtrip_error=maxerr,unselected_faces_and_all_other_chunks_byte_identical=True,geometry_normals_attachments_animations_damage_and_lower_LODs_preserved=True));(W/(name+'.exported_faces.json')).write_text(json.dumps(changed,indent=2)+'\n')
for family,key in [('orcr1_hull','maps'),('orcr2_collar','repair_maps')]:
 maps=r[key]
 for k,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(maps[k]['path'],O/f'{family}{suffix}.png')
 rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/f'{family}_orm.png')
 for suffix in ['','_normal','_orm']:shutil.copy2(O/f'{family}{suffix}.png',O/f'g{family}{suffix}.png')
for name in ['license.txt','mission990.dte']:shutil.copy2(P/name,O/name)
ini=(P/'mod.ini').read_text();ini='\n'.join('Description=Worn restoration with continuous engine collar seams, extended panel joint, clarified emblem and frame-fitted reflective glass. Shared flight, training and loadout artwork; review pending.' if l.startswith('Description=') else l for l in ini.splitlines())+'\n';(O/'mod.ini').write_text(ini)
shutil.copy2(D/'review/audit_v2/whole.png',O/'mod.png')
tool=Path(__import__('os').environ.get('SLTOOL') or shutil.which('sltool') or 'sltool');checks=[]
for p in [*O.glob('*.SHP'),O/'mission990.dte']:
 q=subprocess.run([str(tool),'dte' if p.suffix=='.dte' else 'shp','check',str(p)],capture_output=True,text=True);assert q.returncode==0,(p,q.stdout,q.stderr);checks.append(dict(file=p.name,exit_status=q.returncode,output=q.stdout+q.stderr,sha256=sha(p)))
(W/'native_preservation.json').write_text(json.dumps(reports,indent=2)+'\n');(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n');print('CRUSADER_V2_NATIVE_VALIDATED',reports)
