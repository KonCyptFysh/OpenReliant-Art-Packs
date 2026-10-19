from pathlib import Path
import struct,json,collections,numpy as np
D=Path('${RELIANT_WORKSPACE}');W=D/'work/refinement_v2';B=D/'history/stages/pre_surface_v2/exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';O=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
nozzles=json.loads((D/'work/reconstruction_v1/nozzle-audit.json').read_text())['nozzles']
reports=[]
for fname in ['Reliant.SHP','Reliant_destback.SHP','Allied_Cap_Gun.SHP','13_al_STUR.SHP']:
 original=(B/fname if (B/fname).exists() else D/'source'/fname).read_bytes();out=bytearray(original);pos=0;pi=li=-1;vertices=None;uv_changes=[];join_changes=0;names=[];allowed=set();core_report=[]
 while pos<len(out):
  t,size,count=struct.unpack_from('<3H',out,pos);start=pos+6;end=start+size*count
  if t==2:pi+=1;li=-1
  if t==4:li+=1;vertices=np.array([struct.unpack_from('<3f',out,start+i*size) for i in range(count)])
  if t==6 and fname in ['Allied_Cap_Gun.SHP','13_al_STUR.SHP']:
   for i in range(count):
    off=start+i*size;name=out[off:off+64].split(b'\0')[0].decode();new={'all_trt':'orr_cgun','missiles':'orr_sgun'}.get(name.lower())
    if new:out[off:off+64]=new.encode().ljust(64,b'\0');allowed.update(range(off,off+64));names.append([name,new])
  if t==3:
   fs=[]
   for i in range(count):
    at=start+i*size;uv=np.array(struct.unpack_from('<6f',out,at+24)).reshape(2,3).T*256
    fs.append(dict(id=i,mat=struct.unpack_from('<I',out,at)[0],ids=list(struct.unpack_from('<3I',out,at+12)),uv=uv,normal=np.array(struct.unpack_from('<3f',out,at+48)),kind=struct.unpack_from('<I',out,at+72)[0],remaining=struct.unpack_from('<I',out,at+76)[0]))
   before=[f['uv'].copy() for f in fs]
   if fname in ['Reliant.SHP','Reliant_destback.SHP']:
    edges=collections.defaultdict(list);parent=list(range(count*3))
    def root(i):
     while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
     return i
    def union(a,b):parent[root(a)]=root(b)
    # First join corners that already have identical UVs at a vertex.
    corners={}
    for f in fs:
     for j,v in enumerate(f['ids']):
      key=(f['mat'],v,*np.round(f['uv'][j],3));idx=f['id']*3+j
      if key in corners:union(idx,corners[key])
      else:corners[key]=idx
     for j in range(3):
      k=(j+1)%3;a,b=f['ids'][j],f['ids'][k]
      if a>b:a,b=b,a;j,k=k,j
      edges[a,b].append((f,j,k))
    for edge,pair in edges.items():
     if len(pair)!=2:continue
     f,j,k=pair[0];g,u,v=pair[1]
     if f['mat']!=2 or g['mat']!=2:continue
     a=f['uv'][[j,k]];b=g['uv'][[u,v]];delta=np.linalg.norm(a-b,axis=1);alluv=np.r_[a,b];lo=alluv.min(0);hi=alluv.max(0)
     radiator=pi in [16,17,18,23] and lo[0]>=0 and hi[0]<89 and lo[1]>115 and hi[1]<256 and max(delta)<20
     petals=pi==19 and hi[0]<38 and lo[1]>129 and max(delta)<2
     engine_shell=pi==19 and lo[0]>157 and hi[0]<184 and 64<lo[1] and hi[1]<144 and max(delta)<6
     if max(delta)>.06 and (radiator or petals or engine_shell):union(f['id']*3+j,g['id']*3+u);union(f['id']*3+k,g['id']*3+v)
    groups=collections.defaultdict(list)
    for f in fs:
     for j in range(3):groups[root(f['id']*3+j)].append((f,j))
    for members in groups.values():
     avg=np.mean([f['uv'][j] for f,j in members],axis=0)
     for f,j in members:f['uv'][j]=avg
    # Align disk artwork to the ORIGINAL exhaust anchor, never relocate the effect.
    if pi==19:
     for q in nozzles:
      chosen=[]
      for f in fs:
       pts=vertices[f['ids']];c=pts.mean(0)
       if f['mat']==0 and f['normal'][2]<-.99 and abs(c[2]-q['back'])<3 and np.linalg.norm(c[:2]-q['center'])<q['radius']:chosen.append(f)
      if chosen:
       xy=np.concatenate([vertices[f['ids'],:2] for f in chosen]);old=np.concatenate([f['uv'] for f in chosen]);coef=np.linalg.lstsq(np.c_[xy,np.ones(len(xy))],old,rcond=None)[0];at=np.r_[q['center'],1]@coef
       for f in chosen:f['uv']=(np.c_[vertices[f['ids'],:2],np.ones(3)]@coef-at)*.88+[107,15]
       core_report.append(dict(engine=q['name'],lod=li,old_anchor_uv=at.tolist(),new_anchor_uv=[107,15],faces=[f['id'] for f in chosen]))
   for f,old in zip(fs,before):
    if np.max(abs(f['uv']-old))>1e-5:
     at=start+f['id']*size+24;struct.pack_into('<6f',out,at,*(f['uv']/256).T.ravel());allowed.update(range(at,at+24));uv_changes.append(dict(part=pi,lod=li,face=f['id'],before=old.tolist(),after=f['uv'].tolist()))
   # Split existing strips only where a changed mapping stops sharing UVs.
   first=0
   while first<count:
    last=first+fs[first]['remaining']+1;seg=first;segments=[]
    for j in range(first+1,last):
     anchor,prev,cur=fs[seg],fs[j-1],fs[j]
     ids=[anchor['ids'][0],prev['ids'][2]] if anchor['kind']==1 else prev['ids'][1:]
     uv=[anchor['uv'][0],prev['uv'][2]] if anchor['kind']==1 else prev['uv'][1:]
     if ids!=cur['ids'][:2] or np.max(np.abs(np.array(uv)-cur['uv'][:2]))>1e-4:segments.append((seg,j));seg=j
    segments.append((seg,last))
    for a,b in segments:
     for j in range(a,b):
      if fs[j]['remaining']!=b-j-1:
       at=start+j*size+76;struct.pack_into('<I',out,at,b-j-1);allowed.update(range(at,at+4));join_changes+=1
    first=last
  pos=end
 diff=[i for i,(a,b) in enumerate(zip(original,out)) if a!=b];assert len(original)==len(out) and all(i in allowed for i in diff)
 (O/fname).write_bytes(out)
 reports.append(dict(file=fname,uv_changes=uv_changes,continuation_changes=join_changes,material_aliases=names,engine_core_mapping=core_report,geometry_animation_effect_anchors_collision_unchanged=True))
 print(fname,'UV faces',len(uv_changes),'joins',join_changes,flush=True)
(W/'native_repairs.json').write_text(json.dumps(dict(passed=True,files=reports),indent=2)+'\n')
