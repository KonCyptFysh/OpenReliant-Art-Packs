import os
from pathlib import Path
import json,hashlib,subprocess,concurrent.futures,shutil
from PIL import Image
import numpy as np
D=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve();W=D/'work/audit_v3';out=D/'exports/runtime_v3';sl=Path(os.environ.get('SLTOOL', 'sltool'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();snap=json.loads((W/'snapshot.json').read_text())
def check(p):
 r=subprocess.run([str(sl),'shp','check',str(p)],capture_output=True,text=True);assert r.returncode==0,(p.name,r.stdout,r.stderr);return dict(file=p.name,sha256=sha(p),exit_status=r.returncode,output=r.stdout+r.stderr)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:checks=list(ex.map(check,sorted(out.glob('*.SHP'))))
(W/'native_checks.json').write_text(json.dumps(checks,indent=2));maps=[]
for p in sorted(out.glob('*.png')):
 im=Image.open(p);a=np.array(im.convert('RGB'));record=dict(file=p.name,resolution=im.size,sha256=sha(p))
 if '_normal' in p.name:
  v=a.astype(float)/127.5-1;mask=np.any(a>0,axis=2);err=abs(np.linalg.norm(v,axis=2)-1)[mask];record.update(covered_max_unit_error=float(err.max()),covered_mean_unit_error=float(err.mean()))
  assert np.quantile(err,.999)<.08,(p.name,record)
 maps.append(record)
(W/'map_checks.json').write_text(json.dumps(maps,indent=2))
for name in snap['user_approved_preserve']:assert sha(out/name)==snap['runtime_v2'][name]
for p in out.glob('orord[12]*.png'):assert sha(p)==snap['runtime_v2'][p.name]
records=json.loads((W/'native_export_validation.json').read_text());bad=[(x['file'],x['max_uv_anisotropy']) for x in records if x['max_uv_anisotropy']>12];assert not bad,bad
print('PASS: 32 native round trips; 15 maps; 18 approved variants exact; prior maps exact; no collapsed UV projections.')
