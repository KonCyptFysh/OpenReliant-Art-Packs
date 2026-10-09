import os
from pathlib import Path
import hashlib,json,shutil,struct,subprocess,numpy as np
from PIL import Image
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/nose_seam_v3'
MOD='103-basilisk-worn-v1';old=D/'exports/openreliant_v2/mods'/MOD;out=D/'exports/openreliant_v3/mods'/MOD
out.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=json.loads((W/'validation.json').read_text());assert sha(r['scene'])==r['scene_sha256']
for p in old.iterdir():shutil.copy2(p,out/p.name)
raw=(old/'Rus_basalisk.SHP').read_bytes();data=bytearray(raw);allowed=set();pos=0;part=lod=-1;names=[];edits=[];joins=[];stats=[]
def groups(fs):
 i=0
 while i<len(fs):
  end=i+fs[i]['remaining']+1;assert end<=len(fs)
  assert all(fs[j]['remaining']==end-j-1 for j in range(i,end));yield i,end;i=end
def matches(a,p,c):
 if a['kind']==1:ids=[a['vertices'][0],p['vertices'][2]];uv=[a['uv'][0],p['uv'][2]]
 else:assert a['kind'] in [2,3];ids=p['vertices'][1:];uv=p['uv'][1:]
 return ids==c['vertices'][:2] and np.max(np.abs(np.asarray(uv)-c['uv'][:2]))<=1e-6
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count
 if tag==1:names=[raw[start+i*size:start+i*size+64].split(b'\0')[0].decode().replace(' ','_') for i in range(count)]
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==3:
  assert size==80
  if names[part] in ['Basalisk','Basalisk_Cpit'] and lod==0:
   for edit in r['uv_repairs']:
    if edit['part']!=names[part]:continue
    i=edit['face'];at=start+i*size;ids=list(struct.unpack_from('<3I',raw,at+12));f=r['models'][names[part]]['faces'][i];assert sorted(ids)==sorted(f['vertices'])
    q=[f['uv'][f['vertices'].index(j)] for j in ids]
    struct.pack_into('<6f',data,at+24,*[a[0] for a in q],*[1-a[1] for a in q]);allowed.update(range(at+24,at+48));edits.append(dict(part=names[part],lod=lod,face=i))
  fs=[]
  for i in range(count):
   at=start+i*size;uv=np.asarray(struct.unpack_from('<6f',data,at+24)).reshape(2,3).T;kind,remaining=struct.unpack_from('<2I',data,at+72)
   fs.append(dict(vertices=list(struct.unpack_from('<3I',data,at+12)),uv=uv,kind=kind,remaining=remaining))
  orig_groups=list(groups(fs));segments=[]
  for first,last in orig_groups:
   seg=first
   for j in range(first+1,last):
    if not matches(fs[seg],fs[j-1],fs[j]):segments.append((seg,j));seg=j
   segments.append((seg,last))
  for first,last in segments:
   for j in range(first,last):
    remaining=last-j-1
    if remaining!=fs[j]['remaining']:
     at=start+j*size+76;struct.pack_into('<I',data,at,remaining);allowed.update(range(at,at+4));joins.append(dict(part=names[part],lod=lod,face=j,prior=fs[j]['remaining'],remaining=remaining));fs[j]['remaining']=remaining
  for first,last in groups(fs):
   for j in range(first+1,last):assert matches(fs[first],fs[j-1],fs[j])
  stats.append(dict(part=names[part],lod=lod,faces=count,all_shared_corner_uvs_match=True))
 pos=end
assert pos==len(raw)==len(data);diff=[i for i,(a,b) in enumerate(zip(raw,data)) if a!=b];assert all(i in allowed for i in diff);assert len(edits)==6 and sum(x['faces'] for x in stats)==1661
(out/'Rus_basalisk.SHP').write_bytes(data)
for p in old.glob('*.png'):assert sha(p)==sha(out/p.name)
assert raw[2290:2290+168]==data[2290:2290+168]
(out/'mod.ini').write_text((old/'mod.ini').read_text().replace('Red hull light spill restrained.','Red hull light spill restrained; front nose seam UV corrected.'))
report=dict(passed=True,source_sha256=sha(old/'Rus_basalisk.SHP'),output_sha256=sha(out/'Rus_basalisk.SHP'),uv_edits=edits,continuation_corrections=joins,detail_meshes=stats,changed_bytes=len(diff),allowed_changes='Only UVs on six finest-detail front nose triangles and required primitive continuations',all_1661_faces_checked=True,geometry_normals_lights_attachments_animation_collision_and_winding_byte_identical=True,all_texture_files_byte_identical=True,previous_18_machinery_uv_repairs_preserved=True,light_spill_refinement_preserved=True)
(W/'native_preservation.json').write_text(json.dumps(report,indent=2)+'\n')
checks=[];tool=os.environ['OPENRELIANT_SLTOOL']
for kind,name in [('shp','Rus_basalisk.SHP'),('dte','mission988.dte')]:
 c=subprocess.run([tool,kind,'check',str(out/name)],check=True,text=True,capture_output=True);checks.append(dict(file=name,exit_code=c.returncode,output=c.stdout+c.stderr,sha256=sha(out/name)))
(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
# Sample the upper island border at progressively coarser texture levels.
base=Image.open(out/'orbs1_hull.png').convert('RGB');levels=[]
for part,edge in r['atlas_edges'].items():
 for size in [4096,2048,1024,512,256]:
  im=np.asarray(base.resize((size,size),Image.Resampling.LANCZOS)).astype(float)/255;rec={'part':part,'texture_size':size}
  for name,u in [('before',edge['before_right']),('after',edge['after_right'])]:
   vs=np.linspace(.624,.700,600) if part=='Basalisk' else np.linspace(.673,.699,600)
   xs=np.rint(u*(size-1)).astype(int);ys=np.rint((1-vs)*(size-1)).astype(int);a=im[ys,xs];red=(a[:,0]>1.6*a[:,1])&(a[:,0]>1.4*a[:,2])&(a[:,0]>.25);rec[name+'_red_samples']=int(red.sum())
  assert rec['after_red_samples']==0,rec
  levels.append(rec)
(W/'seam_sampling_checks.json').write_text(json.dumps(dict(passed=True,upper_front_right_edge_red_samples=levels,all_maps_byte_identical=True),indent=2)+'\n')
print(json.dumps(dict(native=report['output_sha256'],uv_faces=len(edits),continuation_corrections=len(joins),samples=levels),indent=2))
