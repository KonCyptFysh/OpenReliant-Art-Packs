#!/usr/bin/env python3
"""Capture ship gallery photographs using the official engine screenshot API.

Requires a local licensed StarLancer install; reads release runtime files directly
from this repository. Never reads Pictures, changes artwork, or edits game settings.
"""
import argparse, datetime, hashlib, json, os, shutil, subprocess
from pathlib import Path

SHIP_TYPES = {'coyote':4,'predator':0,'reaper':9,'wolverine':8,'tempest':6,
 'shroud':10,'mirage':5,'naginata':1,'patriot':7,'phoenix':11,'crusader':3,
 'sai':23,'grendal':2,'saber':43,'basilisk':49,'kamov':45,'loki':65,
 'azan':42,'cossack':50,'lagg':44,'salin':41,'saracen':46,'haidar':39,
 'karac':40,'galahad':25,'hades':26,'scimitar':48,'kurgen':60,'prowler':30,'reliant':12}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def capture(args):
 root=args.repository.resolve(); game=args.game.resolve(); stage=args.stage.resolve()
 assert stage != game and game not in stage.parents, 'Use an isolated capture directory outside the installed game'
 marker=stage/'.gallery-capture-stage'
 assert not stage.exists() or not any(stage.iterdir()) or marker.exists(), 'Refusing to reuse an unrelated existing directory'
 version=subprocess.check_output([str(args.engine),'--version'],text=True).strip()
 policy=json.loads((root/'tracking/gallery-standard.json').read_text())
 engine_label='Official OpenReliant '+version.split()[-1]
 assert engine_label in {policy['engine'],*policy.get('engine_overrides',{}).values()}, 'Engine is not approved by the photography profile'
 stage.mkdir(parents=True,exist_ok=True)
 marker.write_text('ship-gallery-v1\n')
 for p in game.iterdir():
  if p.name.lower() in {'mods','cache','screenshots','starlancer.ini','openreliant.log','missions','pilots'}: continue
  if not (stage/p.name).exists(): (stage/p.name).symlink_to(p)
 (stage/'mods').mkdir(exist_ok=True)
 # This authored one-ship mission has zero combat triggers, a fixed world origin
 # and the same native nebula and sunlight used for every ordinary ship.
 fixture=stage/'mods/00-gallery-standard';fixture.mkdir(exist_ok=True)
 shutil.copy2(root/'Alliance Fighters/Mirage/mods/90-mirage-worn-v1/mission993.dte',fixture/'mission969.dte')
 (fixture/'mod.ini').write_text('[Mod]\nName=Gallery capture fixture\nVersion=1\nOpenReliant=0.8.1\n[Missions]\nmission969.dte=quiet.luau\n')
 (fixture/'quiet.luau').write_text('''local world = require("openreliant.world")
return {engine_handlers = {on_mission_start = function()
    for _, o in world.objects() do
        o.side = "friendly"
        o.invulnerable = "full"
        o.guns_disabled = true
        o.engines_disabled = true
        o.missiles_disabled = true
        o.eject_disabled = true
    end
end}}
''')
 before_ini=sha(game/'starlancer.ini') if (game/'starlancer.ini').exists() else None
 catalog=json.loads((root/'catalog.json').read_text())
 for asset in catalog['assets']:
  if asset['id'] not in SHIP_TYPES or (args.assets and asset['id'] not in args.assets): continue
  assert engine_label==policy.get('engine_overrides',{}).get(asset['id'],policy['engine']), 'Use the recorded official engine baseline for '+asset['id']
  edition=asset['liveries'][0];folder=root/asset['folder'];mod=folder/'mods'/edition['modFolder']
  records=json.loads((folder/'asset-manifest.json').read_text())
  for rec in records: assert sha(folder/rec['path'])==rec['sha256'], (asset['id'],rec['path'])
  for p in (stage/'mods').iterdir():
   if p.is_symlink():p.unlink()
  (stage/'mods'/mod.name).symlink_to(mod)
  shipname=folder.name;work=args.workspaces/shipname/'worn/work/gallery_standard_v1'
  photos=args.workspaces/shipname/'worn/review/gallery_standard_v1'
  work.mkdir(parents=True,exist_ok=True);photos.mkdir(parents=True,exist_ok=True)
  modes=[('overview',969,60)]
  if asset['id']=='kamov':modes=[('overview',987,60),('deployed',986,450)]
  if asset['id']=='galahad':modes=[('overview',973,60),('deployed',972,450)]
  if asset['id']=='scimitar':modes=[('overview',964,60)]
  if asset['id']=='hades':modes=[('overview',968,60),('deployed',967,450)]
  if asset['id']=='loki':modes=[('overview',983,60),('fighting',982,450)]
  for mode,mission,ticks in modes:
   picture=photos/(mode+'.png');record=work/(mode+'.json')
   if args.resume and record.exists() and picture.exists():
    old=json.loads(record.read_text())
    if old['raw_sha256']==sha(picture) and old['runtime_manifest_sha256']==sha(folder/'asset-manifest.json'):
     print('ALREADY_CAPTURED',asset['id'],mode,flush=True);continue
   command=[str(args.engine),str(stage),'--mission',str(mission),'--ship',str(SHIP_TYPES[asset['id']]),'--view','1',
    '--skip-launch','--watch','0','--watch-from','1.4,-1.4,1.4','--size','2560x1920','--msaa','8',
    '--no-sound','--seed','1','--screenshot',str(picture),'--screenshot-ticks',str(ticks)]
   env=os.environ.copy();env.pop('XDG_ACTIVATION_TOKEN',None);env['SDL_VIDEODRIVER']=args.driver
   print('CAPTURING',asset['id'],mode,flush=True)
   with (work/(mode+'.log')).open('w') as log:
    result=subprocess.run(command,cwd=stage,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
   assert result.returncode==0,(asset['id'],mode,result.returncode)
   assert picture.exists() and picture.stat().st_size>10000
   logtext=(work/(mode+'.log')).read_text()
   assert 'error:' not in logtext.lower() and 'error(' not in logtext.lower(),logtext[-2000:]
   report=dict(asset=asset['id'],livery=edition['id'],artwork_revision=edition['assetRevision'],mode=mode,
    profile='ship-gallery-v1',ship_type=SHIP_TYPES[asset['id']],mission=mission,ticks=ticks,
    watch_from=[1.4,-1.4,1.4],render_size=[2560,1920],msaa=8,seed=1,
    engine=engine_label,engine_sha256=sha(args.engine),
    source='Fresh engine screenshot; isolated game directory; repository runtime files',
    runtime_manifest=str((folder/'asset-manifest.json').relative_to(root)),
    runtime_manifest_sha256=sha(folder/'asset-manifest.json'),raw_file=str(picture),raw_sha256=sha(picture),
    captured_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=0)
   record.write_text(json.dumps(report,indent=2)+'\n')
   print('CAPTURED',asset['id'],mode,picture.stat().st_size,flush=True)
  for rec in records: assert sha(folder/rec['path'])==rec['sha256']
 assert before_ini==(sha(game/'starlancer.ini') if (game/'starlancer.ini').exists() else None)
 print('CAPTURE_BATCH_COMPLETE: runtime files and user settings unchanged',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--repository',type=Path,required=True);p.add_argument('--game',type=Path,required=True)
 p.add_argument('--engine',type=Path,required=True);p.add_argument('--workspaces',type=Path,required=True)
 p.add_argument('--stage',type=Path,required=True);p.add_argument('--driver',default='x11')
 p.add_argument('--assets',nargs='*');p.add_argument('--resume',action='store_true')
 capture(p.parse_args())
