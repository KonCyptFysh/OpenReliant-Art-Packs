import os
from pathlib import Path
import hashlib,json,shutil,struct,subprocess,numpy as np
from PIL import Image
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/glass_gun_v4';MOD='103-basilisk-worn-v1';old=D/'exports/openreliant_v3/mods'/MOD;out=D/'exports/openreliant_v4/mods'/MOD
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();r=json.loads((W/'validation.json').read_text());assert sha(r['scene'])==r['scene_sha256'];out.mkdir(parents=True,exist_ok=True)
for p in old.iterdir():shutil.copy2(p,out/p.name)
raw=(old/'Rus_basalisk.SHP').read_bytes();pos=0;part=lod=-1;chunks=[];edits=[];joins=[];stats=[];preserved=[];names=[]
def groups(fs):
 i=0
 while i<len(fs):
  end=i+fs[i]['remaining']+1;assert end<=len(fs);assert all(fs[j]['remaining']==end-j-1 for j in range(i,end));yield i,end;i=end
def matches(a,p,c):
 if a['kind']==1:ids=[a['vertices'][0],p['vertices'][2]];uv=[a['uv'][0],p['uv'][2]]
 else:assert a['kind'] in [2,3];ids=p['vertices'][1:];uv=p['uv'][1:]
 return a['material']==c['material'] and ids==c['vertices'][:2] and np.max(np.abs(np.asarray(uv)-c['uv'][:2]))<=1e-6
while pos<len(raw):
 tag,size,count=struct.unpack_from('<3H',raw,pos);end=pos+6+size*count;orig=raw[pos+6:end];data=bytearray(orig);allow=set();oldcount=count
 if tag==1:names=[orig[i*size:i*size+64].split(b'\0')[0].decode().replace(' ','_') for i in range(count)]
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==3:
  assert size==80
  if names[part]=='Basalisk' and lod==0:
   for edit in r['uv_repairs']:
    i=edit['face'];at=i*size;ids=list(struct.unpack_from('<3I',orig,at+12));f=r['models']['Basalisk']['faces'][i];assert sorted(ids)==sorted(f['vertices']);q=[f['uv'][f['vertices'].index(j)] for j in ids]
    struct.pack_into('<I',data,at,1);struct.pack_into('<6f',data,at+24,*[a[0] for a in q],*[1-a[1] for a in q]);allow.update(range(at,at+4));allow.update(range(at+24,at+48));edits.append(dict(part=names[part],lod=lod,face=i,material=1))
  fs=[]
  for i in range(count):
   at=i*size;uv=np.asarray(struct.unpack_from('<6f',data,at+24)).reshape(2,3).T;kind,remaining=struct.unpack_from('<2I',data,at+72);fs.append(dict(vertices=list(struct.unpack_from('<3I',data,at+12)),uv=uv,kind=kind,remaining=remaining,material=struct.unpack_from('<I',data,at)[0]))
  segments=[]
  for first,last in list(groups(fs)):
   seg=first
   for j in range(first+1,last):
    if not matches(fs[seg],fs[j-1],fs[j]):segments.append((seg,j));seg=j
   segments.append((seg,last))
  for first,last in segments:
   for j in range(first,last):
    rem=last-j-1
    if rem!=fs[j]['remaining']:
     at=j*size+76;struct.pack_into('<I',data,at,rem);allow.update(range(at,at+4));joins.append(dict(part=names[part],lod=lod,face=j,before=fs[j]['remaining'],after=rem));fs[j]['remaining']=rem
  for first,last in groups(fs):
   for j in range(first+1,last):assert matches(fs[first],fs[j-1],fs[j])
  stats.append(dict(part=names[part],lod=lod,faces=count,shared_corner_uvs_and_materials_match=True))
 if tag==6 and names[part]=='Basalisk' and lod==0:
  assert size==64 and count==1 and orig.split(b'\0')[0]==b'orbs1_hull';data+=b'orbs2_gun'.ljust(64,b'\0');count=2
 else:
  assert len(data)==len(orig);assert all(i in allow for i,(a,b) in enumerate(zip(orig,data)) if a!=b)
 if bytes(data)==orig:preserved.append(dict(tag=tag,part=part,lod=lod,count=count,sha256=hashlib.sha256(orig).hexdigest()))
 chunks.append(struct.pack('<3H',tag,size,count)+data);pos=end
assert pos==len(raw);output=b''.join(chunks);assert len(output)==len(raw)+64;assert len(edits)==8;assert sum(x['faces'] for x in stats)==1661
(out/'Rus_basalisk.SHP').write_bytes(output)
for name,stem in [('hull','orbs1_hull'),('gun','orbs2_gun')]:
 maps=r['maps'][name]
 for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(maps[key]['path'],out/(stem+suffix+'.png'))
 rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(out/(stem+'_orm.png'))
 for suffix in ['','_normal','_orm']:shutil.copy2(out/(stem+suffix+'.png'),out/('g'+stem+suffix+'.png'));assert sha(out/(stem+suffix+'.png'))==sha(out/('g'+stem+suffix+'.png'))
assert sha(out/'orbs1_hull.png')==sha(old/'orbs1_hull.png')
bx,by,n,_=r['gun_tile'];priorbase=np.asarray(Image.open(old/'orbs1_hull.png').convert('RGB'));gunbase=np.asarray(Image.open(out/'orbs2_gun.png').convert('RGB'));assert np.array_equal(gunbase,priorbase[by:by+n,bx:bx+n])
mask=np.asarray(Image.open(r['maps']['hull']['glazing_edit_mask']['path']).convert('L'))
checks={}
prior_maps=json.loads((D/'work/nose_seam_v3/validation.json').read_text())['maps']['hull']
for key in ['roughness','metallic','normal']:
 a=np.asarray(Image.open(r['maps']['hull'][key]['path']).convert('RGB'));b=np.asarray(Image.open(prior_maps[key]['path']).convert('RGB'));difference=np.max(np.abs(a.astype(int)-b.astype(int)),axis=2)
 assert difference[mask==0].max()<=1,(key,difference[mask==0].max());checks[key+'_outside_glazing_max_change']=int(difference[mask==0].max())
glass=np.asarray(Image.open(r['maps']['hull']['glass']['path']).convert('L'))>254
normal=np.asarray(Image.open(out/'orbs1_hull_normal.png').convert('RGB')).astype(float)/255*2-1;orm=np.asarray(Image.open(out/'orbs1_hull_orm.png').convert('RGB'));assert np.max(np.abs(normal[glass]-[0,0,1]))<.008;assert orm[:,:,1][glass].max()<=43;assert orm[:,:,2][glass].max()==0
for stem in ['orbs1_hull','orbs2_gun']:
 a=np.asarray(Image.open(out/(stem+'_normal.png')).convert('RGB')).astype(float)/255*2-1;err=float(np.max(np.abs(np.linalg.norm(a,axis=2)-1)));assert err<.02;checks[stem+'_normal_max_unit_error']=err
(out/'mod.ini').write_text((old/'mod.ini').read_text().replace('front nose seam UV corrected.','front nose seam UV corrected, matching reflective gun housing and frame-fitted glass.'))
report=dict(passed=True,source_sha256=sha(old/'Rus_basalisk.SHP'),output_sha256=sha(out/'Rus_basalisk.SHP'),material_and_uv_edits=edits,new_material='orbs2_gun',new_material_scope='Basalisk finest detail, eight forward gun-housing side triangles only',continuation_corrections=joins,detail_meshes=stats,all_1661_faces_checked=True,other_native_records_byte_identical=True,preserved_chunks=preserved,prior_uv_repairs_and_red_light_preserved=True,geometry_normals_attachments_animation_collision_and_winding_preserved=True)
(W/'native_preservation.json').write_text(json.dumps(report,indent=2)+'\n')
tool=os.environ['OPENRELIANT_SLTOOL'];native=[]
for kind,name in [('shp','Rus_basalisk.SHP'),('dte','mission988.dte')]:
 p=subprocess.run([tool,kind,'check',str(out/name)],capture_output=True,text=True,check=True);native.append(dict(file=name,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(out/name)))
info=subprocess.run([tool,'shp','info',str(out/'Rus_basalisk.SHP')],capture_output=True,text=True,check=True).stdout;assert 'orbs2_gun' in info;(W/'native_model_info.txt').write_text(info)
(W/'native_checks.json').write_text(json.dumps(native,indent=2)+'\n');(W/'map_checks.json').write_text(json.dumps(dict(passed=True,base_colour_unchanged=True,gun_colour_matches_exact_source_crop=True,glass_normals_flat=True,glass_roughness_range=[int(orm[:,:,1][glass].min()),int(orm[:,:,1][glass].max())],glass_metallic_zero=True,**checks),indent=2)+'\n')
print('BASILISK_V4_NATIVE_MAP_CHECKS_PASSED',len(edits),'gun faces',len(joins),'continuation changes',len(list(out.iterdir())),'runtime files',flush=True)
