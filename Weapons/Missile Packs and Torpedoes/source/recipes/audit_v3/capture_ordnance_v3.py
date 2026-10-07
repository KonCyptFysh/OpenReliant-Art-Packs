import os
import argparse,subprocess,os,json,hashlib,datetime
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('item',type=int);p.add_argument('slug');p.add_argument('--from',dest='camera',default='1.6,-0.6,0.8');a=p.parse_args()
b=Path(os.environ.get('OPENRELIANT', 'openreliant'))
d=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve()
g=Path(os.environ['ORDNANCE_REVIEW']).expanduser().resolve()
out=d/'review/game_audit_v3'/f'{a.slug}.png';log=d/'work/audit_v3'/f'{a.slug}.log'
cmd=[str(b),str(g/'game-data'),'--mission','991','--ship',f'ordnance-inspection:item{a.item}','--view','1','--skip-launch','--watch','0','--watch-from',a.camera,'--size','1600x1000','--no-sound','--screenshot-ticks','120','--screenshot',str(out)]
env=os.environ.copy();env['SDL_VIDEODRIVER']='x11';env.pop('XDG_ACTIVATION_TOKEN',None)
with log.open('w') as f:r=subprocess.run(cmd,cwd=g,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90)
assert r.returncode==0,(r.returncode,str(log));assert out.is_file(),str(log)
entry={'item':a.item,'image':str(out),'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'binary_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'command':cmd,'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'log':str(log),'exit_code':r.returncode}
with (d/'work/audit_v3/captures.jsonl').open('a') as f:f.write(json.dumps(entry)+'\n')
print(out)
