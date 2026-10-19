from pathlib import Path
import hashlib,json,datetime,zipfile
D=Path('${RELIANT_WORKSPACE}');W=D/'work/flight_review_v1';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';G=Path('${OPENRELIANT_HOME}');I=G/'game-data/mods'/S.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
log=(W/'validated-runtime.log').read_text()
assert all(s in log for s in ['ORDER launch','ORDER player_control','hangar=true','DOORS_OPEN_CLOSE_PASS','COMMS Permission to land | Request backup','LAND_REQUEST','CAMERA landing_tube','PASS launch, free flight, doors, landing and mission end'])
assert not any(s in log for s in ['warning(', 'error('])
installed_log=(W/'installed-launch.log').read_text()
assert not any(s in installed_log for s in ['warning(', 'error('])
assert 'started reliant_flight_review.luau' in installed_log
assert (W/'installed-launch.png').stat().st_size>100000
before=json.loads((W/'before/asset-sha256.json').read_text())
unchanged=[name for name in before if name!='mod.ini']
assert all(sha(S/name)==before[name] for name in unchanged)
assert {p.name for p in I.iterdir()}=={p.name for p in S.iterdir()}
assert all(sha(p)==sha(I/p.name) for p in S.iterdir() if p.is_file())
packages=[]
for tier,root in [('4k',D/'exports/openreliant_0_18_v1'),('2k',D/'exports/review_v1_2k'),('1k',D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name
 for name in ['mission957.dte','reliant_flight_review.luau','mod.ini']:
  assert sha(T/name)==sha(S/name)
 files=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 manifest=json.loads((root/'manifest.json').read_text())
 manifest.update(status='surface-revision-9-flight-review-1-awaiting-review',files=files,flight_review_revision=1)
 manifest['flight_review']={'mission':957,'player':'Patriot','native_launch':True,'native_comms_landing':True,'repeating_doors':True,'separate_hangar_art':'original','runtime_validation':'complete','source':'source/mission957.luau'}
 (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for p in root.rglob('*'):
   if p.is_file():assert hashlib.sha256(archive.read(str(p.relative_to(root)))).hexdigest()==sha(p)
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size))
 print('PACK VERIFIED',tier,flush=True)
validation=dict(passed=True,engine='official OpenReliant 0.18.0',mission=957,surface_revision=9,flight_review_revision=1,
 native_launch=True,free_flight=True,normal_hud_and_controls=True,door_open_close_verified=True,door_travel=2233.265625,
 comms_path=['Base','Permission to land'],native_landing_camera='landing_tube',mission_end_verified=True,
 landing_guard_no_subsequent_review_animation_commands=True,runtime_log='validated-runtime.log',installed_launcher_smoke='installed-launch.log',
 launch_image='installed-launch.png',existing_runtime_files_unchanged=unchanged,installed_hashes_match=True,packages=packages,
 visual_approval='pending user review',hangar_interior='separate original asset, unchanged')
(W/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
state_path=D.parent/'project_state.json';state=json.loads(state_path.read_text())
state.update(updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),packages=packages)
state['flight_review_revision_1']=dict(mission=957,player='Patriot',native_launch=True,door_cycle='repeat open-hold-close-hold after launch; stop issuing commands on landing',native_comms_landing=True,normal_hud=True,hangar_art='Original separate interior',validation=str(W/'validation.json'),status='runtime_verified_user_review_pending')
launcher=str(G/'launch-reliant-flight-test.sh')
if launcher not in state['launchers']:state['launchers'].append(launcher)
state_path.write_text(json.dumps(state,indent=2)+'\n')
print('INSTALLED FILES AND ALL REVIEW PACKAGES VERIFIED; art and UVs unchanged',flush=True)
