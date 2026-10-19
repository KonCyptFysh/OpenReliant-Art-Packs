"""Build registered hangar materials and narrowly scoped native-model repairs.

ImageGen supplies colour artwork. All secondary maps derive from the same pixels;
no separately traced or generated normal contours can drift from the colour map.
"""
from pathlib import Path
import json, struct, sys, hashlib, shutil
import numpy as np
from PIL import Image, ImageFilter

D=Path('${RELIANT_WORKSPACE}')
W=D/'work/hangar_v11'; M=D/'maps/hangar_v11'; M.mkdir(exist_ok=True)
B=D/'history/stages/pre_hangar_v11/exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
N=W/'native'; N.mkdir(exist_ok=True)
sys.path.insert(0,str(D/'work/alignment_v3'))
from audit_native import parse
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def blur(a,r):
    return np.asarray(Image.fromarray(np.uint8(np.clip(a,0,1)*255)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255

maps=[]
for i,stem in [(1,'orr_hang1'),(2,'orr_hang2'),(3,'orr_hang3'),(4,'orr_tube')]:
    src=W/(f'relint_{i}_source.png' if i<4 else 'tube_source.png')
    # Native generated resolution is retained in source. 4K is a delivery tier,
    # not a claim of independently generated 4K detail.
    im=Image.open(src).convert('RGB').resize((2048,2048),Image.Resampling.LANCZOS)
    a=np.asarray(im).astype(np.float32)/255
    lum=a@np.array([.2126,.7152,.0722],np.float32)
    smooth=blur(lum,1.2); broad=blur(lum,4)
    # Suppress fine paint/grime relief. The dark engineered grooves recess;
    # small highlights and wear never become huge bumps.
    # Paint and scratches sit on a flat plate. Only the dark seams, rails and
    # recesses receive appreciable depth, avoiding a pebbled metal surface.
    h=np.clip((blur(lum,2.2)-.035)/.105,0,1)*1.6
    dy,dx=np.gradient(h)
    v=np.stack([-dx*3,dy*3,np.ones_like(dx)],-1)
    v/=np.linalg.norm(v,axis=-1,keepdims=True)
    rough=np.clip(.70-.17*np.clip((broad-.12)/.4,0,1),.48,.76)
    sat=a.max(-1)-a.min(-1)
    metal=np.clip(.48+.25*np.clip((broad-.17)/.5,0,1)-sat*1.4,.14,.75)
    ao=np.clip(.78+.22*np.clip(smooth/.20,0,1),.78,1)
    em=np.zeros_like(a)
    # Only the small red safety lenses on the tube have self illumination;
    # native launch beacons remain real blinking attachments, never painted glow.
    if i==4:
        red=(a[...,0]>a[...,1]*1.65)&(a[...,0]>a[...,2]*1.65)&(a[...,0]>.12)
        em[red]=a[red]*np.array([.65,.18,.08])
    channels={'':a,'_normal':v*.5+.5,'_orm':np.stack([ao,rough,metal],-1),'_emissive':em}
    for suffix,arr in channels.items():
        Image.fromarray(np.uint8(np.clip(arr,0,1)*255+.5)).save(M/f'{stem}{suffix}.png')
    np.save(M/f'{stem}_height.npy',h)
    Image.fromarray(np.uint8(np.clip(h/2.5,0,1)*255)).save(M/f'{stem}_height.png')
    maps.append(dict(stem=stem,source=str(src),source_sha256=sha(src),authoring_size=2048,normal_max_error=float(abs(np.linalg.norm(v,axis=-1)-1).max())))

def chunks(raw):
    pos=0
    while pos<len(raw):
        t,s,c=struct.unpack_from('<3H',raw,pos); st=pos+6; end=st+s*c
        yield pos,t,s,c,st,end
        pos=end
    assert pos==len(raw)

def split_mismatched_groups(raw):
    """Split existing GPU primitives only at material or UV discontinuities."""
    out=bytearray(raw); repairs=0
    for _,t,s,c,st,end in chunks(raw):
        if t!=3:continue
        fs=[]
        for k in range(c):
            at=st+k*s
            fs.append((struct.unpack_from('<I',raw,at)[0],struct.unpack_from('<3I',raw,at+12),np.array(struct.unpack_from('<6f',raw,at+24)).reshape(2,3).T,*struct.unpack_from('<2I',raw,at+72)))
        first=0
        while first<c:
            last=first+fs[first][4]+1; assert last<=c
            seg=first; segments=[]
            for k in range(first+1,last):
                anchor,prev,cur=fs[seg],fs[k-1],fs[k]
                ids=[anchor[1][0],prev[1][2]] if anchor[3]==1 else list(prev[1][1:])
                uv=np.array([anchor[2][0],prev[2][2]]) if anchor[3]==1 else prev[2][1:]
                if cur[0]!=anchor[0] or ids!=list(cur[1][:2]) or np.max(abs(uv-cur[2][:2]))>1e-6:
                    segments.append((seg,k));seg=k
            segments.append((seg,last))
            for a,b in segments:
                for k in range(a,b):
                    if fs[k][4]!=b-k-1:
                        struct.pack_into('<I',out,st+k*s+76,b-k-1);repairs+=1
            first=last
    return out,repairs

def batch_body(raw,body_indices):
    # The official renderer permits twenty consecutive surface runs per mesh.
    # Group whole primitives by material without changing any triangle. Remap
    # collision leaf indices through the same permutation of detail level 0.
    out=bytearray(raw);pi=li=-1;permutation={};audit=[]
    for _,t,s,c,st,end in chunks(raw):
        if t==2:pi+=1;li=-1
        if t==4:li+=1
        if pi not in body_indices:continue
        if t==3:
            groups=[];k=0
            while k<c:
                rem=struct.unpack_from('<I',raw,st+k*s+76)[0]
                last=k+rem+1;assert last<=c
                groups.append(list(range(k,last)));k=last
            groups.sort(key=lambda g:struct.unpack_from('<3I',raw,st+g[0]*s))
            order=[k for g in groups for k in g];assert sorted(order)==list(range(c))
            out[st:end]=b''.join(raw[st+k*s:st+(k+1)*s] for k in order)
            if li==0:permutation[pi]={old:new for new,old in enumerate(order)}
            runs=sum(j==0 or struct.unpack_from('<3I',out,st+j*s)!=struct.unpack_from('<3I',out,st+(j-1)*s) for j in range(c))
            assert runs<=20
            audit.append(dict(part=pi,lod=li,surface_runs=runs,triangles_unchanged=True))
        if t==8:
            for k in range(c):
                at=st+k*s;old=struct.unpack_from('<I',raw,at)[0]
                struct.pack_into('<I',out,at,permutation[pi][old])
    return out,audit

raw=(D/'source/Reliant_Hang.SHP').read_bytes();out=bytearray(raw);pi=-1;lights=[]
for _,t,s,c,st,end in chunks(raw):
    if t==2:pi+=1
    if t==6:
        for k in range(c):
            at=st+k*s;old=raw[at:at+64].split(b'\0')[0].decode().lower()
            new={'relint_1':'orr_hang1','relint_2':'orr_hang2','relint_3':'orr_hang3'}[old]
            out[at:at+64]=new.encode().ljust(64,b'\0')
    if t==9:
        for k in range(c):
            at=st+k*s
            if struct.unpack_from('<I',raw,at)[0]!=4:continue
            blink=struct.unpack_from('<2i',raw,at+84)
            before=struct.unpack_from('<2f',raw,at+116)
            # Retain beacon cadence/phase, colour, location and sprite. Reduce
            # the overpowering steady red fill but keep its original reach.
            after=(1500.,2.) if sum(blink) else (5500.,.55)
            struct.pack_into('<2f',out,at+116,*after)
            lights.append(dict(part=pi,attachment=k,blink=list(blink),before=list(before),after=list(after)))
out,splits=split_mismatched_groups(out);(N/'Reliant_Hang.SHP').write_bytes(out)
hangar=dict(source_sha256=sha(D/'source/Reliant_Hang.SHP'),output_sha256=sha(N/'Reliant_Hang.SHP'),lights=lights,primitive_splits=splits)

reports=[]
for name in ['Reliant.SHP','Reliant_destback.SHP']:
    raw,ps=parse(B/name);out=bytearray(raw);selected={};changes=[]
    for pi,p in enumerate(ps):
        door=p['name'].startswith(('Rel top dr ','Rel bot dr '))
        if p['name']!='Reliant Body' and not door:continue
        for li,l in enumerate(p['lods']):
            for f in l['faces']:
                uv=f['uv'];v=l['vertices'][f['ids']]+p['origin']
                if door:
                    sign=1 if p['name'].startswith('Rel top dr ') else -1
                    if f['norm'][1]*sign<.98:continue
                elif not(f['mat']==0 and uv[:,0].min()>115 and uv[:,0].max()<161 and uv[:,1].min()>58 and uv[:,1].max()<155 and abs(f['norm'][1])<.05 and v[:,1].min()>-2020 and v[:,1].max()<-75):continue
                # Isotropic world-space projection, shared by both triangles,
                # with the same 1800 native units per tile in both directions.
                if door:mapped=np.c_[v[:,0]/1800,v[:,2]/1800*sign]
                else:
                    if abs(f['norm'][0])>.9:u=v[:,2]/1800 * (1 if f['norm'][0]>0 else -1)
                    else:u=v[:,0]/1800 * (-1 if f['norm'][2]>0 else 1)
                    mapped=np.c_[u,(v[:,1]+2020)/1800]
                struct.pack_into('<6f',out,f['at']+24,*mapped.T.ravel())
                selected.setdefault(pi,[]).append(f['at'])
                changes.append(dict(part=pi,part_name=p['name'],role='door_inner' if door else 'tube_wall',lod=li,face=f['id'],old_uv=uv.tolist(),new_uv=(mapped*256).tolist(),normal=f['norm'].tolist()))
    # Native material tables are local to each part. Append, never replace an
    # existing material used by external faces or the destroyed sections.
    output=[];pi=-1;new_material=None
    for pos,t,s,c,st,end in chunks(raw):
        if t==2:pi+=1
        if t==6 and pi in selected:
            new_material=c
            for at in selected[pi]:struct.pack_into('<I',out,at,c)
            for change in changes:
                if change['part']==pi:change['material']=c
            record=bytearray(raw[st:st+s]);record[:64]=b'orr_tube'.ljust(64,b'\0')
            # Output assembled below after all face material indices are set.
    pi=-1
    for pos,t,s,c,st,end in chunks(raw):
        if t==2:pi+=1
        if t==6 and pi in selected:
            record=bytearray(raw[st:st+s]);record[:64]=b'orr_tube'.ljust(64,b'\0')
            output.append(struct.pack('<3H',t,s,c+1)+bytes(out[st:end])+record)
        else:output.append(bytes(out[pos:end]))
    final,splits=split_mismatched_groups(b''.join(output))
    final,batches=batch_body(final,set(selected));(N/name).write_bytes(final)
    # Vertex geometry, normals, tracks, attachments and collision bounds remain
    # byte-identical; leaf indices follow the face permutation above.
    before=[(t,s,c,raw[st:end]) for _,t,s,c,st,end in chunks(raw) if t not in (3,6,8)]
    after=[(t,s,c,final[st:end]) for _,t,s,c,st,end in chunks(final) if t not in (3,6,8)]
    assert before==after
    reports.append(dict(file=name,changes=changes,primitive_splits=splits,batches=batches,geometry_attachments_animation_unchanged=True,collision_leaf_indices_follow_face_permutation=True))
    print(name,len(changes),'tube faces',flush=True)

(W/'build-report.json').write_text(json.dumps(dict(maps=maps,hangar=hangar,tube_models=reports,normal_method='Shared colour-derived structural relief; micro wear suppressed; no added geometry'),indent=2)+'\n')
print('INTERIOR MATERIALS AND NATIVE MODELS BUILT',flush=True)
