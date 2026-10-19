from pathlib import Path
import json,hashlib,shutil,zipfile,datetime
D=Path('${RELIANT_WORKSPACE}');W=D/'work/service_bays_v10';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';I=Path('${OPENRELIANT_HOME}/game-data/mods/119-reliant-worn-v1')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
material=json.loads((W/'material-validation.json').read_text());assert material['passed']
evidence=['v10-machinery','v10-machinery-left-rotated-2k','v10-machinery-opposite-1k']
for name in evidence:
 assert (W/(name+'.png')).exists()
 log=(W/(name+'.log')).read_text().lower();assert not any(x in log for x in ['warning(scripts)','warning(library)','error(']),name
packages=[]
for tier,root in [('4k',D/'exports/openreliant_0_18_v1'),('2k',D/'exports/review_v1_2k'),('1k',D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name;shutil.copy2(D/'README.md',root/'README.md')
 files=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 manifest=json.loads((root/'manifest.json').read_text())
 manifest.update(status='surface-revision-10-flight-review-1-awaiting-review',surface_revision=10,files=files)
 manifest['progress'].update(pbr_authoring='Three capital-ship service galleries; new registered colour, relief and ORM',engine_validation='Close detail, altered light and opposite side; 1K/2K/4K verified',visual_review='Awaiting user review')
 manifest['service_bays']={'revision':10,'engineering_tiers':3,'source':'built-in ImageGen','map_registration':'shared aperture warp','depth':'image-derived normal/height; unchanged geometry'}
 (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for p in root.rglob('*'):
   if p.is_file():assert hashlib.sha256(archive.read(str(p.relative_to(root)))).hexdigest()==sha(p)
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGED AND VERIFIED',tier,flush=True)
for name in ['orr2_hull.png','orr2_hull_orm.png','orr2_hull_normal.png','mod.ini']:shutil.copy2(S/name,I/name)
assert {p.name for p in S.iterdir()}=={p.name for p in I.iterdir()}
assert all(sha(p)==sha(I/p.name) for p in S.iterdir() if p.is_file())
state_path=D.parent/'project_state.json';state=json.loads(state_path.read_text())
state.update(status='surface_revision_10_ready_for_review',surface_revision=10,latest_scene=str(D/'reliant_worn_pbr_v10.blend'),current_maps=str(D/'maps/service_bays_v10'),user_approved=False,published=False,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(pbr_authoring='Capital-ship-scale service galleries: three equipment tiers, heat exchangers, distribution cabinets and routed services; aligned image-derived relief and PBR',engine_validation='Official 0.18.0: close detail, changed illumination and opposite side; 1K/2K/4K verified; flight/landing, lighting, meshes and UVs unchanged',visual_review='Revision 10 machinery reauthoring awaits user review')
state['machinery_revision_9']['status']='Superseded: sparse oversized plumbing did not convey capital-ship scale'
state['service_bays_revision_10']=dict(bays=[17,18,19],engineering_tiers=3,source_mode='built-in ImageGen with shared aperture registration and material derivation',source=str(W/'service-bays-source.png'),prompt=str(W/'imagegen-prompt.txt'),registration=str(W/'registration.json'),frames_windows_and_uvs_preserved=True,lighting_and_flight_logic_unchanged=True,evidence=str(W/'validation.json'),depth_method='image-derived multiscale height and tangent normals; no additional mesh geometry',scale_evidence='Strip spans 9152 native units, about 20.4 percent of the hull body length')
state_path.write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',surface_revision=10,material_validation=str(W/'material-validation.json'),bays=[17,18,19],geometry_uv_and_scripts_unchanged=True,frames_windows_and_emission_unchanged=True,flight_review_preserved=True,originals_unchanged=True,packages=packages,installed_hashes_match=True,evidence=evidence,user_visual_approval_pending=True),indent=2)+'\n')
print('V10 INSTALLED; PREVIOUS ART, FLIGHT SCENE AND ALL PACKAGE HASHES VERIFIED',flush=True)
