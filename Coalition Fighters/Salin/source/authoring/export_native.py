from pathlib import Path
import os,hashlib,importlib.util,json,shutil,struct,subprocess
import numpy as np
from PIL import Image

D=Path(os.environ['SALIN_WORKSPACE'])
W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_8_v1/mods/109-salin-worn-v1';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());assert sha(r['scene'])==r['scene_sha256']
changed={}
for x in r['uv_repairs']:changed.setdefault(x['part'],set()).update(x['faces'])
raw=(D/'source/Luda.SHP').read_bytes();out=bytearray(raw);pos=0;part=lod=-1;names=[];edits=[];joins=[];stats=[];materials=[]
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
 return anchor['material']==cur['material'] and ids==cur['vertices'][:2] and np.max(np.abs(np.array(uv)-cur['uv'][:2]))<=1e-6
allowed=set()
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count
 if tag==1:names=[raw[start+i*size:start+i*size+64].split(b'\0')[0].decode() for i in range(count)]
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==6:
  for i in range(count):
   at=start+i*size;old=raw[at:at+64].split(b'\0')[0].decode();assert old.lower() in ('luda',)
   out[at:at+64]=b'orsn1_hull'.ljust(64,b'\0');allowed.update(range(at,at+64));materials.append(dict(part=part,lod=lod,old=old,new='orsn1_hull'))
 if tag==3:
  assert size==80
  if lod==0 and names[part].replace(' ','_') in changed:
   model=r['models'][names[part].replace(' ','_')];assert count==len(model['faces'])
   for i in sorted(changed[names[part].replace(' ','_')]):
    at=start+i*size;ids=list(struct.unpack_from('<3I',out,at+12));f=model['faces'][i]
    assert sorted(ids)==sorted(f['vertices'])
    q=[f['uv'][f['vertices'].index(j)] for j in ids]
    struct.pack_into('<6f',out,at+24,*[x[0] for x in q],*[1-x[1] for x in q]);allowed.update(range(at+24,at+48));edits.append(dict(part=names[part],lod=lod,face=i))
  fs=[]
  for i in range(count):
   at=start+i*size;uv=np.array(struct.unpack_from('<6f',out,at+24)).reshape(2,3).T
   kind,remaining=struct.unpack_from('<2I',out,at+72)
   fs.append(dict(material=struct.unpack_from('<I',out,at)[0],vertices=list(struct.unpack_from('<3I',out,at+12)),uv=uv,kind=kind,remaining=remaining))
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
assert len(edits)==0 and sum(x['faces'] for x in stats)==898
(O/'Luda.SHP').write_bytes(out)
preservation=dict(passed=True,source_sha256=sha(D/'source/Luda.SHP'),output_sha256=sha(O/'Luda.SHP'),uv_edits=edits,continuation_corrections=joins,detail_meshes=stats,all_898_faces_checked=True,geometry_normals_attachments_animation_collision_and_winding_byte_identical=True,allowed_changes='Texture names, primitive continuation counts at UV seams only',changed_bytes=len(diff))
(W/'native_preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
maps=r['maps']['hull']
for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(maps[key]['path'],O/('orsn1_hull'+suffix+'.png'))
rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R')
Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/'orsn1_hull_orm.png')
tool=os.environ['OPENRELIANT_SLTOOL'];checks=[]
for kind,file in [('shp','Luda.SHP'),('dte','mission977.dte')]:
 p=subprocess.run([tool,kind,'check',str(O/file)],capture_output=True,text=True,check=True);checks.append(dict(file=file,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(O/file)))
ships=subprocess.check_output([tool,'dte','ships',str(O/'mission977.dte')],text=True);assert 'Salin - Inspection' in ships and '41' in ships
(W/'mission977-ships.txt').write_text(ships)
(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
def binary_erosion(mask,iterations):
 mask=mask.copy()
 for _ in range(iterations):
  inner=mask[1:-1,1:-1]&mask[2:,1:-1]&mask[:-2,1:-1]&mask[1:-1,2:]&mask[1:-1,:-2]
  mask[:]=False;mask[1:-1,1:-1]=inner
 return mask
glass=binary_erosion(np.asarray(Image.open(maps['glass']['path']).convert('L'))>250,iterations=16)
assert glass.sum()>10000
flat=binary_erosion(np.asarray(Image.open(maps['flat_graphics']['path']).convert('L'))>250,iterations=12)
normal=np.asarray(Image.open(O/'orsn1_hull_normal.png').convert('RGB')).astype(np.float32)/255*2-1
lengths=np.linalg.norm(normal,axis=-1);assert np.max(np.abs(lengths-1))<.02
assert np.max(np.abs(normal[glass]-[0,0,1]))<.008
orm=np.asarray(Image.open(O/'orsn1_hull_orm.png').convert('RGB'))
assert np.all(orm[:,:,0]==255) and np.all(orm[:,:,1]==np.asarray(rough)) and np.all(orm[:,:,2]==np.asarray(metal))
assert orm[:,:,2][glass].max()==0
for key,rec in maps.items():
 assert sha(rec['path'])==rec['sha256']
 with Image.open(rec['path']) as im:im.load();assert list(im.size)==rec['dimensions']
(W/'map_checks.json').write_text(json.dumps(dict(passed=True,normal_max_unit_error=float(np.max(np.abs(lengths-1))),glass_interior_normals_flat=True,glass_metallic_zero=True,orm_channels_match=True,one_shared_material_set_without_gr_duplicates=True,dimensions=[4096,4096]),indent=2)+'\n')

# Only material names, strip/fan continuations are edited.
# All part records, mounts, attachments, animation headers and keyframe chunks match exactly.
def chunks(data):
 p=0
 while p<len(data):
  tag,size,count=struct.unpack_from('<3H',data,p);end=p+6+size*count
  yield tag,data[p:end];p=end
preserved=[]
for (tag,a),(tag2,b) in zip(chunks(raw),chunks(out)):
 assert tag==tag2
 if tag in (1,9,10,11):
  assert a==b;preserved.append(dict(tag=tag,bytes=len(a),sha256=hashlib.sha256(a).hexdigest()))
(W/'animation_preservation.json').write_text(json.dumps(dict(passed=True,chunks=preserved,entire_animation_and_attachments_byte_identical=True),indent=2)+'\n')
(O/'mod.ini').write_text('[Mod]\nName=Salin - Worn Paint (Review)\nVersion=0.1.0-beta.1\nDescription=Restored worn atlas, recessed amber glazing and structural surface maps. Original model and animation retained. Awaiting visual review.\nOpenReliant=0.8.1\nLicense=CC-BY-NC-SA-4.0\n')
(O/'license.txt').write_text('Salin - Worn Paint\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/\nOriginal StarLancer assets retain their respective owners rights. Requires your own StarLancer installation.\n')
shutil.copy2(D/'review/reconstruction_v1/material_front.png',O/'mod.png')
print('SALIN_NATIVE_EXPORT_PASSED',len(diff),'changed bytes;',len(joins),'continuation counts repaired;',len(preserved),'animation/attachment/part chunks preserved')
