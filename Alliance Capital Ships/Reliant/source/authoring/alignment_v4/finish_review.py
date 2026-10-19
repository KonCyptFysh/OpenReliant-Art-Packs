from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,datetime,numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/alignment_v4';B=D/'history/stages/pre_alignment_v4';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';G=Path('${OPENRELIANT_HOME}');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((B/'project_state.json').read_text());before=B/'exports/openreliant_0_18_v1/mods'/S.name
changed={'orr2_hull_normal.png','orr2_hull_orm.png','mod.ini'}
for p in S.iterdir():
 if p.name not in changed:assert sha(p)==sha(before/p.name),p.name
for name,digest in old['source_originals'].items():assert sha(D/'source'/name)==digest,name
assert np.array_equal(np.asarray(Image.open(S/'orr2_hull_orm.png'))[:,:,1:],np.asarray(Image.open(before/'orr2_hull_orm.png'))[:,:,1:])
assert (D/'reliant_worn_pbr_v4.blend').exists()
pane=json.loads((W/'pane-containment.json').read_text());assert pane['passed'] and len(pane['checked'])==61
checks=[]
for p in S.iterdir():
 if p.suffix in ['.SHP','.dte']:
  q=subprocess.run([str(G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'),'shp' if p.suffix=='.SHP' else 'dte','check',str(p)],capture_output=True,text=True,check=True);checks.append(dict(file=p.name,result=q.stdout.strip()))
evidence=['v4-bridge-cell-rotated','v4-bridge-other-rotated','v4-forward-windows','v4-small-windows-rotated','v4-machinery','v4-machinery-left']
for name in evidence:
 s=(W/(name+'.log')).read_text();assert not any(x in s.lower() for x in ['warning(scripts)','warning(library)','error(']),name;assert (W/(name+'.png')).exists()
packages=[];normals=[]
for tier,n,root in [('4k',4096,S.parent.parent),('2k',2048,D/'exports/review_v1_2k'),('1k',1024,D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name;T.mkdir(parents=True,exist_ok=True)
 if T!=S:
  # Other tier maps already represent the unchanged v3 source; preserve their bytes.
  for name in changed:
   p=S/name
   if p.suffix!='.png':shutil.copy2(p,T/p.name);continue
   im=Image.open(p).convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
   if p.stem.endswith('_normal'):
    a=np.asarray(im).astype('float32')/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-8);im=Image.fromarray(np.uint8(np.clip(a*.5+.5,0,1)*255+.5))
   im.save(T/p.name)
 for p in T.glob('*.png'):
  if p.name=='mod.png':continue
  im=Image.open(p);assert im.size==(n,n),(p,im.size)
  if p.stem.endswith('_normal'):
   a=np.asarray(im.convert('RGB')).astype('float32')/127.5-1;err=float(abs(np.linalg.norm(a,axis=-1)-1).max());assert err<.015;normals.append(dict(tier=tier,file=p.name,max_unit_error=err))
 for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:subprocess.run(['bash','-n',str(root/name)],check=True)
 shutil.copy2(D/'README.md',root/'README.md');records=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-4-awaiting-review',resolution=tier,surface_revision=4,files=records),indent=2)+'\n')
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
state=json.loads((D.parent/'project_state.json').read_text());state.update(status='surface_revision_4_ready_for_review',user_approved=False,published=False,latest_scene=str(D/'reliant_worn_pbr_v4.blend'),current_maps=str(D/'maps/alignment_v4'),surface_revision=4,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(pbr_authoring='Revision 4 replaces all 20 REL2 frame paths and 19 visible pipe profiles after revision 3 visual rejection; other materials retained',engine_validation='Official 0.18.0 targeted close views: both bridge sides, forward windows, small window surrounds and machinery. Revised lighting angles inspected; native, normal-vector, channel-preservation and installed-hash checks passed',visual_review='Revision 4 awaits user visual approval; revision 3 panel tracing was rejected')
state['alignment_revision_3']['visual_review']='Rejected: inaccurate REL2 frame and pipe paths; superseded by revision 4'
state['alignment_revision_4']={'pockets':20,'pipe_profiles':19,'pane_containment':61,'changed_material':'REL2 normal, structural height and AO only','native_and_lighting_unchanged':True,'evidence':str(W/'validation.json')}
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',source_originals_unchanged=True,base_emission_roughness_metallic_scripts_unchanged=True,native_files_byte_identical_to_v3=True,other_atlases_byte_identical=True,pane_containment=pane,native_checks=checks,normal_checks=normals,installed_hashes_match=True,packages=packages,evidence=evidence,user_visual_approval_pending=True),indent=2)+'\n');print('RELIANT_V4_INSTALLED_AND_PACKAGED',flush=True)
