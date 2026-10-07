from pathlib import Path
import json,struct,hashlib,shutil,subprocess,importlib.util
from PIL import Image
D=Path('local-only://worn');W=D/'work/refinement_v2';R=Path('local-only://openreliant-alliance-fighters');F='96-patriot-worn-v1';out=R/'mods'/F;out.mkdir(parents=True,exist_ok=True);r=json.loads((W/'validation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(Path(r['scene']))==r['scene_sha256'];reports=[];parts=['Patriot_Cockpit','Patriot_Rear_Gun','Patriot_Body']
for name in ['USMF_Pat.SHP','t_USMF_Pat.SHP']:
 data=(D/'source'/name).read_bytes();chunks=[];pos=0;part=-1;lod=-1;changes=[]
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos);end=pos+6+size*count;payload=bytearray(data[pos+6:end]);original=bytes(payload)
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  if lod==0 and tag==3:
   model=r['models'][parts[part]];assert len(model['faces'])==count;records=[];lookup={tuple(sorted(f['vertices'])):f for f in model['faces']};assert len(lookup)==count
   for i in range(count):
    off=i*size;record=bytearray(payload[off:off+size]);idx=list(struct.unpack_from('<3I',record,12));f=lookup[tuple(sorted(idx))];uv=[f['uv'][f['vertices'].index(j)] for j in idx];struct.pack_into('<I',record,0,1 if f['material']==2 else 0)
    if struct.unpack_from('<I',record,72)[0]==3:idx[1],idx[2]=idx[2],idx[1];uv[1],uv[2]=uv[2],uv[1]
    struct.pack_into('<3I',record,12,*idx);struct.pack_into('<6f',record,24,*[q[0] for q in uv],*[1-q[1] for q in uv]);struct.pack_into('<2I',record,72,0,0)
    assert record[4:12]==original[off+4:off+12] and record[48:72]==original[off+48:off+72];records.append(record)
   records.sort(key=lambda q:struct.unpack_from('<3I',q));payload=bytearray(b''.join(records));changes.append({'part':part,'faces':count,'allowed_changes':['material slot','corner UV','equivalent triangle fan encoding','surface grouping order']})
  elif lod==0 and tag==6:payload=bytearray(b'orpa1_hull'.ljust(64,b'\0')+b'orpa2_fix'.ljust(64,b'\0'));count=2
  else:assert payload==original
  chunks.append(struct.pack('<HHH',tag,size,count)+payload);pos=end
 assert pos==len(data);(out/name).write_bytes(b''.join(chunks));reports.append({'file':name,'source_sha256':sha(D/'source'/name),'delivered_sha256':sha(out/name),'changes':changes,'geometry_normals_attachments_lower_LODs_animation_turret_data_unchanged':True})
for maps,stem in [(r['main_maps'],'orpa1_hull'),(r['maps'],'orpa2_fix')]:
 for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(maps[key]['path'],out/(stem+suffix+'.png'))
 rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(out/(stem+'_orm.png'))
 for suffix in ['','_normal','_orm']:shutil.copy2(out/(stem+suffix+'.png'),out/('g'+stem+suffix+'.png'))
assert (out/'mission992.dte').is_file()
(out/'mod.ini').write_text('[Mod]\nName=Patriot Worn - v2\nVersion=2.0\nDescription=Refined smoked glass, continuous panel joins, centred gun muzzles and corrected raised radiator fins.\nOpenReliant=0.7\n')
shutil.copy2(D/'review/refinement_v2/v2_overview.png',out/'mod.png')
tool=Path('local-only://sltool');checks=[]
for name,kind in [('USMF_Pat.SHP','shp'),('t_USMF_Pat.SHP','shp'),('mission992.dte','dte')]:
 q=subprocess.run([str(tool),kind,'check',str(out/name)],capture_output=True,text=True);assert q.returncode==0,(name,q.stdout,q.stderr);checks.append({'file':name,'exit_status':0,'output':q.stdout+q.stderr,'sha256':sha(out/name)})
for name in ['USMF_Pat.SHP','t_USMF_Pat.SHP']:
 info=subprocess.run([str(tool),'shp','info',str(out/name)],capture_output=True,text=True,check=True).stdout;assert 'orpa2_fix' in info and 'orpa1_hull' in info and 'Patriot Rear Gun' in info;(W/(name+'.info')).write_text(info)
mission=subprocess.run([str(tool),'dte','ships',str(out/'mission992.dte')],capture_output=True,text=True,check=True).stdout;assert 'Patriot - Inspection' in mission and '     7 ' in mission;(W/'mission992-ships.txt').write_text(mission)
for p in out.glob('*.png'):
 with Image.open(p) as im:im.verify()
(W/'native_preservation.json').write_text(json.dumps(reports,indent=2));(W/'native_checks.json').write_text(json.dumps(checks,indent=2));(W/'repository_export.json').write_text(json.dumps({'runtime_folder':str(out),'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir())]},indent=2));print('PATRIOT_NATIVE_EXPORT_COMPLETE',len(list(out.iterdir())),'files',flush=True)
