from pathlib import Path
import json,hashlib,shutil,zipfile,datetime,numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/frame_relief_v6';M=D/'maps/frame_relief_v6';B=D/'history/stages/pre_frame_relief_v6';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';G=Path('${OPENRELIANT_HOME}');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mask=np.asarray(Image.open(W/'frame-edit-mask.png'))>0
for suffix in ['', '_emissive', '_normal', '_orm']:
 a=np.asarray(Image.open(M/f'orr2_hull{suffix}.png'));b=np.asarray(Image.open(D/f'maps/windows_v5/orr2_hull{suffix}.png'))
 if suffix in ['', '_emissive']:assert np.array_equal(a,b)
 else:assert np.array_equal(a[~mask],b[~mask])
 if suffix=='_orm':assert np.array_equal(a[:,:,1:],b[:,:,1:])
regions=json.loads((D/'work/windows_v5/window-material-regions.json').read_text())['windows']
for r in regions:
 a,b,c,d=r['outer_frame'];assert not mask[b:d,a:c].any(),r['id']
assert len(regions)==64
edges=json.loads((W/'measured-bevels.json').read_text());assert len(edges)==20;assert sum(len(e['edges']) for e in edges)==160
state=json.loads((D.parent/'project_state.json').read_text())
for name,digest in state['source_originals'].items():assert sha(D/'source'/name)==digest,name
for p in M.iterdir():
 if p.name not in ['orr2_hull_normal.png','orr2_hull_orm.png','orr2_hull_height.png','orr2_hull_height.npy']:assert sha(p)==sha(D/'maps/windows_v5'/p.name),p.name
assert (D/'reliant_worn_pbr_v6.blend').exists()
evidence=['v5-bridge-cell','v6-bridge-cell','v6-forward-windows','v6-machinery-left','v6-bridge-other-rotated','v6-bridge-cell-rotated','v6-bridge-cell-1k','v6-forward-windows-2k']
for name in evidence:
 assert (W/(name+'.png')).exists();s=(W/(name+'.log')).read_text().lower();assert not any(x in s for x in ['warning(scripts)','warning(library)','error(']),name
packages=[];normal_checks=[]
for tier,n,root in [('4k',4096,S.parent.parent),('2k',2048,D/'exports/review_v1_2k'),('1k',1024,D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name;old=B/'exports'/root.name/'mods'/S.name
 for p in T.iterdir():
  if p.name not in ['orr2_hull_normal.png','orr2_hull_orm.png','mod.ini']:assert sha(p)==sha(old/p.name),p.name
 for suffix in ['_normal','_orm']:
  im=Image.open(T/f'orr2_hull{suffix}.png');assert im.size==(n,n)
  if suffix=='_normal':
   a=np.asarray(im).astype('float32')/127.5-1;err=float(abs(np.linalg.norm(a,axis=-1)-1).max());assert err<.015;normal_checks.append(dict(tier=tier,max_unit_error=err))
 shutil.copy2(D/'README.md',root/'README.md');records=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-6-awaiting-review',resolution=tier,surface_revision=6,files=records),indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as a:
  for p in sorted(root.rglob('*')):
   if p.is_file():a.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as a:
  assert a.testzip() is None
  for r in records:assert hashlib.sha256(a.read('mods/'+S.name+'/'+r['file'])).hexdigest()==r['sha256']
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGED',tier,flush=True)
I=G/'game-data/mods'/S.name
for name in ['orr2_hull_normal.png','orr2_hull_orm.png','mod.ini']:shutil.copy2(S/name,I/name)
assert {p.name for p in S.iterdir()}=={p.name for p in I.iterdir()};assert all(sha(p)==sha(I/p.name) for p in S.iterdir())
state.update(status='surface_revision_6_ready_for_review',surface_revision=6,latest_scene=str(D/'reliant_worn_pbr_v6.blend'),current_maps=str(M),user_approved=False,published=False,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(pbr_authoring='Structural pocket transitions retraced at painted falloff; normal/height and cavity corrected; revision 5 window artwork preserved',engine_validation='Official 0.18.0 same-camera before/after, both bridge sides, changed lighting, forward/machinery frames, 1K/2K checks; map and installed hash validation passed',visual_review='Revision 6 structural bevel correction awaits user review')
state['alignment_revision_4']['remaining_issue']='Superseded structural pocket ramps: bright-ridge fit with excessive constant depth produced detached dark strip'
state['frame_relief_revision_6']=dict(pockets=20,measured_edges=160,changed_material='REL2 structural pocket normal, height, AO',window_inserts_unchanged=64,geometry_uv_and_scripts_unchanged=True,evidence=str(W/'validation.json'))
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',pockets=20,measured_edges=160,window_inserts_unchanged=64,basecolor_and_emission_unchanged=True,roughness_and_metallic_unchanged=True,unrelated_maps_and_native_files_unchanged=True,source_originals_unchanged=True,pixels_outside_frame_mask_unchanged=True,normal_checks=normal_checks,evidence=evidence,packages=packages,installed_hashes_match=True,user_visual_approval_pending=True),indent=2)+'\n');print('V6_INSTALLED_VERIFIED',flush=True)
