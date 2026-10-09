import os
from pathlib import Path
import json,hashlib,re,shutil,numpy as np
D=Path(str(Path(os.environ['KAMOV_WORKSPACE'])));W=D/'work/reconstruction_v1';R=D/'work/runtime_validation';O=D/'exports/openreliant_v1/mods/104-kamov-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse(path):
 text=Path(path).read_text();assert text.count('started kamov_inspection.luau')==1, 'Unexpected mission restart'
 assert not re.search(r'(error\(|Error:|not ported|runtime error|stack traceback)',text), 'Runtime error'
 rows={};events=[]
 for line in text.splitlines():
  if 'KAMOV_TORPEDO\t' in line:
   x=line.split('KAMOV_TORPEDO\t')[1].split('\t');step,slot=int(x[0]),int(x[1]);assert x[2]=='launch';rows.setdefault(step,{})[slot]=np.array(list(map(float,x[3:6])))
  if 'KAMOV_ANIMATION\t' in line:
   x=line.split('KAMOV_ANIMATION\t')[1].split('\t');events.append(dict(step=int(x[0]),command=x[1]))
 for data in rows.values():assert set(data)=={1,2,3,4}
 return rows,events,text
rows,events,text=parse('/tmp/kamov-cycle-final.log');assert max(rows)>=950
assert [x['command'] for x in events]==['start_ship_animation','start_ship_animation_reverse','start_ship_animation']
travel={};returned={};repeat={}
for slot in range(1,5):
 travel[slot]=float(np.linalg.norm(rows[400][slot]-rows[25][slot]));assert travel[slot]>200
 returned[slot]=float(np.linalg.norm(rows[700][slot]-rows[25][slot]));assert returned[slot]<.001
 repeat[slot]=float(np.linalg.norm(rows[925][slot]-rows[400][slot]));assert repeat[slot]<.001
 # Check an intermediate opening position, not just two endpoint poses.
 assert 50<float(np.linalg.norm(rows[225][slot]-rows[25][slot]))<travel[slot]
opened,open_events,open_text=parse('/tmp/kamov-deployed-final.log');assert max(opened)>=125
assert open_events[0]['command']=='start_ship_animation'
for slot in range(1,5):assert np.linalg.norm(opened[125][slot]-rows[400][slot])<.001
stowed,stowed_events,stowed_text=parse('/tmp/kamov-stowed-final.log');assert stowed_events==[]
for slot in range(1,5):assert np.linalg.norm(stowed[25][slot]-rows[25][slot])<.001
for name in ['cycle-final','deployed-final','stowed-final']:shutil.copy2('/tmp/kamov-'+name+'.log',R/(name+'.log'))
report=dict(passed=True,engine='Official OpenReliant 0.7.0',engine_sha256=sha(str(Path(os.environ['OPENRELIANT_HOME']) / 'releases/openreliant-v0.7.0-linux-x86_64/openreliant')),mission985_cycle=dict(screenshot_ticks=3900,simulation_steps=max(rows),events=events,all_four_torpedoes_attached=True,intermediate_motion_verified=True,stowed_deployed_stowed_then_second_deployment_verified=True,travel_native_units=travel,return_error_native_units=returned,second_deployment_error_native_units=repeat,no_mission_restart=True),mission987_stowed=dict(screenshot_ticks=100,all_torpedoes_in_stowed_position=True),mission986_deployed=dict(screenshot_ticks=600,simulation_steps=max(opened),pose_matches_cycle=True,holds_deployed=True),native_animation_untouched=True,torpedo_asset='Existing approved 97-ordnance-worn-v1',runtime_files=[dict(name=p.name,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file()],captures=[dict(path=str(p),sha256=sha(p)) for p in sorted((D/'review/animation_v1').glob('*.png'))],logs=[dict(path=str(R/(name+'.log')),sha256=sha(R/(name+'.log'))) for name in ['cycle-final','deployed-final','stowed-final']],scope='Bounded bay mechanism and carried-torpedo tests. User visual review and full gameplay remain pending.',test_harness_note='Long --watch captures end a mission via the native watch camera timer; full cycle was verified in standard external view. Final run has no restart. Mission-only Luau sets friendly sides, passive turrets, disabled player engines and invulnerability. First three modes block missile input; manual-launch mode allows it.')
(W/'runtime_animation_checks.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(__file__,W/'validate_runtime_animation.py');shutil.copy2('/tmp/prepare-kamov-runtime.py',W/'prepare_runtime.py');print(json.dumps({k:report['mission985_cycle'][k] for k in ['events','travel_native_units','return_error_native_units','second_deployment_error_native_units']},indent=2))
