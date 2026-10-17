from pathlib import Path
import json,numpy as np
D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Kurgen/worn')
P=Path(__file__).parent
part=json.loads((D/'source/native_parts.json').read_text())[0]
centers=np.array([[-677.95,204.75,-2026.06],[617.95,202.76,-2028.05]])
rows=[]
for k,lod in enumerate(part['lods']):
    vertices=np.array(lod['vertices']);hits=set();sides=set()
    for face in lod['faces']:
        if face['hidden'] or face['normal'][2]>-.65:continue
        xyz=vertices[face['vertices']]
        for u in np.linspace(0,1,25):
            points=np.array([xyz[0]*(1-u-v)+xyz[1]*u+xyz[2]*v for v in np.linspace(0,1-u,25)])
            for side,center in enumerate(centers):
                depth=np.minimum(abs(points[:,2]-center[2]),abs(points[:,2]-(center[2]-101)))
                inside=(depth<7)&(np.linalg.norm(points[:,:2]-center[:2],axis=1)<124)
                if np.any(inside):hits.add(face['id']);sides.add(side)
    rows.append({'lod':k,'faces':sorted(hits),'both_nozzles':len(sides)==2})
assert all(r['both_nozzles'] for r in rows[:3])
assert all(not r['faces'] for r in rows[3:])
assert set(rows[0]['faces'])=={129,130,131,132,133,175,176,177,178,179,182,248}
(P/'nozzle_surface_audit.json').write_text(json.dumps({'passed':True,'detail_levels':rows,
 'scope':'Only recessed nozzle disks; LOD 2 uses its flattened end disks; coarse LODs have no disks'},indent=2)+'\n')
print('PASS nozzle isolation on all six detail levels')
