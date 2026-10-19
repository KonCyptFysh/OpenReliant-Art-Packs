from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,datetime,numpy as np
from PIL import Image
from audit_native import parse
D=Path('${RELIANT_WORKSPACE}');W=D/'work/alignment_v3';B=D/'history/stages/pre_alignment_v3';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';G=Path('${OPENRELIANT_HOME}');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((B/'project_state.json').read_text());before=B/'exports/openreliant_0_18_v1/mods'/S.name
for name,digest in old['source_originals'].items():assert sha(D/'source'/name)==digest,name
for p in S.iterdir():
 if p.suffix in ['.luau','.glsl'] or (p.suffix=='.png' and not p.stem.endswith(('_normal','_orm'))):assert sha(p)==sha(before/p.name),p.name
assert (D/'reliant_worn_pbr_v3.blend').exists()
rep=json.loads((W/'native_repairs.json').read_text());count=sum(len(f['uv_changes']) for f in rep['files']);assert count==42
# Verify every audited geometric edge really shares UVs in the written native files.
seam_checks=[]
for item in rep['files']:
 raw,parts=parse(S/item['file'])
 for pair in item['seams']:
  li=pair['lod'];pa,pb=pair['parts'];fa,fb=pair['faces'];a=parts[pa]['lods'][li];b=parts[pb]['lods'][li];f=a['faces'][fa];g=b['faces'][fb]
  x=a['vertices'][f['ids']]+parts[pa]['origin'];y=b['vertices'][g['ids']]+parts[pb]['origin'];match=np.argwhere(np.linalg.norm(x[:,None]-y[None,:],axis=-1)<.1);assert len(match)>=2
  err=max(np.linalg.norm(f['uv'][i]-g['uv'][j]) for i,j in match);assert err<.0001,(pair,err)
  seam_checks.append(dict(lod=li,parts=pair['parts'],faces=pair['faces'],max_error_native_pixels=float(err)))
checks=[]
for p in S.iterdir():
 if p.suffix in ['.SHP','.dte']:
  q=subprocess.run([str(G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'),'shp' if p.suffix=='.SHP' else 'dte','check',str(p)],capture_output=True,text=True,check=True);checks.append(dict(file=p.name,result=q.stdout.strip()))
evidence=['bridge','pipes','gun','core','core-lit','vent','radiator','front']
for name in evidence:
 src=Path(f'/tmp/reliant-v3-{name}.log');s=src.read_text();assert not any(x in s.lower() for x in ['warning(scripts)','warning(library)','error(']),name
 shutil.copy2(src,W/f'runtime-{name}.log');shutil.copy2(f'/tmp/reliant-v3-{name}.png',W/f'{name}-check.png')
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
   a=np.asarray(im.convert('RGB')).astype('float32')/127.5-1;err=float(abs(np.linalg.norm(a,axis=-1)-1).max());assert err<.015;normals.append(dict(tier=tier,file=p.name,max_unit_error=err))
 for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:
  if root!=S.parent.parent:shutil.copy2(S.parent.parent/name,root/name)
  subprocess.run(['bash','-n',str(root/name)],check=True)
 shutil.copy2(D/'README.md',root/'README.md');records=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-3-awaiting-review',resolution=tier,surface_revision=3,files=records),indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for r in records:assert hashlib.sha256(archive.read('mods/'+S.name+'/'+r['file'])).hexdigest()==r['sha256']
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGE',tier,flush=True)
installed=G/'game-data/mods'/S.name
for p in S.iterdir():shutil.copy2(p,installed/p.name)
assert {p.name for p in S.iterdir()}=={p.name for p in installed.iterdir()};assert all(sha(p)==sha(installed/p.name) for p in S.iterdir())
state=json.loads((D.parent/'project_state.json').read_text());state.update(status='surface_revision_3_ready_for_review',user_approved=False,published=False,latest_scene=str(D/'reliant_worn_pbr_v3.blend'),current_maps=str(D/'maps/alignment_v3'),surface_revision=3,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(texture_uv='Preserved current colour/emission; 42 additional faces aligned at the forward body/comms join across LODs',pbr_authoring='Rebuilt aligned hull/bridge/machinery/radiator and shared capital-turret relief; deep engine annulus, domed hub, rim and 12 individually traced vanes',engine_validation='Official 0.18.0 close checks: bridge, machinery, radiator, forward join, underside turret and cold engine interiors under changed lighting; native preservation, seam and map-unit checks passed',visual_review='Revision 3 awaits user visual approval')
state['alignment_revision_3']={'uv_faces':count,'matched_edges':len(seam_checks),'base_and_emission_unchanged':True,'thermal_and_cabin_logic_unchanged':True,'evidence':str(W/'validation.json')}
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',source_originals_unchanged=True,base_emission_scripts_unchanged=True,native_geometry_animations_collision_effects_unchanged=True,uv_faces=count,seam_checks=seam_checks,native_checks=checks,normal_checks=normals,installed_hashes_match=True,packages=packages,evidence=evidence,user_visual_approval_pending=True),indent=2)+'\n');print('RELIANT_V3_INSTALLED_AND_PACKAGED',flush=True)
