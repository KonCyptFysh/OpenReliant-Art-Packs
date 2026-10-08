from pathlib import Path
import hashlib,importlib.util,json,shutil,struct,subprocess
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parents[2];W=D/'recipes/reconstruction_v1';out=D/'exports/openreliant_v1/mods/99-crusader-worn-v1';out.mkdir(parents=True,exist_ok=True)
r=json.loads((W/'validation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(Path(r['scene']))==r['scene_sha256']
parts=['Crusader_Body','Crusader_Cockpit','Crusader_Tail_Gun'];reports=[]
for name in ['British_Crusader.SHP','t_British_Crusader.SHP','Crusader_gun.SHP']:
 data=(D/'originals'/name).read_bytes();chunks=[];pos=0;part=lod=-1;changes=[];uv_errors=[];face_count=0
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos);end=pos+6+size*count;payload=bytearray(data[pos+6:end]);original=bytes(payload)
  if tag==2:part+=1;lod=-1
  if tag==4:
   lod+=1
   if lod==0 and part<3:
    model=r['models'][parts[part]];sv=np.array(model['vertices']);dv=np.array([struct.unpack_from('<3f',payload,i*size) for i in range(count)])
    sv-=.5*(sv.min(0)+sv.max(0));dv-=.5*(dv.min(0)+dv.max(0));canonical=np.linalg.norm(sv[:,None,:]-sv[None,:,:],axis=-1).argmin(1);dist=np.linalg.norm(dv[:,None,:]-sv[None,:,:],axis=-1);nearest=dist.argmin(1)
    assert dist.min(1).max()<3,(name,part,float(dist.min(1).max()));lookup={tuple(sorted(canonical[f['vertices']])):f for f in model['faces']};assert len(lookup)==len(model['faces'])
  if tag==3 and lod==0 and part<3:
   assert len(model['faces'])==count
   for i in range(count):
    off=i*size;idx=list(struct.unpack_from('<3I',payload,off+12));uv=struct.unpack_from('<6f',payload,off+24);f=lookup[tuple(sorted(nearest[idx]))];cu=[canonical[j] for j in f['vertices']]
    expected=[f['uv'][cu.index(nearest[j])] for j in idx];err=max(max(abs(uv[k]-expected[k][0]),abs(1-uv[k+3]-expected[k][1])) for k in range(3));uv_errors.append(err);face_count+=1
  if tag==6:
   for i in range(count):
    old=bytes(payload[i*size:(i+1)*size]).split(b'\0')[0].decode()
    if old.lower() in ['brit1','t_brit1']:
     payload[i*size:(i+1)*size]=b'orcr1_hull'.ljust(size,b'\0');changes.append(dict(part=part,lod=lod,old_material=old,new_material='orcr1_hull'))
  else:assert bytes(payload)==original
  chunks.append(struct.pack('<HHH',tag,size,count)+payload);pos=end
 assert pos==len(data) and face_count==382
 assert max(uv_errors)<0.00001,(name,max(uv_errors))
 (out/name).write_bytes(b''.join(chunks))
 reports.append(dict(file=name,source_sha256=sha(D/'originals'/name),delivered_sha256=sha(out/name),material_replacements=changes,verified_lod0_faces=face_count,max_uv_difference_from_flight=max(uv_errors),all_geometry_uvs_normals_attachments_animations_and_damage_flags_byte_identical=True,all_original_LODs_retained=True))
for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(r['maps'][key]['path'],out/f'orcr1_hull{suffix}.png')
rough=Image.open(r['maps']['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(r['maps']['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(out/'orcr1_hull_orm.png')
for suffix in ['','_normal','_orm']:shutil.copy2(out/f'orcr1_hull{suffix}.png',out/f'gorcr1_hull{suffix}.png')
spec=importlib.util.spec_from_file_location('crusader_inspection',W/'inspection.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);(out/'mission990.dte').write_bytes(module.inspection_mission())
(out/'mod.ini').write_text('[Mod]\nName=Crusader - Worn Paint\nVersion=0.1.0-beta.1\nDescription=Restored worn steel and red livery, smooth cockpit glazing and structural material maps. Flight, training and loadout share the artwork. In-game review pending.\nOpenReliant=0.7.0\nLicense=CC-BY-NC-SA-4.0\n')
(out/'license.txt').write_text("Crusader - Worn Paint\nOriginal artwork contributions by KonCyptFysh: CC-BY-NC-SA-4.0\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/\nOriginal StarLancer models, texture designs and other third-party materials remain the property of their respective rights holders. This licence applies only to the original restoration contributions, not to the original game or OpenReliant. Requires your own StarLancer installation.\n")
shutil.copy2(D/'review/reconstruction_v1/material_front.png',out/'mod.png')
tool=Path(__import__('os').environ.get('SLTOOL') or shutil.which('sltool') or 'sltool');checks=[]
for p in [*out.glob('*.SHP'),out/'mission990.dte']:
 kind='dte' if p.suffix=='.dte' else 'shp';q=subprocess.run([str(tool),kind,'check',str(p)],capture_output=True,text=True);assert q.returncode==0,(p,q.stdout,q.stderr);checks.append(dict(file=p.name,exit_status=q.returncode,output=q.stdout+q.stderr,sha256=sha(p)))
 if kind=='shp':
  info=subprocess.run([str(tool),'shp','info',str(p)],capture_output=True,text=True,check=True).stdout;assert 'orcr1_hull' in info;(W/(p.name+'.info')).write_text(info)
q=subprocess.run([str(tool),'dte','ships',str(out/'mission990.dte')],capture_output=True,text=True,check=True);assert 'Crusader - Inspection' in q.stdout and '     3 ' in q.stdout;(W/'mission990-ships.txt').write_text(q.stdout)
for p in out.glob('*.png'):
 with Image.open(p) as im:im.verify()
(W/'native_preservation.json').write_text(json.dumps(reports,indent=2)+'\n');(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n');print('Crusader native export validated: 3 models, all LODs, shared maps and one-ship mission.')
