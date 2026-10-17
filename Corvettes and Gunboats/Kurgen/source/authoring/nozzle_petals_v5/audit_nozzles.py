"""Sample the native triangles to verify thermal emission stays inside both nozzles."""
from pathlib import Path
import json
import numpy as np

D = Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Kurgen/worn')
parts = json.loads((D / 'source/native_parts.json').read_text())
centers = np.array([[-677.95, 204.75, -2026.06], [617.95, 202.76, -2028.05]])

def smooth(a, b, x):
    t = np.clip((x-a)/(b-a), 0, 1)
    return t*t*(3-2*t)

def petals(points, normal, center):
    radial = points[:, :2] - center[:2]
    radius = np.linalg.norm(radial, axis=1)
    aft = center[2] - points[:, 2]
    inward = smooth(.12, .35, -(radial @ normal[:2])/np.maximum(radius, 1))
    detailed = 1-smooth(.003, .009, abs(-normal[2]-.5675))
    back = max(detailed, smooth(.70, .72, -normal[2]))
    depth = (1-smooth(2, 6, -aft)) * (1-smooth(96, 102.5, aft))
    inside = 1-smooth(211, 215, radius)
    taper = .9 + (.35-.9)*np.clip(aft/101, 0, 1)
    return inward*back*depth*inside*taper

expected = [set(range(19, 35)) | set(range(98, 114)),
            set(range(13, 21)) | set(range(45, 54)) | {63, 84, 86},
            set(), set(), set(), set()]
rows = []
for level, lod in enumerate(parts[0]['lods']):
    vertices = np.array(lod['vertices'])
    selected = set()
    sides = [set(), set()]
    peaks = {}
    for face in lod['faces']:
        if face['hidden']:
            continue
        xyz = vertices[face['vertices']]
        normal = np.cross(xyz[1]-xyz[0], xyz[2]-xyz[0])
        normal /= max(np.linalg.norm(normal), 1e-6)
        if np.dot(normal, face['normal']) < 0:
            normal = -normal
        samples = np.array([xyz[0]*(1-u-v)+xyz[1]*u+xyz[2]*v
                            for u in np.linspace(0, 1, 33)
                            for v in np.linspace(0, 1-u, 33)])
        for side, center in enumerate(centers):
            peak = float(petals(samples, normal, center).max())
            if peak > 1e-6:
                selected.add(face['id'])
                sides[side].add(face['id'])
                peaks[str(face['id'])] = round(peak, 5)
    assert selected == expected[level], (level, sorted(selected), sorted(expected[level]))
    assert (len(sides[0]) == len(sides[1])) if level == 0 else True
    rows.append(dict(lod=level, petal_faces=sorted(selected),
                     left_faces=sorted(sides[0]), right_faces=sorted(sides[1]),
                     peak_weights=peaks))

# Verify the casing and lip normals cannot receive thermal glow, even where
# their positions border the lit petals. The petal gradient must cool outward.
normal = np.array([-1., 0., 0.])
for center in centers:
    q = np.array([center + np.array([150., 0., -20.]),
                  center + np.array([180., 0., -60.]),
                  center + np.array([205., 0., -95.])])
    w = petals(q, np.array([-.8246, 0., -.5657]), center)
    assert w[0] > w[1] > w[2] > 0
    assert not petals(q, -normal, center).any()
    assert not petals(q, np.array([0., 0., -1.]), center).any()

result = dict(passed=True, detail_levels=rows,
              scope='32 inward petal triangles at LOD 0; simplified interiors at LOD 1; no added glow at LOD 2-5. Existing disk mask unchanged.',
              exterior_faces_selected=0, taper='0.90 at throat to 0.35 before lip fade',
              geometry_normals='triangle derivatives; independent of texture normals')
(Path(__file__).parent / 'nozzle_surface_audit.json').write_text(json.dumps(result, indent=2)+'\n')
print('PASS: both nozzles, all six LODs; 32 full-detail petal triangles; zero exterior faces.')
