import struct,json,numpy as np
from pathlib import Path
from PIL import Image
D=Path('${KURGEN_WORKSPACE}');W=D/'work/window_scope_v3';O=D/'exports/openreliant_0_8_v3/mods/116-kurgen-worn-v1'
source=json.loads((D/'source/native_parts.json').read_text());raw=(O/'Rus_Kurgan.SHP').read_bytes();pos=0;part=lod=-1;models={}
while pos<len(raw):
    t,s,c=struct.unpack_from('<3H',raw,pos);d=raw[pos+6:pos+6+s*c]
    if t==2:part+=1;lod=-1
    if t==4:
        lod+=1;models[part,lod]={'vertices':np.array([struct.unpack_from('<3f',d,i*s) for i in range(c)])+source[part]['origin']}
    if t==3:
        models[part,lod]['faces']=[dict(id=i,mat=struct.unpack_from('<I',d,i*s)[0],hidden=bool(struct.unpack_from('<I',d,i*s+8)[0]&1 or struct.unpack_from('<I',d,i*s+4)[0]&15==1),vertices=list(struct.unpack_from('<3I',d,i*s+12)),uv=np.array(struct.unpack_from('<6f',d,i*s+24)).reshape(2,3).T) for i in range(c)]
    if t==6:models[part,lod]['materials']=[d[i*s:i*s+64].split(b'\0')[0].decode() for i in range(c)]
    pos+=6+s*c
maps={}
for name in ['orku1_hull','orku3_bridge','orku3_bridge_lod']:
    a=np.array(Image.open(O/(name+'_emissive.png')).convert('RGB'));factor=a.shape[0]//256;factor_x=a.shape[1]//256
    mask=a.reshape(256,factor,256,factor_x,3).max(axis=(1,3,4))>4
    yy,xx=np.where(mask);maps[name]=np.stack(((xx+.5)/256,(yy+.5)/256),axis=1)
selection=json.loads((W/'bridge_face_selection.json').read_text());rows=[]
for (part,lod),m in models.items():
    emitted=[];positions=[]
    for f in m['faces']:
        name=m['materials'][f['mat']]
        if f['hidden'] or name not in maps:continue
        uv=f['uv'];xy=maps[name]
        try:ab=np.linalg.solve((uv[1:]-uv[0]).T,(xy-uv[0]).T).T
        except np.linalg.LinAlgError:continue
        ab=ab[(ab.min(axis=1)>=0)&(ab.sum(axis=1)<=1)]
        if not len(ab):continue
        xyz=m['vertices'][f['vertices']];points=xyz[0]+ab@(xyz[1:]-xyz[0]);positions.append(points)
        if name=='orku3_bridge_lod':assert part==0 and f['id'] in [[],[66,202],[33,113],[],[],[]][lod]
        if name=='orku3_bridge':assert part==0 and f['id'] in selection['selected_faces_by_lod'][lod]
        # No generated light on the nose, belly, rear end, engine rings or rear turret platform.
        assert np.all(points[:,2]>-2500) and np.all(points[:,2]<-950) and np.all(points[:,1]<-420),(part,lod,f['id'],points.min(0),points.max(0))
        emitted.append(dict(face=f['id'],material=name,lit_samples=len(points),minimum=points.min(0).tolist(),maximum=points.max(0).tolist()))
    rows.append(dict(part=part,lod=lod,emitting_faces=emitted))
report=dict(passed=True,method='Decode exported SHP; project nonzero emission texels to every visible triangle at each detail level',nose_rear_underside_and_engines_non_emissive=True,allowed_windows='Only the user-highlighted bridge front and sides, mirrored on the opposite side',detail_levels=rows)
Path('/tmp/kurgen-emission-surface-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print([(r['part'],r['lod'],len(r['emitting_faces'])) for r in rows])
