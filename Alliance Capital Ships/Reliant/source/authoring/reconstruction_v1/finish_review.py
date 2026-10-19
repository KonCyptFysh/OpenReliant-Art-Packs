from pathlib import Path
import shutil,hashlib,json,subprocess,zipfile,datetime
import numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/reconstruction_v1';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.18.0-linux-x86_64';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
log=Path('/tmp/reliant-runtime.log').read_text();assert 'PASS native engine destruction, open-close-open doors, cabin faults and thermal response' in log
assert not any(t in log.lower() for t in ['error(', 'warning(scripts)', 'warning(library)', 'imagemissing'])
assert 'PASS 43 total checks' in (W/'response-tests.log').read_text()
for p in S.glob('*.luau'):subprocess.run(['/tmp/kurgen-luau/build/luau-compile',str(p)],stdout=subprocess.DEVNULL,check=True)
checks=[]
for kind,name in [('shp','Reliant.SHP'),('shp','Reliant_destback.SHP'),('dte','mission959.dte'),('dte','mission958.dte')]:
 q=subprocess.run([str(E/'sltool'),kind,'check',str(S/name)],text=True,capture_output=True,check=True);checks.append(dict(file=name,sha256=sha(S/name),output=q.stdout+q.stderr))
(W/'native_checks.json').write_text(json.dumps({'passed':True,'checks':checks},indent=2)+'\n')
for src,dest in [('/tmp/reliant-runtime.log',W/'runtime.log'),('/tmp/reliant-runtime-check.png',D/'review/runtime-destruction-check.png'),('/tmp/reliant-material-build.log',W/'materials-build.log'),('/tmp/reliant-tiers.log',W/'tiers-build.log')]:shutil.copy2(src,dest)
packages=D/'packages';packages.mkdir(exist_ok=True);tiers=[]
for tier,n,root in [('4k',4096,S.parent.parent),('2k',2048,D/'exports/review_v1_2k'),('1k',1024,D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name
 for p in S.iterdir():
  if p.suffix!='.png':
   if T!=S:shutil.copy2(p,T/p.name)
   assert sha(p)==sha(T/p.name)
  elif p.name!='mod.png':
   with Image.open(T/p.name) as im:
    im.load();assert im.size==(n,n)
    if '_normal' in p.name:
     a=np.asarray(im.convert('RGB')).astype(np.float32)/255*2-1;assert np.max(np.abs(np.linalg.norm(a,axis=-1)-1))<.02
 assert len(list(T.glob('orr*.png')))==12 and not list(T.glob('g-*.png')) and not list(T.glob('r-*.png'))
 for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:
  if root!=S.parent.parent:shutil.copy2(S.parent.parent/name,root/name)
  subprocess.run(['bash','-n',str(root/name)],check=True)
 shutil.copy2(D/'README.md',root/'README.md')
 records=[{'file':str(p.relative_to(T)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps({'ship':'Reliant','status':'local-first-review','resolution':tier,'files':records},indent=2)+'\n')
 z=packages/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for r in records:assert hashlib.sha256(archive.read('mods/'+S.name+'/'+r['file'])).hexdigest()==r['sha256']
 tiers.append({'tier':tier,'dimensions':[n,n],'runtime':str(T),'package':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'files':records})
 print('PACKAGE_READY',tier,round(z.stat().st_size/1048576,2),'MiB',flush=True)
# Deploy the exact verified 4K export. This is a new ship-specific review directory.
installed=G/'game-data/mods'/S.name
if installed.exists():
 assert all(p.is_file() and (S/p.name).is_file() and sha(p)==sha(S/p.name) for p in installed.iterdir()),'Unexpected existing Reliant review content'
shutil.copytree(S,installed,dirs_exist_ok=True)
for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:shutil.copy2(S.parent.parent/name,G/name);(G/name).chmod(0o755)
assert {p.name for p in installed.iterdir()}=={p.name for p in S.iterdir()}
assert all(sha(p)==sha(installed/p.name) for p in S.iterdir())
assert not (installed/'test_runtime.luau').exists() and 'dt *= 10' not in (installed/'reliant_lighting.luau').read_text()
state=json.loads((D.parent/'project_state.json').read_text())
for name,expected in state['source_originals'].items():assert sha(D/'source'/name)==expected
state.update(status='first_pass_ready_for_review',user_approved=False,published=False,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),installed_runtime=str(installed),launchers=[str(G/'launch-reliant-test.sh'),str(G/'launch-reliant-doors-test.sh')],packages=[{'tier':r['tier'],'path':r['package'],'sha256':r['sha256']} for r in tiers])
state['progress'].update(texture_uv='Three atlases restored with built-in imagegen; native UVs retained; primitive continuation breaks repaired',pbr_authoring='Structural normals, metal/rough and masked emissive maps complete at 1K, 2K and 4K',engine_validation='Official 0.18.0 integration passed: healthy/damaged/fault lights, throttle, afterglow, engine destruction, and open-close-open door motion',visual_review='User review pending; no Git/gallery publication')
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
result={'passed':True,'engine':'Official OpenReliant 0.18.0','response_checks':43,'runtime_log':str(W/'runtime.log'),'native_models':checks,'nozzle_mask_all_native_parts_and_lods':True,'shared_turret_mask_checks':json.loads((W/'shared-nozzle-audit.json').read_text()),'runtime_test_clock':'Probe only: response and assertion clocks accelerated 10x; native doors/destruction use real engine; shipped scripts unmodified','tiers':tiers,'installed':{'path':str(installed),'exact_export_hashes':True},'source_originals_preserved':True,'visual_approval':'pending','published':False}
(W/'review-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('RELIANT_INSTALLED_VERIFIED',len(list(installed.iterdir())),flush=True)
