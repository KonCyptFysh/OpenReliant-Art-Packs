from pathlib import Path
import struct,numpy as np,json
D=Path('${RELIANT_WORKSPACE}');W=D/'work/alignment_v3';S=D/'history/stages/pre_alignment_v3/exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
def parse(path):
 raw=path.read_bytes();pos=0;parts=[];pi=li=-1
 while pos<len(raw):
  tag,size,count=struct.unpack_from('<3H',raw,pos);st=pos+6
  if tag==1:
   for k in range(count):
    at=st+k*size;parts.append(dict(name=raw[at:at+64].split(b'\0')[0].decode(),origin=np.array(struct.unpack_from('<3f',raw,at+68)),lods=[]))
  if tag==2:pi+=1;li=-1
  if tag==4:li+=1;parts[pi]['lods'].append(dict(vertices=np.array([struct.unpack_from('<3f',raw,st+k*size) for k in range(count)]),faces=[]))
  if tag==3:
   for k in range(count):
    at=st+k*size;parts[pi]['lods'][li]['faces'].append(dict(id=k,at=at,mat=struct.unpack_from('<I',raw,at)[0],ids=list(struct.unpack_from('<3I',raw,at+12)),uv=np.array(struct.unpack_from('<6f',raw,at+24)).reshape(2,3).T*256,kind=struct.unpack_from('<I',raw,at+72)[0],rem=struct.unpack_from('<I',raw,at+76)[0],norm=np.array(struct.unpack_from('<3f',raw,at+48))))
  pos=st+size*count
 return raw,parts
if __name__=='__main__':
 raw,parts=parse(S/'Reliant.SHP');out=[]
 for pi,p in enumerate(parts):
  if 'DEST' in p['name']:continue
  for li,l in enumerate(p['lods'][:1]):
   for f in l['faces']:
    v=l['vertices'][f['ids']];du=np.linalg.det((f['uv'][1:]-f['uv'][0]));area=np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2
    if abs(du)<.2 and area>10000:out.append(dict(part=pi,face=f['id'],mat=f['mat'],uv=f['uv'].round(3).tolist(),uv_area=du/2,area=area,world=(v.mean(0)+p['origin']).round().tolist()))
 (W/'degenerate-uv.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
