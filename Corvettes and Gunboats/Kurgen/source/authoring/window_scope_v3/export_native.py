from pathlib import Path
import struct,json,hashlib,shutil,numpy as np
D=Path('${KURGEN_WORKSPACE}');W=D/'work/window_scope_v3'
OLD=D/'exports/openreliant_0_8_v2';E=D/'exports/openreliant_0_8_v3';O=E/'mods/116-kurgen-worn-v1'
if not E.exists():shutil.copytree(OLD,E)
src=OLD/'mods/116-kurgen-worn-v1/Rus_Kurgan.SHP';raw=src.read_bytes();selection=json.loads((W/'bridge_face_selection.json').read_text());selected=selection['selected_faces_by_lod'];crop=selection['atlas_crop'];lod_selected=[[],[66,202],[33,113],[],[],[]]
def sha(b):return hashlib.sha256(b).hexdigest()
def groups(fs):
    i=0
    while i<len(fs):
        end=i+fs[i]['remaining']+1;assert end<=len(fs);assert all(fs[j]['remaining']==end-j-1 for j in range(i,end));yield i,end;i=end
def match(anchor,previous,current):
    if anchor['kind']==1:ids=[anchor['vertices'][0],previous['vertices'][2]];uv=[anchor['uv'][0],previous['uv'][2]]
    else:
        assert anchor['kind'] in (2,3);ids=previous['vertices'][1:];uv=previous['uv'][1:]
    return anchor['material']==current['material'] and ids==current['vertices'][:2] and np.max(np.abs(np.array(uv)-current['uv'][:2]))<1e-6
chunks=[];pos=0;part=lod=-1;report=[];protected=[];rem_changes=[]
while pos<len(raw):
    tag,size,count=struct.unpack_from('<3H',raw,pos);end=pos+6+size*count;old=raw[pos+6:end];data=bytearray(old);newcount=count
    if tag==2:part+=1;lod=-1
    if tag==4:lod+=1
    if tag==3:
        assert size==80;sel=(selected[lod]+lod_selected[lod]) if part==0 else [];fs=[]
        for i in range(count):
            at=i*size;oldUV=np.array(struct.unpack_from('<6f',old,at+24)).reshape(2,3)
            if i in sel:
                assert struct.unpack_from('<I',data,at)[0]==0
                tile=crop if i in selected[lod] else [96,128,112,192];tile_scale=np.array([tile[2]-tile[0],tile[3]-tile[1]])[:,None];mi=1 if i in selected[lod] else 2
                newUV=(oldUV*256-np.array(tile[:2])[:,None])/tile_scale;assert np.min(newUV)>=0 and np.max(newUV)<=1
                struct.pack_into('<I',data,at,mi);struct.pack_into('<6f',data,at+24,*newUV.ravel())
                check=np.array(struct.unpack_from('<6f',data,at+24)).reshape(2,3);assert np.max(np.abs((check*tile_scale+np.array(tile[:2])[:,None])/256-oldUV))<1e-7
                report.append(dict(part=part,lod=lod,face=i,old_material=0,new_material=mi,old_uv=oldUV.T.tolist(),new_uv=check.T.tolist()))
            kind,remaining=struct.unpack_from('<2I',data,at+72)
            fs.append(dict(kind=kind,remaining=remaining,material=struct.unpack_from('<I',data,at)[0],vertices=list(struct.unpack_from('<3I',data,at+12)),uv=np.array(struct.unpack_from('<6f',data,at+24)).reshape(2,3).T))
        oldgroups=list(groups(fs));segments=[]
        for first,last in oldgroups:
            start=first
            for j in range(first+1,last):
                if not match(fs[start],fs[j-1],fs[j]):segments.append((start,j));start=j
            segments.append((start,last))
        for first,last in segments:
            for j in range(first,last):
                rem=last-j-1
                if rem!=fs[j]['remaining']:rem_changes.append(dict(part=part,lod=lod,face=j,before=fs[j]['remaining'],after=rem));struct.pack_into('<I',data,j*size+76,rem);fs[j]['remaining']=rem
        for first,last in groups(fs):
            for j in range(first+1,last):assert match(fs[first],fs[j-1],fs[j])
        for i in range(count):
            before=old[i*size:(i+1)*size];after=data[i*size:(i+1)*size]
            allowed=set(range(0,4))|set(range(24,48)) if i in sel else set();allowed|=set(range(76,80))
            assert all(a==b or j in allowed for j,(a,b) in enumerate(zip(before,after)))
            assert before[4:24]==after[4:24] and before[48:76]==after[48:76]
    elif tag==6 and part==0 and selected[lod]:
        assert size==64 and count==1 and old.split(b'\0')[0]==b'orku1_hull'
        data.extend(b'orku3_bridge'.ljust(64,b'\0'));newcount=2
        if lod_selected[lod]:data.extend(b'orku3_bridge_lod'.ljust(64,b'\0'));newcount=3
    else:
        assert bytes(data)==old;protected.append(dict(part=part,lod=lod,tag=tag,sha256=sha(old)))
    chunks.append(struct.pack('<3H',tag,size,newcount)+data);pos=end
assert pos==len(raw) and len(report)==18
out=b''.join(chunks);(O/'Rus_Kurgan.SHP').write_bytes(out)
(W/'native_preservation.json').write_text(json.dumps(dict(passed=True,source_sha256=sha(raw),output_sha256=sha(out),geometry_normals_attachments_animation_collision_byte_identical=True,window_faces_remapped=report,continuation_corrections=rem_changes,protected_chunks=protected,added_materials=['orku3_bridge','orku3_bridge_lod'],added_material_records=6,front_faces=14,coarse_side_faces=4,all_other_faces_uvs_and_materials_unchanged=True,original_detail_levels=6),indent=2)+'\n')
print('NATIVE_SCOPE_FIXED',len(report),'faces; extra continuation fixes',len(rem_changes))
