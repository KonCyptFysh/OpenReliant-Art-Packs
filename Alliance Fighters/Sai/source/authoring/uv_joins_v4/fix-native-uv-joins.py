from pathlib import Path
import struct,json,hashlib,shutil,subprocess
import numpy as np

D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/uv_joins_v4';Q=D/'review/uv_joins_v4';H=D/'history/stages/pre_uv_joins_v4';O=D/'exports/openreliant_v4/mods/100-sai-worn-v1';prior=D/'exports/openreliant_v3/mods/100-sai-worn-v1'
for p in [W,Q,H]:p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=json.loads((D.parent/'project_state.json').read_text());assert state['latest_pass']=='kanji_v3'
for p in [D.parent/'project_state.json',D/'manifest.json',D/'README.md']:
 if not (H/p.name).exists():shutil.copy2(p,H/p.name)
shutil.copytree(prior,O,dirs_exist_ok=True)
source=prior/'Jap_Sai.SHP';raw=source.read_bytes();patched=bytearray(raw)
def read_faces(data,size,count):
 out=[]
 for i in range(count):
  q=data[i*size:(i+1)*size];ids=list(struct.unpack_from('<3I',q,12));uv=np.array(struct.unpack_from('<6f',q,24)).reshape(2,3).T.tolist();kind,left=struct.unpack_from('<2I',q,72)
  out.append(dict(id=i,vertices=ids,uv=uv,kind=kind,remaining=left))
 return out
def groups(fs):
 i=0
 while i<len(fs):
  end=i+fs[i]['remaining']+1;assert end<=len(fs)
  for j in range(i,end):assert fs[j]['remaining']==end-j-1
  yield i,end;i=end
def reused(anchor,previous):
 if anchor['kind']==1:return [anchor['vertices'][0],previous['vertices'][2]],[anchor['uv'][0],previous['uv'][2]]
 assert anchor['kind'] in [2,3]
 return previous['vertices'][1:],previous['uv'][1:]
def consistent(anchor,prev,cur):
 ids,uv=reused(anchor,prev)
 return ids==cur['vertices'][:2] and np.max(np.abs(np.array(uv)-np.array(cur['uv'][:2])))<=1e-6
def effective(fs):
 result=[]
 for start,end in groups(fs):
  corners=list(zip(fs[start]['vertices'],fs[start]['uv']));kind=fs[start]['kind'];anchor=corners[0];prev=corners[-2:]
  result.append(dict(id=start,vertices=fs[start]['vertices'],uv=fs[start]['uv']))
  for j in range(start+1,end):
   last=(fs[j]['vertices'][2],fs[j]['uv'][2]);now=[anchor,prev[-1],last] if kind==1 else [prev[-2],prev[-1],last]
   assert [p[0] for p in now]==fs[j]['vertices'];result.append(dict(id=j,vertices=fs[j]['vertices'],uv=[p[1] for p in now]));prev=now[-2:]
 return result

pos=0;part=lod=-1;changed=[];chunks=[];before_mesh={};after_mesh={};stats=[]
names=['Sai_Nose','Sai_Low_fin','Sai_Main_body']
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);data_start=pos+6;data=raw[data_start:data_start+size*count];pos=data_start+size*count
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag!=3:continue
 assert size==80
 fs=read_faces(data,size,count);orig_groups=list(groups(fs));before=effective(fs);segments=[]
 for start,end in orig_groups:
  seg=start
  for j in range(start+1,end):
   if not consistent(fs[seg],fs[j-1],fs[j]):segments.append((seg,j));seg=j
  segments.append((seg,end))
 for start,end in segments:
  for j in range(start,end):
   left=end-j-1
   if fs[j]['remaining']!=left:
    at=data_start+j*size+76;struct.pack_into('<I',patched,at,left);changed.append(dict(part=names[part],lod=lod,face=j,original_remaining=fs[j]['remaining'],remaining=left,offset=at));fs[j]['remaining']=left
 after=effective(fs)
 assert all(np.max(np.abs(np.array(q['uv'])-np.array(fs[q['id']]['uv'])))<=1e-6 for q in after)
 mismatches=[q['id'] for q in before if np.max(np.abs(np.array(q['uv'])-np.array(fs[q['id']]['uv'])))>1e-6]
 stats.append(dict(part=names[part],lod=lod,faces=count,prior_groups=len(orig_groups),new_groups=len(segments),previously_misread_faces=mismatches,remaining_misread_faces=0))
 if lod==0:before_mesh[names[part]]=before;after_mesh[names[part]]=after
 # The only editable field is the original primitive continuation count.
 newdata=patched[data_start:data_start+size*count]
 for j in range(count):assert newdata[j*size:j*size+76]==data[j*size:j*size+76]

assert pos==len(raw);allowed=set(k for c in changed for k in range(c['offset'],c['offset']+4));diff=[i for i,(a,b) in enumerate(zip(raw,patched)) if a!=b];assert all(i in allowed for i in diff)
assert len(patched)==len(raw);(O/'Jap_Sai.SHP').write_bytes(patched)
tool='/home/lva-8700/Games/OpenReliant/releases/openreliant-v0.7.0-linux-x86_64/sltool';checks=[]
for file,kind in [('Jap_Sai.SHP','shp'),('mission991.dte','dte')]:
 p=subprocess.run([tool,kind,'check',str(O/file)],capture_output=True,text=True,check=True);checks.append(dict(file=file,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(O/file)))
assert [p.name for p in prior.iterdir() if sha(p)!=sha(O/p.name)]==['Jap_Sai.SHP']
report={'passed':True,'cause':'The separate left/right remap introduced UV seams inside native fan/strip groups. The 0.7.0 loader and draw pass reuse the first two corners at each continuation, so those corners used the prior triangle UVs across the atlas.','repair':'Split continuation groups only where shared-corner UVs differ; keep every per-face vertex index, UV, winding, material and normal byte unchanged.','source':str(source),'source_sha256':sha(source),'output':str(O/'Jap_Sai.SHP'),'output_sha256':sha(O/'Jap_Sai.SHP'),'changed_continuation_records':len(changed),'changed_bytes':len(diff),'only_continuation_fields_changed':True,'all_maps_and_other_mod_files_byte_identical':True,'all_native_LOD_faces_checked':sum(x['faces'] for x in stats),'rendered_corner_uvs_match_authored_uvs':True,'remaining_misread_faces':0,'details':stats,'changes':changed,'native_checks':checks,'runtime_visual_review':'pending_user_review','engine_build':'Official OpenReliant 0.7.0','source_reference':['https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/game/srofiles.zig','https://github.com/OpenReliant/openreliant/blob/v0.7.0/src/engine/surrender/srd3d/srd3d.zig']}
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(W/'effective_uvs_before.json').write_text(json.dumps(before_mesh));(W/'effective_uvs_after.json').write_text(json.dumps(after_mesh))
shutil.copy2(__file__,W/'fix-native-uv-joins.py')
for name in ['srofiles','srd3d']:shutil.copy2(Path('/tmp')/f'sai-{name}-v070.zig',W/f'{name}-v070.zig')
print(json.dumps({k:v for k,v in report.items() if k not in ['details','changes']},indent=2))
