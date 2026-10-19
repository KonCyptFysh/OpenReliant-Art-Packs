from audit_native import *
import collections
O=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';reports=[]
for fname in ['Reliant.SHP','Reliant_destback.SHP']:
 raw,parts=parse(S/fname);out=bytearray(raw);changes=[];pairs=[];allowed=set()
 for li in range(max(len(p['lods']) for p in parts)):
  allf=[];edges=collections.defaultdict(list);parent=[];uvs=[]
  def root(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  def join(a,b):parent[root(a)]=root(b)
  # Join geometrically coincident corners already sharing mapping. This includes
  # duplicated mesh vertices and boundaries between the body and comms parts.
  corners={}
  for pi,p in enumerate(parts):
   if li>=len(p['lods']):continue
   l=p['lods'][li]
   for f in l['faces']:
    pts=l['vertices'][f['ids']]+p['origin'];f['base']=len(parent);f['pi']=pi;allf.append(f)
    for j in range(3):
     idx=len(parent);parent.append(idx);uvs.append(f['uv'][j].copy());key=(f['mat'],*np.round(pts[j],1),*np.round(f['uv'][j],3))
     if key in corners:join(idx,corners[key])
     else:corners[key]=idx
    for j in range(3):
     k=(j+1)%3;a=tuple(np.round(pts[j],1));b=tuple(np.round(pts[k],1))
     if a>b:a,b=b,a;j,k=k,j
     edges[(a,b)].append((f,j,k))
  for ed,members in edges.items():
   # Audited continuous forward radiator/side-panel island only.
   for a in range(len(members)):
    for b in range(a+1,len(members)):
     f,j,k=members[a];g,u,v=members[b]
     if f['mat']!=2 or g['mat']!=2:continue
     if f['pi'] not in [16,17,23] or g['pi'] not in [16,17,23]:continue
     uv=np.r_[f['uv'][[j,k]],g['uv'][[u,v]]];err=np.linalg.norm(f['uv'][[j,k]]-g['uv'][[u,v]],axis=1)
     if uv[:,0].min()>=0 and uv[:,0].max()<89 and uv[:,1].min()>115 and uv[:,1].max()<256 and .025<max(err)<20:
      join(f['base']+j,g['base']+u);join(f['base']+k,g['base']+v);pairs.append(dict(lod=li,parts=[f['pi'],g['pi']],faces=[f['id'],g['id']],before_error=err.tolist()))
  groups=collections.defaultdict(list)
  for i in range(len(parent)):groups[root(i)].append(i)
  fixed=np.array(uvs)
  for ids in groups.values():
   # Deduplicate identical corner coordinates before averaging: triangle count must
   # not bias the result differently on each side of a split.
   avg=np.unique(np.round(fixed[ids],5),axis=0).mean(0);fixed[ids]=avg
  for f in allf:
   old=f['uv'].copy();new=fixed[f['base']:f['base']+3]
   if np.max(abs(new-old))>.00005:
    f['uv']=new;at=f['at']+24;struct.pack_into('<6f',out,at,*(new/256).T.ravel());allowed.update(range(at,at+24));changes.append(dict(part=f['pi'],lod=li,face=f['id'],before=old.tolist(),after=new.tolist()))
 # Keep triangle strip/fan UV boundaries explicit.
 joins=0
 for p in parts:
  for l in p['lods']:
   fs=l['faces'];first=0
   while first<len(fs):
    last=first+fs[first]['rem']+1;seg=first;segments=[]
    for i in range(first+1,last):
     a,b,c=fs[seg],fs[i-1],fs[i];ids=[a['ids'][0],b['ids'][2]] if a['kind']==1 else b['ids'][1:];uv=[a['uv'][0],b['uv'][2]] if a['kind']==1 else b['uv'][1:]
     if ids!=c['ids'][:2] or np.max(abs(np.array(uv)-c['uv'][:2]))>1e-4:segments.append((seg,i));seg=i
    segments.append((seg,last))
    for a,b in segments:
     for i in range(a,b):
      if fs[i]['rem']!=b-i-1:at=fs[i]['at']+76;struct.pack_into('<I',out,at,b-i-1);allowed.update(range(at,at+4));joins+=1
    first=last
 assert len(out)==len(raw) and all(i in allowed for i,(a,b) in enumerate(zip(raw,out)) if a!=b)
 (O/fname).write_bytes(out);reports.append(dict(file=fname,uv_changes=changes,seams=pairs,continuation_changes=joins,geometry_animations_effects_unchanged=True));print(fname,len(changes),'faces',len(pairs),'joins')
(W/'native_repairs.json').write_text(json.dumps(dict(passed=True,files=reports),indent=2)+'\n')
