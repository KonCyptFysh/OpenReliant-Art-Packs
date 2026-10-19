from pathlib import Path
import json,hashlib,shutil,zipfile,datetime
D=Path('${RELIANT_WORKSPACE}');W=D/'work/opaque_glass_v8';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';I=Path('${OPENRELIANT_HOME}/game-data/mods/119-reliant-worn-v1')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
material=json.loads((W/'material-validation.json').read_text());assert material['passed']
evidence=['v8-bridge-cell-light1','v8-bridge-distant-light1','v8-bridge-cell-light0','v8-bridge-cell-light0.25','v8-bridge-other-rotated-light1-2k','v8-bridge-distant-light1-1k']
for name in evidence:
    assert (W/(name+'.png')).exists()
    log=(W/(name+'.log')).read_text().lower()
    assert not any(x in log for x in ['warning(scripts)','warning(library)','error(']),name
packages=[]
for tier,root in [('4k',D/'exports/openreliant_0_18_v1'),('2k',D/'exports/review_v1_2k'),('1k',D/'exports/review_v1_1k')]:
    T=root/'mods'/S.name
    shutil.copy2(D/'README.md',root/'README.md')
    files=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
    (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-8-awaiting-review',resolution=tier,surface_revision=8,engine='official OpenReliant 0.18.0',progress=dict(texture_uv='Revision 7 UV repairs retained',pbr_authoring='Opaque illuminated glazing with matching roughness and micro-normal relief',engine_validation='Runtime and material checks passed',visual_review='Awaiting user review'),files=files),indent=2)+'\n')
    z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
    with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as a:
        for p in sorted(root.rglob('*')):
            if p.is_file():a.write(p,p.relative_to(root))
    with zipfile.ZipFile(z) as a:
        assert a.testzip() is None
        for f in files:assert hashlib.sha256(a.read('mods/'+S.name+'/'+f['file'])).hexdigest()==f['sha256']
    packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGED',tier,flush=True)
for name in ['orr2_hull.png','orr2_hull_emissive.png','orr2_hull_orm.png','orr2_hull_normal.png','mod.ini']:shutil.copy2(S/name,I/name)
assert {p.name for p in S.iterdir()}=={p.name for p in I.iterdir()}
assert all(sha(p)==sha(I/p.name) for p in S.iterdir())
state=json.loads((D.parent/'project_state.json').read_text())
state.update(status='surface_revision_8_ready_for_review',surface_revision=8,latest_scene=str(D/'reliant_worn_pbr_v8.blend'),current_maps=str(D/'maps/opaque_glass_v8'),user_approved=False,published=False,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(pbr_authoring='64 opaque frosted window panes: brighter warm emission, subtle glass wear, matching roughness/normal/height; accepted bezels and structural pocket relief preserved',engine_validation='Official 0.18.0 close/distant and both-side checks, 0/25/100% power and all texture tiers; native meshes and scripts byte-identical to revision 7',visual_review='Revision 8 brighter opaque glazing awaits user review')
state['opaque_glass_revision_8']=dict(count=64,source_mode='built-in ImageGen plus registered material assembly',source=str(W/'opaque-glass-art-source.png'),prompt=str(W/'imagegen-prompt.txt'),frames_gaskets_and_uvs_preserved=True,room_imagery_removed=True,lighting_logic_unchanged=True,evidence=str(W/'validation.json'))
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',material_validation=str(W/'material-validation.json'),window_count=64,geometry_uv_and_scripts_unchanged=True,frames_and_gaskets_unchanged=True,originals_unchanged=True,packages=packages,installed_hashes_match=True,evidence=evidence,user_visual_approval_pending=True),indent=2)+'\n')
print('V8 INSTALLED AND ALL PACKAGE HASHES VERIFIED',flush=True)
