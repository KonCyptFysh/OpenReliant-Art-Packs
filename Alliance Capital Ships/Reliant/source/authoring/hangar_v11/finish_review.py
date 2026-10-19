from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,zipfile,datetime,os
D=Path('${RELIANT_WORKSPACE}');W=D/'work/hangar_v11';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';I=Path('${OPENRELIANT_HOME}/game-data/mods/119-reliant-worn-v1');B=D/'history/stages/pre_hangar_v11/exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['material-validation.json','native-validation.json','scene-validation.json']:assert json.loads((W/name).read_text())['passed']
assert json.loads((W/'scene-validation.json').read_text())['tube_uv_corners']==216
for name in ['launch-010','launch-040','launch-090','landing-final']:
    assert (W/(name+'.png')).exists()
    text=(W/(name+'.log')).read_text().lower()
    assert not any(x in text for x in ['warning(scripts)','warning(library)','error(']),name
runtime=(W/'validated-flight-landing.log').read_text()
assert all(x in runtime for x in ['ORDER launch','ORDER player_control','COMMS Permission to land','LAND_REQUEST','CAMERA landing_tube','function on_mission_end'])
# This earlier interactive run landed before one entire review-door cycle.
# Its old observer consequently rejected that extra condition on shutdown;
# the native sequence itself reached mission end. Preserve that evidence.
warnings=[x for x in runtime.splitlines() if 'warning(' in x]
assert all('120-flight-probe' in x for x in warnings)
assert 'DOORS_OPEN_CLOSE_PASS' in (W/'landing-final.log').read_text()
on=np.asarray(Image.open(W/'launch-010.png')).astype(float)
off=np.asarray(Image.open(W/'launch-040.png')).astype(float)
region=(slice(90,190),slice(350,900),0)
pulse_ratio=float(on[region].mean()/off[region].mean());assert pulse_ratio>1.15
shutil.copy2('/tmp/reliant-hangar-v11/screenshots/screenshot0003.png',W/'landing-wall-check.png')
for p in B.glob('*.luau'):assert sha(p)==sha(S/p.name)
for p in B.glob('*.glsl'):assert sha(p)==sha(S/p.name)
for p in B.glob('orr*_hull*.png'):assert sha(p)==sha(S/p.name)
for p in B.glob('mission*.dte'):assert sha(p)==sha(S/p.name)

description=dict(revision=11,launch_hangar_atlases=3,tube_wall_triangles_lod0=48,inward_door_triangles_lod0=24,native_units_per_tile=1800,generated_source_dimensions=[1254,1254],authoring_map_dimensions=[2048,2048],four_k_maps_resampled=True,lighting='Native beacon timing/phase/positions preserved; range +50%; steady red fill dimmed with approximately preserved reach',normals='Colour-registered structural relief, paint microtexture suppressed',geometry_preserved=True,collision_leaf_geometry_verified=True,exterior_colour_and_materials_unchanged=True)
p=D/'README.md';text=p.read_text().replace('Authoring maps are 2048 square from the retained generated sources','Authoring maps are 2048 square from retained 1254-square generated sources');p.write_text(text)
packages=[]
for tier,folder in [('4k','openreliant_0_18_v1'),('2k','review_v1_2k'),('1k','review_v1_1k')]:
    root=D/'exports'/folder;T=root/'mods'/S.name;shutil.copy2(p,root/'README.md')
    manifest=json.loads((root/'manifest.json').read_text())
    manifest.update(status='surface-revision-11-awaiting-user-review',surface_revision=11,interior_revision=description)
    manifest['files']=[dict(file=f.name,bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(T.iterdir()) if f.is_file()]
    manifest['progress'].update(texture_uv='Tube walls and inner doors use uniform physical texture scale',pbr_authoring='Reconstructed launch hangar and dedicated landing lining; aligned normal/ORM maps',engine_validation='Official 0.18.0 launch flash samples, landing views, native comms and mission end; native collision and exterior preservation checks passed',visual_review='Awaiting user review')
    if 'flight_review' in manifest:manifest['flight_review']['hangar_art']='Revision 11 reconstructed hangar'
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        for f in sorted(root.rglob('*')):
            if f.is_file():archive.write(f,f.relative_to(root))
    with zipfile.ZipFile(z) as archive:
        assert archive.testzip() is None
        for f in root.rglob('*'):
            if f.is_file():assert hashlib.sha256(archive.read(str(f.relative_to(root)))).hexdigest()==sha(f)
    packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGE VERIFIED',tier,flush=True)
for p in S.iterdir():
    if p.is_file():shutil.copy2(p,I/p.name)
assert {p.name for p in S.iterdir()}=={p.name for p in I.iterdir()}
assert all(sha(p)==sha(I/p.name) for p in S.iterdir() if p.is_file())
launcher=Path('${OPENRELIANT_HOME}/launch-reliant-flight-test.sh');assert os.access(launcher,os.X_OK)
state_path=D.parent/'project_state.json';state=json.loads(state_path.read_text())
state.update(status='surface_revision_11_ready_for_review',surface_revision=11,latest_scene=str(D/'reliant_worn_pbr_v11.blend'),hangar_scene=str(D/'reliant_hangar_v11.blend'),interior_maps=str(D/'maps/hangar_v11'),user_approved=False,published=False,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(texture_uv='Six tubes and inward faces of twelve doors use uniform physical texture scale; exterior UV repairs retained',pbr_authoring='Revision 11 reconstructed separate launch hangar and landing lining with registered normal/ORM maps',engine_validation='Official 0.18.0 launch pulses, landing cutaways and comms mission end checked; model/collision/original hashes verified',visual_review='Revision 11 interiors awaiting user approval')
state['flight_review_revision_1']['hangar_art']='Revision 11 reconstructed interior'
state['interior_revision_11']=dict(description,validation=str(W/'validation.json'),source_workspace=str(W))
for p in (D/'source/hangar').glob('*.png'):state['source_originals']['hangar/'+p.name]=sha(p)
state_path.write_text(json.dumps(state,indent=2)+'\n')
result=dict(passed=True,engine='official OpenReliant 0.18.0',scope='Interior materials, native model preservation, launch beacon visibility and landing integration',description=description,beacon_red_mean_on_off_ratio=pulse_ratio,normal_material_checks='material-validation.json',native_collision_checks='native-validation.json',scene_checks='scene-validation.json',uniform_scale_checks='uv-scale-validation.json',comms_landing=dict(native_sequence_reached_end=True,log='validated-flight-landing.log',observer_warning='Old probe required a full review-door cycle before landing; this interactive run requested landing early. Production scripts had no warnings.'),door_cycle=dict(open_close_observed=True,log='landing-final.log',note='Deterministic diagnostic landing capture; its shutdown is a screenshot exit, not proof of native mission end.'),packages=packages,installed_hashes_match=True,launcher=str(launcher),originals_preserved=True,user_visual_approval_pending=True)
(W/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
(W/'art-provenance.json').write_text(json.dumps(dict(tool='built-in image_gen',request='Upgrade separate launch hangar, restore visible warning flashes and correct distorted landing interior',sources=[dict(file=p.name,sha256=sha(p),size=list(Image.open(p).size)) for p in sorted(W.glob('*_source.png'))],constraints='Exact existing launch atlas layouts; worn neutral military steel; sharp structural detail; dedicated modular shaft lining; no unrelated exterior edits',secondary_maps='Shared registered pixels; colour-derived recess relief and ORM, not independently generated normals'),indent=2)+'\n')
print('REVISION 11 INSTALLED AND HASH VERIFIED; USER REVIEW PENDING',flush=True)
