import os
from pathlib import Path
import json,struct,hashlib,shutil,subprocess
import numpy as np
from PIL import Image, ImageFilter
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/seams_v2';O=D/'exports/openreliant_0_8_v1/mods/111-haidar-worn-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());assert sha(r['scene'])==r['scene_sha256'];raw=(D/'source/Chin_Han.SHP').read_bytes();selected={x['part']:set(x['faces']) for x in r['uv_repairs']}
def chunks(data):
 at=0
 while at<len(data):
  t,s,n=struct.unpack_from('<3H',data,at);end=at+6+s*n;yield t,s,n,data[at+6:end];at=end
 assert at==len(data)
def groups(fs):
 i=0
 while i<len(fs):
  end=i+fs[i]['remaining']+1;assert end<=len(fs) and all(fs[j]['remaining']==end-j-1 for j in range(i,end));yield i,end;i=end
def matches(a,b,c):
 if a['kind']==1:ids=[a['ids'][0],b['ids'][2]];uv=[a['uv'][0],b['uv'][2]]
 else:assert a['kind'] in [2,3];ids=b['ids'][1:];uv=b['uv'][1:]
 return a['material']==c['material'] and ids==c['ids'][:2] and np.max(np.abs(np.array(uv)-c['uv'][:2]))<=1e-6
out=[];part=lod=-1;names=[];faceedits=[];joins=[];stats=[];preserved=[];materials=[]
for tag,size,count,data in chunks(raw):
 old=data;new=bytearray(data);allowed=set();newcount=count
 if tag==1:names=[data[i*size:i*size+64].split(b'\0')[0].decode().replace(' ','_') for i in range(count)]
 if tag==2:part+=1;lod=-1
 if tag==4:lod+=1
 if tag==6:
  assert size==64 and count==1 and data[:64].split(b'\0')[0]==b'brit2';new=bytearray(b'orhd1_hull'.ljust(64,b'\0'))
  if lod==0 and names[part] in selected:new.extend(b'orhd2_repair'.ljust(64,b'\0'));newcount=2
  materials.append(dict(part=names[part],lod=lod,count=newcount))
 elif tag==3:
  assert size==80
  if lod==0 and names[part] in selected:
   model=r['models'][names[part]]
   for fi in sorted(selected[names[part]]):
    at=fi*size;ids=list(struct.unpack_from('<3I',new,at+12));f=model['faces'][fi];assert sorted(ids)==sorted(f['vertices']) and f['material']==1;q=[f['uv'][f['vertices'].index(j)] for j in ids];struct.pack_into('<I',new,at,1);struct.pack_into('<6f',new,at+24,*[v[0] for v in q],*[1-v[1] for v in q]);allowed.update(range(at,at+4));allowed.update(range(at+24,at+48));faceedits.append(dict(part=names[part],lod=lod,face=fi,new_material='orhd2_repair'))
  fs=[]
  for fi in range(count):
   at=fi*size;kind,remaining=struct.unpack_from('<2I',new,at+72);fs.append(dict(material=struct.unpack_from('<I',new,at)[0],ids=list(struct.unpack_from('<3I',new,at+12)),uv=np.array(struct.unpack_from('<6f',new,at+24)).reshape(2,3).T,kind=kind,remaining=remaining))
  oldgroups=list(groups(fs));segments=[]
  for first,last in oldgroups:
   start=first
   for j in range(first+1,last):
    if not matches(fs[start],fs[j-1],fs[j]):segments.append((start,j));start=j
   segments.append((start,last))
  for first,last in segments:
   for j in range(first,last):
    rem=last-j-1
    if rem!=fs[j]['remaining']:at=j*size+76;struct.pack_into('<I',new,at,rem);allowed.update(range(at,at+4));joins.append(dict(part=names[part],lod=lod,face=j,prior=fs[j]['remaining'],remaining=rem));fs[j]['remaining']=rem
  for first,last in groups(fs):
   for j in range(first+1,last):assert matches(fs[first],fs[j-1],fs[j])
  assert all(i in allowed for i,(a,b) in enumerate(zip(old,new)) if a!=b)
  stats.append(dict(part=names[part],lod=lod,faces=count,shared_corner_uvs_match=True))
 else:assert old==new;preserved.append(dict(tag=tag,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 out.append(struct.pack('<3H',tag,size,newcount)+new)
output=b''.join(out);assert len(faceedits)==sum(map(len,selected.values())) and sum(x['faces'] for x in stats)==1349
(O/'Chin_Han.SHP').write_bytes(output)
report=dict(passed=True,source_sha256=sha(D/'source/Chin_Han.SHP'),output_sha256=sha(O/'Chin_Han.SHP'),uv_edits=faceedits,continuation_corrections=joins,detail_meshes=stats,material_tables=materials,preserved_chunks=preserved,geometry_normals_attachments_animation_collision_and_winding_byte_identical=True,allowed_changes='Selected LOD0 face UVs/material indices, texture tables, and primitive continuation counts',source_bytes=len(raw),output_bytes=len(output),all_1349_faces_checked=True)
(W/'native_preservation.json').write_text(json.dumps(report,indent=2)+'\n')
mapchecks={}
for kind,prefix in [('hull','orhd1_hull'),('repair','orhd2_repair')]:
 maps=r['maps'][kind]
 for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(maps[key]['path'],O/(prefix+suffix+'.png'))
 rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/(prefix+'_orm.png'))
 norm=np.asarray(Image.open(O/(prefix+'_normal.png')).convert('RGB')).astype(np.float32)/127.5-1;err=np.abs(np.linalg.norm(norm,axis=-1)-1);assert err.max()<.02
 for key,rec in maps.items():assert sha(rec['path'])==rec['sha256']
 orm=np.asarray(Image.open(O/(prefix+'_orm.png')));assert np.all(orm[:,:,0]==255) and np.array_equal(orm[:,:,1],rough) and np.array_equal(orm[:,:,2],metal)
 mapchecks[kind]={'dimensions':list(rough.size),'normal_max_unit_error':float(err.max()),'orm_channels_exact':True}
 if kind=='hull':
  g=np.asarray(Image.open(maps['glass']['path']).convert('L'));seal=np.asarray(Image.open(maps['seal']['path']).convert('L'));core=np.asarray(Image.fromarray((g==255).astype(np.uint8)*255).filter(ImageFilter.MinFilter(9)))==255;edge=(g>0)|(seal>0);angles=np.degrees(np.arccos(np.clip(norm[:,:,2]/np.linalg.norm(norm,axis=-1),-1,1)));assert angles[edge].max()<.5;col=np.asarray(Image.open(O/(prefix+'.png')).convert('RGB'));assert np.ptp(col[core],axis=0).max()==0 and orm[:,:,2][core].max()==0;assert np.ptp(orm[:,:,1][core])==0
  old=json.loads((D/'work/reconstruction_v1/validation.json').read_text())['maps']['hull'];locality={}
  footprint=np.asarray(Image.open(maps['glazing_edit_mask']['path']).convert('L'))>0
  for key in ['basecolor','normal','roughness','metallic']:
   a=np.asarray(Image.open(old[key]['path']).convert('RGB')).astype(int);b=np.asarray(Image.open(maps[key]['path']).convert('RGB')).astype(int);allow=g>0 if key=='basecolor' else footprint;delta=np.max(np.abs(a-b),axis=-1);assert delta[~allow].max()<=1,(key,int(delta[~allow].max()));locality[key]=int(delta[~allow].max())
  mapchecks[kind].update(glass_interior_colour=col[core][0].tolist(),glass_roughness=int(orm[:,:,1][core][0]),glass_edge_max_degrees=float(angles[edge].max()),glass_and_gasket_normals_flat=True,non_glass_max_channel_change=locality)
(W/'map_checks.json').write_text(json.dumps(dict(passed=True,materials=mapchecks,duplicate_colour_textures=False),indent=2)+'\n')
tool=os.environ['OPENRELIANT_SLTOOL'];checks=[]
for kind,file in [('shp','Chin_Han.SHP'),('dte','mission975.dte')]:
 p=subprocess.run([tool,kind,'check',str(O/file)],text=True,capture_output=True,check=True);checks.append(dict(file=file,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(O/file)))
ships=subprocess.check_output([tool,'dte','ships',str(O/'mission975.dte')],text=True);assert 'Haidar - Inspection' in ships and '39' in ships;(W/'mission975-ships.txt').write_text(ships);(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(O/'mod.ini').write_text('[Mod]\nName=Haidar - Worn Paint (Review 1.1)\nVersion=0.1.0-beta.1\nDescription=Continuous nose and collar panels, clean undivided inset glass with flat optical normals. Awaiting user review.\nOpenReliant=0.8.1\nLicense=CC-BY-NC-SA-4.0\n');shutil.copy2(R/'material_front.png' if False else D/'review/seams_v2/material_front.png',O/'mod.png')
print('HAIDAR_V2_NATIVE_MAP_CHECKS_PASSED',len(faceedits),'UV/material faces,',len(joins),'continuation repairs')
