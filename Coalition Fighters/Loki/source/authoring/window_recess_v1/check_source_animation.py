import os
from pathlib import Path
import bpy,json,hashlib
D=Path(str(Path(os.environ['LOKI_WORKSPACE'])));W=D/'work/window_recess_v1'
r=json.loads((W/'repository_snapshot.json').read_text())
def signature(path):
 bpy.ops.wm.open_mainfile(filepath=path);s=bpy.context.scene;result={}
 assert len([o for o in s.objects if o.type=='MESH'])==7
 for f in [1,25,51,75,101]:
  s.frame_set(f);bpy.context.view_layer.update();result[f]={o.name:[list(x) for x in o.matrix_world] for o in s.objects if o.type=='MESH'}
 assert sum(result[1][name]!=result[101][name] for name in result[1])>=6
 return result
original=signature(r['canonical_scene']);snapshot=signature(r['snapshot']);assert original==snapshot
(W/'source_animation_check.json').write_text(json.dumps(dict(passed=True,canonical_and_portable_poses_identical=True,frames=[1,25,51,75,101],parts=7,pose_signature=hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest()),indent=2)+'\n')
print('LOKI_PORTABLE_ANIMATION_VERIFIED')
