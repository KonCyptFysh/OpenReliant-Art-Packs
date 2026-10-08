import os
from pathlib import Path
import hashlib,importlib.util,json,shutil,struct,subprocess
import numpy as np
from PIL import Image
D=Path(os.environ['PHOENIX_WORKSPACE'])
W=D/'work/audit_v2';out=D/'exports/openreliant_v2/mods/98-phoenix-worn-v1';out.mkdir(parents=True,exist_ok=True)
r=json.loads((W/'validation.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Path(r['scene']))==r['scene_sha256']
parts=['Phoenix_Tail_Gun','Phoenix_Body','Phoenix_Cockpit'];reports=[]
for name in ['USPF_Phx.SHP','t_USPF_Phx.SHP','Phoenix_gun.SHP']:
 data=(D/'source'/name).read_bytes();chunks=[];pos=0;part=-1;lod=-1;changes=[];face_report=[]
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos);end=pos+6+size*count;payload=bytearray(data[pos+6:end]);original=bytes(payload)
  if tag==2:part+=1;lod=-1
  if tag==4:
   lod+=1
   if lod==0 and part<3:
    model=r['models'][parts[part]];sv=np.array(model['vertices']);dv=np.array([struct.unpack_from('<3f',payload,i*size) for i in range(count)])
    sv-=.5*(sv.min(0)+sv.max(0));dv-=.5*(dv.min(0)+dv.max(0))
    canonical=np.linalg.norm(sv[:,None,:]-sv[None,:,:],axis=-1).argmin(1)
    dist=np.linalg.norm(dv[:,None,:]-sv[None,:,:],axis=-1);nearest=dist.argmin(1)
    assert dist.min(1).max()<3,(name,part,float(dist.min(1).max()))
    lookup={tuple(sorted(canonical[f['vertices']])):f for f in model['faces']}
    assert len(lookup)==len(model['faces'])
  if lod==0 and tag==3 and part<3:
   assert len(model['faces'])==count;records=[];used=[]
   for i in range(count):
    off=i*size;record=bytearray(payload[off:off+size]);idx=list(struct.unpack_from('<3I',record,12))
    f=lookup[tuple(sorted(nearest[idx]))];used.append(f['id'])
    cu=[canonical[j] for j in f['vertices']];uv=[f['uv'][cu.index(nearest[j])] for j in idx]
    # Preserve the material slot in the loadout, which also contains stock gun textures.
    if size >= 80 and struct.unpack_from('<I',record,72)[0]==3:idx[1],idx[2]=idx[2],idx[1];uv[1],uv[2]=uv[2],uv[1]
    struct.pack_into('<3I',record,12,*idx);struct.pack_into('<6f',record,24,*[q[0] for q in uv],*[1-q[1] for q in uv])
    if size >= 80:struct.pack_into('<2I',record,72,0,0)
    assert record[:12]==original[off:off+12] and record[48:72]==original[off+48:off+72]
    records.append(record)
    face_report.append({'part':part,'canonical_face':f['id'],'vertex_ids':idx,'uv':uv})
   assert len(set(used))==count
   records.sort(key=lambda q:struct.unpack_from('<3I',q));payload=bytearray(b''.join(records))
   changes.append({'part':part,'faces':count,'uvs_reused_from_flight_model':True,'max_matching_vertex_delta':float(dist.min(1).max())})
  elif lod==0 and tag==6:
   for i in range(count):
    old=bytes(payload[i*size:(i+1)*size]).split(b'\0')[0].decode()
    if old.lower() in ['yank_4','t_yank_4']:payload[i*size:(i+1)*size]=b'orpx1_hull'.ljust(size,b'\0')
  else:assert payload==original
  chunks.append(struct.pack('<HHH',tag,size,count)+payload);pos=end
 assert pos==len(data)
 (out/name).write_bytes(b''.join(chunks))
 reports.append({'file':name,'source_sha256':sha(D/'source'/name),'delivered_sha256':sha(out/name),'mapped_parts':changes,'geometry_normals_attachments_animation_damage_flags_lower_LODs_unchanged':True})
 (W/(name+'.exported_faces.json')).write_text(json.dumps(face_report,indent=2)+'\n')
for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(r['maps'][key]['path'],out/f'orpx1_hull{suffix}.png')
rough=Image.open(r['maps']['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(r['maps']['metallic']['path']).convert('RGB').getchannel('R')
Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(out/'orpx1_hull_orm.png')
for suffix in ['','_normal','_orm']:shutil.copy2(out/f'orpx1_hull{suffix}.png',out/f'gorpx1_hull{suffix}.png')
spec=importlib.util.spec_from_file_location('phoenix_inspection',W/'inspection.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
(out/'mission990.dte').write_bytes(module.inspection_mission())
(out/'mod.ini').write_text('[Mod]\nName=Phoenix - Worn Paint\nVersion=0.1.0-beta.1\nDescription=Worn artwork with aligned belly band and smooth reflective canopy glass; shared flight, training and loadout models. Final visual review pending.\nOpenReliant=0.7.0\nLicense=CC-BY-NC-SA-4.0\n')
(out/'license.txt').write_text("Phoenix - Worn Paint\nOriginal artwork contributions by KonCyptFysh: CC-BY-NC-SA-4.0\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/\nOriginal StarLancer models, texture designs and other third-party materials remain the property of their respective rights holders. This licence applies only to the original restoration contributions, not to the original game or OpenReliant. Requires your own StarLancer installation.\n")
shutil.copy2(D/'review/audit_v2/material_front.png',out/'mod.png')
tool=Path(os.environ['OPENRELIANT_SLTOOL']);checks=[]
for p in [*out.glob('*.SHP'),out/'mission990.dte']:
 kind='dte' if p.suffix=='.dte' else 'shp';q=subprocess.run([str(tool),kind,'check',str(p)],capture_output=True,text=True);assert q.returncode==0,(p,q.stdout,q.stderr)
 checks.append({'file':p.name,'exit_status':q.returncode,'output':q.stdout+q.stderr,'sha256':sha(p)})
 if kind=='shp':
  info=subprocess.run([str(tool),'shp','info',str(p)],capture_output=True,text=True,check=True).stdout;assert 'orpx1_hull' in info;(W/(p.name+'.info')).write_text(info)
q=subprocess.run([str(tool),'dte','ships',str(out/'mission990.dte')],capture_output=True,text=True,check=True);assert 'Phoenix - Inspection' in q.stdout and '    11 ' in q.stdout;(W/'mission990-ships.txt').write_text(q.stdout)
for p in out.glob('*.png'):
 with Image.open(p) as im:im.verify()
(W/'native_preservation.json').write_text(json.dumps(reports,indent=2)+'\n');(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('Phoenix native export validated: three models, shared maps and a one-ship mission.')
