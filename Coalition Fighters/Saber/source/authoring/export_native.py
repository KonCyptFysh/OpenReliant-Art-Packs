from pathlib import Path
import os
import hashlib,importlib.util,json,shutil,struct,subprocess
import numpy as np
from PIL import Image

D=Path(os.environ['SABER_WORKSPACE']).resolve()
W=D/'work/reconstruction_v1';O=D/'exports/openreliant_v1/mods/102-saber-worn-v1';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());assert sha(r['scene'])==r['scene_sha256']
changed={}
for x in r['uv_repairs']:changed.setdefault(x['part'],set()).update(x['faces'])
raw=(D/'source/Rus_Sabre.SHP').read_bytes();out=bytearray(raw);pos=0;part=lod=-1;names=[];edits=[];joins=[];stats=[];materials=[]
def groups(fs):
 i=0
 while i<len(fs):
  end=i+fs[i]['remaining']+1;assert end<=len(fs)
  assert all(fs[j]['remaining']==end-j-1 for j in range(i,end))
  yield i,end;i=end
def reuse(anchor,previous):
 if anchor['kind']==1:return [anchor['vertices'][0],previous['vertices'][2]],[anchor['uv'][0],previous['uv'][2]]
 assert anchor['kind'] in [2,3]
 return previous['vertices'][1:],previous['uv'][1:]
def matches(anchor,prev,cur):
 ids,uv=reuse(anchor,prev)
 return ids==cur['vertices'][:2] and np.max(np.abs(np.array(uv)-cur['uv'][:2]))<=1e-6
allowed=set()
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count
 if tag==1:names=[raw[start+i*size:start+i*size+64].split(b'\0')[0].decode().replace(' ','_') for i in range(count)]
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==6:
  for i in range(count):
   at=start+i*size;old=raw[at:at+64].split(b'\0')[0].decode();assert old.lower()=='sabre'
   out[at:at+64]=b'orsb1_hull'.ljust(64,b'\0');allowed.update(range(at,at+64));materials.append(dict(part=part,lod=lod,old=old,new='orsb1_hull'))
 if tag==3:
  assert size==80
  if lod==0 and names[part] in changed:
   model=r['models'][names[part]];assert count==len(model['faces'])
   for i in sorted(changed[names[part]]):
    at=start+i*size;ids=list(struct.unpack_from('<3I',out,at+12));f=model['faces'][i]
    assert sorted(ids)==sorted(f['vertices'])
    q=[f['uv'][f['vertices'].index(j)] for j in ids]
    struct.pack_into('<6f',out,at+24,*[x[0] for x in q],*[1-x[1] for x in q]);allowed.update(range(at+24,at+48));edits.append(dict(part=names[part],lod=lod,face=i))
  fs=[]
  for i in range(count):
   at=start+i*size;uv=np.array(struct.unpack_from('<6f',out,at+24)).reshape(2,3).T
   kind,remaining=struct.unpack_from('<2I',out,at+72)
   fs.append(dict(vertices=list(struct.unpack_from('<3I',out,at+12)),uv=uv,kind=kind,remaining=remaining))
  oldgroups=list(groups(fs));segments=[]
  for first,last in oldgroups:
   seg=first
   for j in range(first+1,last):
    if not matches(fs[seg],fs[j-1],fs[j]):segments.append((seg,j));seg=j
   segments.append((seg,last))
  for first,last in segments:
   for j in range(first,last):
    remaining=last-j-1
    if remaining!=fs[j]['remaining']:
     at=start+j*size+76;struct.pack_into('<I',out,at,remaining);allowed.update(range(at,at+4))
     joins.append(dict(part=names[part],lod=lod,face=j,prior=fs[j]['remaining'],remaining=remaining))
     fs[j]['remaining']=remaining
  for first,last in groups(fs):
   for j in range(first+1,last):assert matches(fs[first],fs[j-1],fs[j])
  stats.append(dict(part=names[part],lod=lod,faces=count,groups_before=len(oldgroups),groups_after=len(segments),all_shared_corner_uvs_match=True))
 pos=end
assert pos==len(raw)==len(out)
diff=[i for i,(a,b) in enumerate(zip(raw,out)) if a!=b]
assert all(i in allowed for i in diff)
assert len(edits)==22 and sum(x['faces'] for x in stats)==1938
(O/'Rus_Sabre.SHP').write_bytes(out)
preservation=dict(passed=True,source_sha256=sha(D/'source/Rus_Sabre.SHP'),output_sha256=sha(O/'Rus_Sabre.SHP'),uv_edits=edits,continuation_corrections=joins,detail_meshes=stats,all_1938_faces_checked=True,geometry_normals_attachments_animation_collision_and_winding_byte_identical=True,allowed_changes='22 finest-detail UV faces, texture names and primitive continuation counts at UV seams only',changed_bytes=len(diff))
(W/'native_preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
maps=r['maps']['hull']
for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(maps[key]['path'],O/('orsb1_hull'+suffix+'.png'))
rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R')
Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/'orsb1_hull_orm.png')
for suffix in ['','_normal','_orm']:shutil.copy2(O/('orsb1_hull'+suffix+'.png'),O/('gorsb1_hull'+suffix+'.png'))
ins=(Path(os.environ['ART_PACK_REPOSITORY'])/'Coalition Fighters/Saber/source/authoring/inspection.py').read_text()
(W/'inspection.py').write_text(ins)
spec=importlib.util.spec_from_file_location('saber_inspection',W/'inspection.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
(O/'mission989.dte').write_bytes(module.inspection_mission())
(O/'mod.ini').write_text('[Mod]\nName=Saber - Worn Paint\nVersion=0.1.0-beta.1\nDescription=Restored worn silver-grey and red Coalition livery, amber glazing and repaired machinery UVs.\nOpenReliant=0.7.0\nLicense=CC-BY-NC-SA-4.0\n')
(O/'license.txt').write_text('Saber - Worn Paint\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/\nOriginal StarLancer assets retain their respective owners rights. Requires your own StarLancer installation.\n')
shutil.copy2(D/'review/reconstruction_v1/material_front.png',O/'mod.png')
tool=os.environ['OPENRELIANT_SLTOOL'];checks=[]
for kind,file in [('shp','Rus_Sabre.SHP'),('dte','mission989.dte')]:
 p=subprocess.run([tool,kind,'check',str(O/file)],capture_output=True,text=True,check=True);checks.append(dict(file=file,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(O/file)))
ships=subprocess.check_output([tool,'dte','ships',str(O/'mission989.dte')],text=True);assert 'Saber - Inspection' in ships and '43' in ships
(W/'mission989-ships.txt').write_text(ships)
(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
glass=np.asarray(Image.open(maps['glass']['path']).convert('L'))>250
normal=np.asarray(Image.open(O/'orsb1_hull_normal.png').convert('RGB')).astype(np.float32)/255*2-1
lengths=np.linalg.norm(normal,axis=-1);assert np.max(np.abs(lengths-1))<.02
assert np.max(np.abs(normal[glass]-[0,0,1]))<.008
orm=np.asarray(Image.open(O/'orsb1_hull_orm.png').convert('RGB'))
assert np.all(orm[:,:,0]==255) and np.all(orm[:,:,1]==np.asarray(rough)) and np.all(orm[:,:,2]==np.asarray(metal))
assert orm[:,:,2][glass].max()==0
for suffix in ['','_normal','_orm']:assert sha(O/('orsb1_hull'+suffix+'.png'))==sha(O/('gorsb1_hull'+suffix+'.png'))
for key,rec in maps.items():
 assert sha(rec['path'])==rec['sha256']
 with Image.open(rec['path']) as im:im.load();assert list(im.size)==rec['dimensions']
(W/'map_checks.json').write_text(json.dumps(dict(passed=True,normal_max_unit_error=float(np.max(np.abs(lengths-1))),flat_glass_normals=True,glass_metallic_zero=True,orm_channels_match=True,flight_and_loadout_maps_identical=True,dimensions=[4096,4096]),indent=2)+'\n')
launcher=(Path(os.environ['ART_PACK_REPOSITORY'])/'Coalition Fighters/Saber/tools/launch-saber-test.sh').read_text()
launch=D/'exports/launch-saber-test.sh';launch.write_text(launcher);launch.chmod(0o755);subprocess.run(['bash','-n',str(launch)],check=True)
shutil.copy2(__file__,W/'export_native.py')
print('Native model and mission passed. Repaired',len(edits),'UV faces; validated',sum(x['faces'] for x in stats),'native faces and all delivered maps.')
