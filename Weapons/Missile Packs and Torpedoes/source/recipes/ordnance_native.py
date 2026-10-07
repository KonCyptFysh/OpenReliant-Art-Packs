"""Lossless native chunk reader and isolated material/UV export for ordnance."""
from pathlib import Path
import struct,json,hashlib
import numpy as np
D=Path(__file__).resolve().parents[1]
W=D/'work/reconstruction_v1'
MAT='orord1_hull'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def chunks(raw):
 out=[];at=0;part=-1;lod=-1
 while at<len(raw):
  tag,size,count=struct.unpack_from('<HHH',raw,at)
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  end=at+6+size*count;assert end<=len(raw)
  out.append(dict(tag=tag,size=size,count=count,at=at,start=at+6,end=end,part=part,lod=lod,data=raw[at+6:end]));at=end
 assert at==len(raw);return out

def models(raw):
 out=[];desc={};metadata=[]
 for c in chunks(raw):
  data=c['data'];size=c['size'];count=c['count']
  if c['tag']==1:
   metadata=[dict(name=data[i*size:i*size+64].split(b'\0')[0].decode('latin1'),origin=list(struct.unpack_from('<3f',data,i*size+68)),part=i) for i in range(count)]
  if c['tag']==2:desc=metadata[c['part']]
  if c['tag']==4:
   item=dict(desc,lod=c['lod'],verts=[list(struct.unpack_from('<3f',data,i*size)) for i in range(count)],normals=[list(struct.unpack_from('<3f',data,i*size+12)) for i in range(count)],faces=[]);out.append(item)
  if c['tag']==3:
   for i in range(count):
    b=data[i*size:(i+1)*size];idx=list(struct.unpack_from('<3I',b,12));q=struct.unpack_from('<6f',b,24)
    item['faces'].append(dict(id=i,indices=idx,uv=[[q[j],q[j+3]] for j in range(3)],normal=list(struct.unpack_from('<3f',b,48)),fan=struct.unpack_from('<I',b,72)[0] if size>=80 else 0,hidden=bool((struct.unpack_from('<I',b,8)[0]&1) or (struct.unpack_from('<I',b,4)[0]&15)==1)))
 return out

def ratio(points,uv):
 e=points[1:]-points[0];n=np.cross(*e);nn=np.linalg.norm(n)
 if nn<1e-10:return 0
 n/=nn;t=e[0]/np.linalg.norm(e[0]);q=e@np.stack((t,np.cross(n,t)),axis=1);s=np.linalg.svd(np.linalg.solve(q,uv[1:]-uv[0]),compute_uv=False)
 return float(s[0]/max(s[1],1e-12))

def repaired(m,rgb):
 verts=np.array(m['verts']);faces=m['faces'];uv={f['id']:np.array(f['uv']) for f in faces};bad=[];ns={};records=[]
 for f in faces:
  p=verts[f['indices']];r=ratio(p,uv[f['id']]);n=np.cross(p[1]-p[0],p[2]-p[0]);ns[f['id']]=n/max(np.linalg.norm(n),1e-12)
  if r>12:bad.append(f['id'])
 remain=set(bad)
 while remain:
  group={min(remain)};remain-=group;changed=True
  while changed:
   changed=False
   for b in sorted(remain):
    if any(len(set(faces[b]['indices'])&set(faces[a]['indices']))>=2 and abs(np.dot(ns[b],ns[a]))>.995 for a in group):group.add(b);remain.remove(b);changed=True
  ids=sorted({i for fi in group for i in faces[fi]['indices']});p=verts[ids];mean=p.mean(0);_,_,vh=np.linalg.svd(p-mean,full_matrices=True);xy=(p-mean)@vh[:2].T
  # A consistent physical plane shares every edge within this island. Quiet existing
  # atlas material is reused; no painted symbols or hardware are stretched over walls.
  avg=np.mean(np.concatenate([uv[fi] for fi in group]),axis=0);x,y=np.clip((avg*1254).astype(int),0,1253);r,g,b=rgb[y,x]
  if r>g*1.45 and r>b*1.5 and r>.15:box=(1101,112,1162,178);kind='red paint'
  elif r>g*1.15 and g>b*1.2 and r>.10:box=(562,225,576,307);kind='bronze'
  elif b>r*1.2 and b>g*1.1:box=(797,109,850,184);kind='blue paint'
  else:box=(714,109,773,187);kind='steel'
  lo=xy.min(0);hi=xy.max(0);a,b,c,d=box;scale=min((c-a)/max(hi[0]-lo[0],1e-9),(d-b)/max(hi[1]-lo[1],1e-9));xy=(xy-(lo+hi)/2)*scale+[(a+c)/2,(b+d)/2];lookup={i:v/1254 for i,v in zip(ids,xy)}
  before=[];after=[]
  for fi in sorted(group):
   f=faces[fi];before.append(ratio(verts[f['indices']],uv[fi]));uv[fi]=np.array([lookup[i] for i in f['indices']]);after.append(ratio(verts[f['indices']],uv[fi]));assert after[-1]<1.03
  records.append(dict(part=m['part'],lod=m['lod'],faces=sorted(group),material=kind,atlas_box=box,max_before=max(before),max_after=max(after),method='isotropic planar island, original atlas quiet material'))
 return uv,records

def export(raw,parsed,out):
 data=bytearray(raw);audit=[];lookup={(m['part'],m['lod']):m for m in parsed}
 for c in chunks(raw):
  if c['tag']==6:
   for i in range(c['count']):
    a=c['start']+i*c['size'];data[a:a+64]=MAT.encode().ljust(64,b'\0')
  if c['tag']==3:
   m=lookup[c['part'],c['lod']]
   for f in m['faces']:
    q=m['new_uv'][f['id']];a=c['start']+f['id']*c['size']+24;struct.pack_into('<6f',data,a,*q[:,0],*q[:,1])
 # Prove every byte outside material names and face UV fields remains original.
 mask=bytearray(len(raw))
 for c in chunks(raw):
  if c['tag']==6:
   for i in range(c['count']):mask[c['start']+i*c['size']:c['start']+i*c['size']+64]=b'\1'*64
  if c['tag']==3:
   for i in range(c['count']):mask[c['start']+i*c['size']+24:c['start']+i*c['size']+48]=b'\1'*24
 assert all(a==b or mask[i] for i,(a,b) in enumerate(zip(raw,data)))
 Path(out).write_bytes(data)
 return dict(bytes=len(data),source_sha256=hashlib.sha256(raw).hexdigest(),export_sha256=sha(out),geometry_normals_flags_parts_attachments_animation_and_lod_topology_byte_exact=True)
