from pathlib import Path
import shutil,json,hashlib,subprocess
from PIL import Image
import numpy as np

D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/kanji_v3';O=D/'exports/openreliant_v3/mods/100-sai-worn-v1';old=D/'exports/openreliant_v2/mods/100-sai-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'scene_validation.json').read_text());assert sha(r['scene'])==r['scene_sha256'];shutil.copytree(old,O,dirs_exist_ok=True)
for name in ['orsa1_body.png','gorsa1_body.png']:shutil.copy2(r['maps']['sam1']['basecolor']['path'],O/name)
# Same native deployment command used by the original Sai missions. This is
# new inspection script bytecode only, with no model/animation chunk edits.
source=(D/'work/reconstruction_v1/inspection.py').read_text()
source=source.replace('instructions = bytes.fromhex("2d 00 21 03 32 01 43")','instructions = bytes.fromhex("2d 00 21 03 2c 00 2b 0a 66 69 6e 20 64 6f 77 6e 00 21 11 32 01 43")')
source=source.replace('# push_flight_group 0; CreateFlightGroup; push_byte 1; return.','# CreateFlightGroup 0; StartShipAnimation ship 0, "fin down"; return.')
source=source.replace('Create only the player\'s flight group; return.','Create the player flight group; play fin down; return.')
(W/'inspection.py').write_text(source)
ns={'__name__':'sai_inspection_v3','__file__':str(W/'inspection.py')};exec(compile(source,str(W/'inspection.py'),'exec'),ns)
(O/'mission991.dte').write_bytes(ns['inspection_mission']())
(O/'mod.ini').write_text('[Mod]\nName=Sai - Worn Paint\nVersion=0.1.0-beta.2\nDescription=Independent left/right UVs with correctly oriented painted kanji. Local review build; not published.\nOpenReliant=0.7.0\nLicense=CC-BY-NC-SA-4.0\n')
tool='/home/lva-8700/Games/OpenReliant/releases/openreliant-v0.7.0-linux-x86_64/sltool';checks=[]
for name,kind in [('Jap_Sai.SHP','shp'),('mission991.dte','dte')]:
 p=subprocess.run([tool,kind,'check',str(O/name)],capture_output=True,text=True,check=True);checks.append({'file':name,'exit_code':p.returncode,'output':p.stdout+p.stderr,'sha256':sha(O/name)})
p=subprocess.run([tool,'dte','script',str(O/'mission991.dte')],capture_output=True,text=True,check=True);assert 'StartShipAnimation' in p.stdout and 'fin down' in p.stdout and 'push_ship' in p.stdout;(W/'inspection_script.txt').write_text(p.stdout)
changed=[]
for path in old.iterdir():
 if sha(path)!=sha(O/path.name):changed.append(path.name)
assert sorted(changed)==sorted(['orsa1_body.png','gorsa1_body.png','mission991.dte','mod.ini']),changed
for mat in ['orsa1_body','orsa1_fins']:
 for suffix in ['','_normal','_orm']:
  assert sha(O/f'{mat}{suffix}.png')==sha(O/f'g{mat}{suffix}.png')
for atlas,roles in r['maps'].items():
 for role,rec in roles.items():
  assert sha(rec['path'])==rec['sha256']
  with Image.open(rec['path']) as im: assert list(im.size)==rec['dimensions'];im.verify()
report={'passed':True,'native_checks':checks,'native_model_byte_identical_to_v2':sha(O/'Jap_Sai.SHP')==sha(old/'Jap_Sai.SHP'),'all_normals_orm_and_other_textures_byte_identical':True,'flight_and_loadout_maps_identical':True,'changed_files':changed,'inspection_spawns_one_ship_and_plays_fin_down':True,'runtime_launched':False,'runtime_visual_review':'pending_user_review','official_engine':'OpenReliant 0.7.0','export':str(O)}
(W/'export_validation.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(__file__,W/'export.py');print(json.dumps(report,indent=2))
