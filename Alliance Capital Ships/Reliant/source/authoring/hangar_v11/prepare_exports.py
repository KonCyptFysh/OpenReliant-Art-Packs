from pathlib import Path
from PIL import Image
import numpy as np,shutil,json
D=Path('${RELIANT_WORKSPACE}');W=D/'work/hangar_v11';M=D/'maps/hangar_v11'
checks=[]
for tier,n,folder in [('4k',4096,'openreliant_0_18_v1'),('2k',2048,'review_v1_2k'),('1k',1024,'review_v1_1k')]:
    T=D/'exports'/folder/'mods/119-reliant-worn-v1'
    for p in M.glob('*.png'):
        if '_height' in p.name:continue
        im=Image.open(p).convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
        if '_normal' in p.name:
            a=np.asarray(im).astype(np.float32)/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-8)
            im=Image.fromarray(np.uint8(np.clip(a*.5+.5,0,1)*255+.5))
            v=np.asarray(im).astype(np.float32)/127.5-1;err=float(abs(np.linalg.norm(v,axis=-1)-1).max());assert err<.015
            checks.append(dict(tier=tier,file=p.name,max_normal_error=err))
        im.save(T/p.name)
    for p in (W/'native').glob('*.SHP'):shutil.copy2(p,T/p.name)
    p=T/'mod.ini';s=p.read_text().replace('0.1.0-beta.11','0.1.0-beta.12')
    s=s.replace('Revision 10 capital-scale service galleries, aligned PBR, dynamic windows and thermal engines. Native Patriot launch, cycling doors and comms landing review.','Revision 11 launch hangar and correctly scaled landing tubes, visible native warning flashes, aligned PBR, capital-scale service galleries. Patriot launch, cycling doors and comms landing review.')
    p.write_text(s)
p=D/'README.md';s=p.read_text().replace('surface revision 10','surface revision 11').replace('revision 10 Reliant assets','revision 11 Reliant assets')
s=s.replace('The separate hangar interior remains original.','The separate launch hangar now has three reconstructed interior atlases and matched materials.')
s=s.replace('The Reliant launch uses the separate original `Reliant_Hang.SHP` interior; this\nscene does not claim that its independent textures have been reauthored. Exterior\nand landing views use the current revision 11 Reliant assets.','The Reliant launch uses the revised `Reliant_Hang.SHP` interior. Its three independent\ntexture sheets now have reconstructed colour, aligned relief/normal and material maps.\nLanding views use dedicated tube lining with a consistent world-space texture scale.')
section='''
## Interior revision 11

- Three reauthored launch-hangar atlases cover walls, ceiling, doors and moving retainer.
- Native red beacons keep their original position, alternating timing and phase. Their range increases by 50%; the four steady red fills are dimmed while keeping approximately the same reach, so flashes are visible on the ship and cockpit.
- Six landing tubes use a dedicated modular steel lining. Forty-eight close-detail wall triangles and their lower-detail counterparts use the same 1800-native-unit texture scale in both directions, removing the long-wall stretch.
- Native triangle batches are grouped to fit the official renderer's 20-surface limit. Collision leaf references follow the face permutation; vertex geometry, normals, doors, attachments and animation tracks are preserved.
- All normal/height and ORM maps derive from the same registered colour artwork. Paint scratches do not receive deep displacement. These are surface normals, not new geometric recesses.
- Original files and the previous review are retained in `source` and `history/stages/pre_hangar_v11`. Editable scenes are `reliant_worn_pbr_v11.blend` and `reliant_hangar_v11.blend`.
- Authoring maps are 2048 square from the retained generated sources; the 4K package resamples those maps. It does not claim independently authored 4K detail. Exterior maps remain at their existing tier resolutions.

This is a local review build. Final visual approval remains pending.
'''
if '## Interior revision 11' not in s:s=s.replace('## Review\n',section+'\n## Review\n',1)
p.write_text(s)
(W/'material-validation.json').write_text(json.dumps(dict(passed=True,checks=checks),indent=2)+'\n')
print('ALL THREE INTERIOR EXPORT TIERS READY',flush=True)
