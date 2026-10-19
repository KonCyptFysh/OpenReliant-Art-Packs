from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,datetime,numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/refinement_v2';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';G=Path('${OPENRELIANT_HOME}');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert 'PASS 49 including' in (W/'response-tests.log').read_text()
for name in ['runtime-engine.log','runtime-bridge.log']:
 s=(W/name).read_text();assert not any(t in s.lower() for t in ['warning(scripts)','warning(library)','error(']),name
 if name=='runtime-engine.log':assert 'RELIANT_V2 hot PASS' in s and 'RELIANT_V2 cooling PASS' in s and 'RELIANT_V2 rotation PASS' in s
assert (D/'reliant_worn_pbr_v2.blend').exists()
old=json.loads((D/'history/stages/pre_surface_v2/project_state.json').read_text())
for name,digest in old['source_originals'].items():assert sha(D/'source'/name)==digest,name
for p in S.glob('*.luau'):subprocess.run(['/tmp/kurgen-luau/build/luau-compile',str(p)],stdout=subprocess.DEVNULL,check=True)
checks=[]
for p in S.iterdir():
 if p.suffix in ['.SHP','.dte']:
  q=subprocess.run([str(G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'),'shp' if p.suffix=='.SHP' else 'dte','check',str(p)],capture_output=True,text=True,check=True);checks.append({'file':p.name,'result':q.stdout.strip()})
packages=[];normals=[]
for tier,n,root in [('4k',4096,S.parent.parent),('2k',2048,D/'exports/review_v1_2k'),('1k',1024,D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name;T.mkdir(parents=True,exist_ok=True)
 if T!=S:
  for p in S.iterdir():
   if p.suffix!='.png' or p.name=='mod.png':shutil.copy2(p,T/p.name);continue
   im=Image.open(p).convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
   if p.stem.endswith('_normal'):
    a=np.asarray(im).astype('float32')/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-8);im=Image.fromarray(np.uint8(np.clip(a*.5+.5,0,1)*255+.5))
   im.save(T/p.name)
 for p in T.glob('*.png'):
  if p.name=='mod.png':continue
  im=Image.open(p);assert im.size==(n,n),(p,im.size)
  if p.stem.endswith('_normal'):
   a=np.asarray(im.convert('RGB')).astype('float32')/127.5-1;err=float(abs(np.linalg.norm(a,axis=-1)-1).max());assert err<.015;normals.append({'tier':tier,'file':p.name,'max_unit_error':err})
 for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:
  if root!=S.parent.parent:shutil.copy2(S.parent.parent/name,root/name)
  subprocess.run(['bash','-n',str(root/name)],check=True)
 shutil.copy2(D/'README.md',root/'README.md')
 records=[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-2-awaiting-review',resolution=tier,surface_revision=2,files=records),indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for r in records:assert hashlib.sha256(archive.read('mods/'+S.name+'/'+r['file'])).hexdigest()==r['sha256']
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGE',tier,flush=True)
# No probe files or accelerated observers enter a package.
assert not any('probe' in p.name for p in S.iterdir())
assert 'dt*=10' not in (S/'reliant_lighting.luau').read_text()
installed=G/'game-data/mods'/S.name
for p in S.iterdir():shutil.copy2(p,installed/p.name)
assert {p.name for p in S.iterdir()}=={p.name for p in installed.iterdir()}
assert all(sha(p)==sha(installed/p.name) for p in S.iterdir())
for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:shutil.copy2(S.parent.parent/name,G/name);(G/name).chmod(0o755)
state=json.loads((D.parent/'project_state.json').read_text());state.update(status='surface_revision_2_ready_for_review',user_approved=False,published=False,latest_scene=str(D/'reliant_worn_pbr_v2.blend'),current_maps=str(D/'maps/refinement_v2'),packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(texture_uv='Window rectangles and naval stencil revised; 197 faces across LODs repaired at radiator/engine joins and engine effect anchors',pbr_authoring='Stronger semantic relief and cavity occlusion on hull, bridge, radiator/nozzle surfaces and both shared turrets; unified window material masks',engine_validation='Official 0.18.0: rotation/reset, white-hot cores, red petals, independent cooling and clean bridge-window view passed; 49 response checks',visual_review='Revision 2 awaits user visual approval')
state['surface_revision']=2;state['camera']['revision']=3;state['camera']['features']+=['Alt+arrows ship yaw/pitch','Alt+comma/period ship roll','Alt+Home ship orientation reset'];state['engine_heat']={'core_rise_seconds':8,'core_cooldown_seconds':20,'petal_rise_seconds':4,'petal_cooldown_seconds':5,'colors':'red-to-white core, red-only petals','effect_origins_unchanged':True};state['shared_turrets']={'models':['Allied_Cap_Gun.SHP','13_al_STUR.SHP'],'materials':['orr_cgun','orr_sgun'],'note':'Shared model overrides within this enabled pack; global ALL_TRT/Missiles materials retained'}
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
report=dict(passed=True,engine='official OpenReliant 0.18.0',response_checks=49,window_rectangles=64,source_original_hashes_unchanged=True,native_checks=checks,normal_checks=normals,installed_hashes_match=True,packages=packages,review_status='awaiting user review',geometry_animation_collision_and_effect_anchors_unchanged=True,uv_repairs='native_repairs.json',evidence=['runtime-engine.log','runtime-bridge.log','engine-hot.png','bridge-review.png'])
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('RELIANT_V2_INSTALLED_AND_PACKAGED',flush=True)
