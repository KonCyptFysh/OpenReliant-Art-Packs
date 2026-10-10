from pathlib import Path
import os,struct,json,hashlib
D=Path(os.environ['SALIN_WORKSPACE'])
W=D/"work/reconstruction_v1"
def write(p,j):p.write_text(json.dumps(j,indent=2)+"\n")
raw=(D/'source/Luda.SHP').read_bytes();pos=0;parts=[];part=-1;lod=-1;chunks=[]
while pos<len(raw):
 t,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count;data=raw[start:end];chunks.append(dict(tag=t,size=size,count=count,offset=pos,sha256=hashlib.sha256(data).hexdigest()))
 if t==1:
  for i in range(count):
   q=data[i*size:(i+1)*size];parts.append(dict(index=i,name=q[:64].split(b'\0')[0].decode(),origin=list(struct.unpack_from('<3f',q,68)),parent=struct.unpack_from('<i',q,148)[0],mount=list(struct.unpack_from('<3f',q,152)),orientation=list(struct.unpack_from('<9f',q,164)),still=list(struct.unpack_from('<3I',q,200)),lods=[],tracks=[],attachments=[]))
 if t==2:part+=1;lod=-1
 if t==4:
  lod+=1;parts[part]['lods'].append(dict(vertices=[list(struct.unpack_from('<3f',data,i*size)) for i in range(count)],normals=[list(struct.unpack_from('<3f',data,i*size+12)) for i in range(count)]))
 if t==3:
  fs=[]
  for i in range(count):
   a=i*size;uv=struct.unpack_from('<6f',data,a+24);flags=struct.unpack_from('<2I',data,a+4);fs.append(dict(id=i,material=struct.unpack_from('<I',data,a)[0],vertices=list(struct.unpack_from('<3I',data,a+12)),uv=[[uv[k],1-uv[k+3]] for k in range(3)],normal=list(struct.unpack_from('<3f',data,a+48)),kind=struct.unpack_from('<I',data,a+72)[0],remaining=struct.unpack_from('<I',data,a+76)[0],hidden=bool(flags[1]&1 or flags[0]&15==1)))
  parts[part]['lods'][lod]['faces']=fs
 if t==10:
  for i in range(count):
   q=data[i*size:(i+1)*size];parts[part]['tracks'].append(dict(name=q[6:24].split(b'\0')[0].decode(),length=struct.unpack_from('<i',q)[0],mode=struct.unpack_from('<h',q,4)[0],keys=[]))
 if t==11:parts[part]['tracks'][-1]['keys']=[dict(time=struct.unpack_from('<i',data,i*size)[0],angles=list(struct.unpack_from('<3f',data,i*size+4)),offset=list(struct.unpack_from('<3f',data,i*size+16))) for i in range(count)]
 if t==9:
  for i in range(count):
   q=data[i*size:(i+1)*size];parts[part]['attachments'].append(dict(kind=struct.unpack_from('<i',q)[0],raw_hex=q.hex()))
 pos=end
assert pos==len(raw) and len(parts)==1
write(D/'source/native_parts.json',parts)
write(W/'native-chunks.json',chunks)
