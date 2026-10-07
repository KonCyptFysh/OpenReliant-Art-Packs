from pathlib import Path
import json,struct,hashlib,shutil,subprocess,datetime
from PIL import Image
D=Path('authoring://Naginata/worn');W=D/'work/edges_v4';R=Path('local-only://openreliant-alliance-fighters');folder='95-naginata-worn-v1';out=R/'.local/naginata-v4-export';out.mkdir(exist_ok=True);prior=json.loads((W/'prior_project_state.json').read_text());r=json.loads((W/'bake_validation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(Path(r['source']))==r['source_sha256'] and sha(Path(r['scene']))==r['scene_sha256'];reports=[]
for name in ['JLF_Nagi.SHP','t_JLF_Nagi.SHP']:
 data=(D/'source'/name).read_bytes();chunks=[];pos=0;part=-1;lod=-1;changes=[]
 while pos<len(data):
  tag,size,count=struct.unpack_from('<HHH',data,pos);end=pos+6+size*count;payload=bytearray(data[pos+6:end]);original=bytes(payload)
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  if lod==0 and tag==3:
   model=r['models'][['Naginata_c-pit','Naginata_Body'][part]];assert len(model['faces'])==count;records=[];slots={0:0,1:0,2:1,3:2};counts={0:0,1:0,2:0};lookup={tuple(sorted(f['vertices'])):f for f in model['faces']};assert len(lookup)==count
   for i in range(count):
    off=i*size;record=bytearray(payload[off:off+size]);idx=list(struct.unpack_from('<3I',record,12));f=lookup[tuple(sorted(idx))];uv=[f['uv'][f['vertices'].index(j)] for j in idx];mi=slots[f['material']];counts[mi]+=1;struct.pack_into('<I',record,0,mi)
    if struct.unpack_from('<I',record,72)[0]==3:idx[1],idx[2]=idx[2],idx[1];uv[1],uv[2]=uv[2],uv[1]
    struct.pack_into('<3I',record,12,*idx);struct.pack_into('<6f',record,24,*[q[0] for q in uv],*[1-q[1] for q in uv]);struct.pack_into('<2I',record,72,0,0)
    assert record[4:12]==original[off+4:off+12] and record[48:72]==original[off+48:off+72];records.append(record)
   records.sort(key=lambda q:struct.unpack_from('<3I',q));payload=bytearray(b''.join(records));changes.append({'part':part,'faces':count,'material_face_counts':counts,'allowed_changes':['material slot','corner UV','equivalent triangle winding and fan encoding','surface grouping order']})
  elif lod==0 and tag==6:
   payload=bytearray(b''.join(n.ljust(64,b'\0') for n in [b'orna1_hull',b'orna3_fix',b'orna4_edges']));count=3
  else:assert payload==original
  chunks.append(struct.pack('<HHH',tag,size,count)+payload);pos=end
 assert pos==len(data);(out/name).write_bytes(b''.join(chunks));reports.append({'file':name,'source_sha256':sha(D/'source'/name),'delivered_sha256':sha(out/name),'changes':changes,'all_nonface_nonmaterial_and_lower_LOD_chunks_unchanged':True,'engine_glow_attachments_unchanged':True})
# Reuse the accepted complete v3 texture families byte for byte.
current=R/'mods'/folder
for p in current.iterdir():
 if p.suffix.lower() not in ['.shp'] and p.name!='mod.ini':shutil.copy2(p,out/p.name)
for kind,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(r['maps'][kind]['path'],out/f'orna4_edges{suffix}.png')
rough=Image.open(r['maps']['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(r['maps']['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(out/'orna4_edges_orm.png')
for suffix in ['','_normal','_orm']:shutil.copy2(out/f'orna4_edges{suffix}.png',out/f'gorna4_edges{suffix}.png')
(out/'mod.ini').write_text('[Mod]\nName=Naginata Worn - v4 Edges and Exhausts\nVersion=4.0\nDescription=Separate full-area wing edge and opening UVs, corrected engine wear projection, and legacy-style louvred exhaust outlets at the original engine points.\nOpenReliant=0.7\n')
tool=Path('local-only://sltool');checks=[]
for name,kind in [('JLF_Nagi.SHP','shp'),('t_JLF_Nagi.SHP','shp'),('mission994.dte','dte')]:
 q=subprocess.run([str(tool),kind,'check',str(out/name)],capture_output=True,text=True);assert q.returncode==0,(name,q.stdout,q.stderr);checks.append({'file':name,'exit_code':0,'output':q.stdout+q.stderr,'sha256':sha(out/name)})
for name in ['JLF_Nagi.SHP','t_JLF_Nagi.SHP']:
 info=subprocess.run([str(tool),'shp','info',str(out/name)],capture_output=True,text=True,check=True).stdout;assert all(n in info for n in ['orna1_hull','orna3_fix','orna4_edges']);(W/(name+'.info')).write_text(info)
for p in out.glob('*.png'):
 with Image.open(p) as im:im.verify()
# Preserve the previous repository export before installing the coherent new directory contents.
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=R/'.local/backups'/('naginata-v3-'+stamp);shutil.copytree(current,backup)
for p in sorted(out.iterdir()):shutil.copy2(p,current/p.name);assert sha(p)==sha(current/p.name)
assert len(list(current.iterdir()))==23
(W/'native_preservation_v4.json').write_text(json.dumps(reports,indent=2));(W/'native_checks_v4.json').write_text(json.dumps(checks,indent=2));(W/'repository_export_v4.json').write_text(json.dumps({'runtime_folder':str(current),'previous_export_backup':str(backup),'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(current.iterdir())]},indent=2));print('REPOSITORY_V4_EXPORT',len(list(current.iterdir())),'files; 2 native models; 3 complete texture families',flush=True)
