from pathlib import Path
import sys,json,struct,collections,hashlib,subprocess
import numpy as np
D=Path('${RELIANT_WORKSPACE}');W=D/'work/hangar_v11';B=D/'history/stages/pre_hangar_v11/exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
sys.path.insert(0,str(D/'work/alignment_v3'));from audit_native import parse
def chunks(raw):
    pos=0;pi=-1;li=-1
    while pos<len(raw):
        t,s,c=struct.unpack_from('<3H',raw,pos);st=pos+6;end=st+s*c
        if t==2:pi+=1;li=-1
        if t==4:li+=1
        yield pi,li,t,s,c,st,end
        pos=end
def leaf_geometry(raw,ps):
    result=[]
    for pi,li,t,s,c,st,end in chunks(raw):
        if t!=8:continue
        fs=ps[pi]['lods'][0]['faces']
        result.append([fs[struct.unpack_from('<I',raw,st+i*s)[0]]['ids'] for i in range(c)])
    return result
report=json.loads((W/'build-report.json').read_text());checks=[]
for r in report['tube_models']:
    name=r['file'];old,ps=parse(B/name);new,qs=parse(W/'native'/name);expected=bytearray(old)
    for f in r['changes']:
        at=ps[f['part']]['lods'][f['lod']]['faces'][f['face']]['at']
        struct.pack_into('<I',expected,at,f['material']);struct.pack_into('<6f',expected,at+24,*(np.array(f['new_uv'])/256).T.ravel())
    for p,q in zip(ps,qs):
        for l,k in zip(p['lods'],q['lods']):
            assert np.array_equal(l['vertices'],k['vertices'])
            assert collections.Counter(bytes(expected[f['at']:f['at']+76]) for f in l['faces'])==collections.Counter(bytes(new[f['at']:f['at']+76]) for f in k['faces'])
    assert leaf_geometry(old,ps)==leaf_geometry(new,qs)
    checks.append(dict(file=name,all_triangles_preserved=True,all_unedited_face_uvs_preserved=True,collision_leaf_geometry_identical=True))
old,ps=parse(D/'source/Reliant_Hang.SHP');new,qs=parse(W/'native/Reliant_Hang.SHP')
for p,q in zip(ps,qs):
    for l,k in zip(p['lods'],q['lods']):
        assert np.array_equal(l['vertices'],k['vertices'])
        for f,g in zip(l['faces'],k['faces']):assert old[f['at']:f['at']+76]==new[g['at']:g['at']+76]
for r in [p for p in (W/'native').glob('*.SHP')]:
    c=subprocess.run(['${OPENRELIANT_HOME}/releases/openreliant-v0.18.0-linux-x86_64/sltool','shp','check',str(r)],capture_output=True,text=True)
    assert c.returncode==0,(r,c.stdout,c.stderr)
    checks.append(dict(file=r.name,native_check=c.stdout.strip()))
state=json.loads((D.parent/'project_state.json').read_text())
for name,h in state['source_originals'].items():assert hashlib.sha256((D/'source'/name).read_bytes()).hexdigest()==h
(W/'native-validation.json').write_text(json.dumps(dict(passed=True,checks=checks,immutable_originals_verified=True,hangar_geometry_uvs_normals_unchanged=True),indent=2)+'\n')
print('TRIANGLE IDENTITY, EXTERIOR UVS, COLLISION LEAVES AND ORIGINALS VERIFIED')
