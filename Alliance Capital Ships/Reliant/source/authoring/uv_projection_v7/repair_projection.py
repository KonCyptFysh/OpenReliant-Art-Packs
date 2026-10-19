from pathlib import Path
import sys,struct,json,numpy as np
D=Path('${RELIANT_WORKSPACE}');W=D/'work/uv_projection_v7';B=D/'history/stages/pre_uv_projection_v7/exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
sys.path.insert(0,str(D/'work/alignment_v3'));from audit_native import parse
reports=[]
for name in ['Reliant.SHP','Reliant_destback.SHP']:
 raw,ps=parse(B/name);out=bytearray(raw);changes=[];allowed=set()
 for pi,p in enumerate(ps):
  for li,l in enumerate(p['lods']):
   for f in l['faces']:
    uv=f['uv'];c=uv.mean(0)
    if f['mat']!=1 or not(100<c[0]<210 and 15<c[1]<58):continue
    pts=l['vertices'][f['ids']]
    # Only the two native broadside window panels, never similarly textured parts.
    if not (np.max(abs(pts[:,2]))<5200 and np.min(pts[:,2])<-4500 and np.max(pts[:,1])<1000 and np.min(pts[:,1])>-450 and abs(f['norm'][0])>.99):continue
    side=1 if f['norm'][0]>0 else -1
    u0,u1=(114.90,207.80) if side==1 else (114.95,207.90)
    vtop,vshort=(55.90,38.20) if side==1 else (36.72,17.55)
    # One affine projection from the ship's longitudinal/vertical coordinates.
    # The tapered end uses existing non-emissive trim around the atlas bank.
    uu=u0+(487.90-pts[:,2])/(487.90+5161.82)*(u1-u0)
    vv=vtop+(pts[:,1]+439.7075)/(726.0645+439.7075)*(vshort-vtop)
    new=np.c_[uu,vv];at=f['at']+24;struct.pack_into('<6f',out,at,*(new/256).T.ravel());allowed.update(range(at,at+24))
    changes.append(dict(part=pi,part_name=p['name'],lod=li,face=f['id'],side=side,vertices=f['ids'],before=uv.tolist(),after=new.tolist()))
 # Preserve native strip/fan layout when shared UVs remain coincident.
 for pi,p in enumerate(ps):
  for li,l in enumerate(p['lods']):
   fs=l['faces'];first=0
   while first<len(fs):
    last=first+fs[first]['rem']+1
    for i in range(first+1,last):
     anchor,prev,cur=fs[first],fs[i-1],fs[i];ids=[anchor['ids'][0],prev['ids'][2]] if anchor['kind']==1 else prev['ids'][1:]
     if ids!=cur['ids'][:2]:continue
     def getuv(f):return np.array(struct.unpack_from('<6f',out,f['at']+24)).reshape(2,3).T
     a,b,c=getuv(anchor),getuv(prev),getuv(cur);expected=np.array([a[0],b[2]]) if anchor['kind']==1 else b[1:]
     # No strip continuation should newly cross a UV split.
     oldexpected=np.array([anchor['uv'][0],prev['uv'][2]]) if anchor['kind']==1 else prev['uv'][1:]
     if np.max(abs(oldexpected-cur['uv'][:2]))<.001:assert np.max(abs(expected-c[:2]))<1e-5,(name,pi,li,i)
    first=last
 assert len(out)==len(raw) and all(i in allowed for i,(a,b) in enumerate(zip(raw,out)) if a!=b)
 (W/'native'/name).write_bytes(out);reports.append(dict(file=name,uv_changes=changes,geometry_and_every_non_uv_byte_unchanged=True,scope='Intact panel in detail levels 0 and 1; collapsed distant geometry and intentionally deformed wreck retained'));print(name,len(changes),'UV faces',flush=True)
(W/'native_repairs.json').write_text(json.dumps(dict(passed=True,files=reports),indent=2)+'\n')
