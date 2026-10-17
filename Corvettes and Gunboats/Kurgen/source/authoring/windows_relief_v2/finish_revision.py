from pathlib import Path
import json,hashlib,shutil,datetime,subprocess,tempfile,os
D=Path('${KURGEN_WORKSPACE}');W=D/'work/windows_relief_v2';M=D/'maps/windows_relief_v2';O=D/'exports/openreliant_0_8_v2/mods/116-kurgen-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Corvettes and Gunboats/Kurgen';G=Path('${OPENRELIANT_HOME}');I=G/'game-data/mods'/O.name
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
checks=read(W/'map_checks.json');snap=read(W/'repository_snapshot.json');native=read(W/'native_checks.json');val=read(W/'validation.json')
assert checks['passed'] and snap['packed_relative_resources_reopened'] and all(q['exit_code']==0 for q in native)
assert sha(val['scene'])==val['scene_sha256']
prior_manifest=read(A/'asset-manifest.json')
for q in prior_manifest:assert sha(I/Path(q['path']).name)==q['sha256'],q['path']
if not (W/'installed_before_v2').exists():shutil.copytree(I,W/'installed_before_v2')
for p in ['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','release.json','validation.json','compatibility-0.8.json','asset-manifest.json','source-manifest.json']:
    dest=W/'prior_repository_metadata'/p;dest.parent.mkdir(exist_ok=True)
    if not dest.exists():shutil.copy2(A/p,dest)
review=dict(kind='Blender authoring views, not engine captures',views=['front','opposite','belly','rear','emissive_dark'],reviewed_at_utc=now,observations=['Inset warm window panes follow the existing bridge and hull openings.','Dark frame divisions remain visible on both sides.','No emission on stars, caution paint or surrounding hull.','Panel and machinery relief strengthened while painted graphics remain flat.'],in_game_visual_review='pending_user')
dump(W/'authoring_review.json',review)
shutil.copytree(M,A/'source/maps/windows_relief_v2',dirs_exist_ok=True)
shutil.copytree(D/'review/windows_relief_v2',A/'source/review/windows_relief_v2',dirs_exist_ok=True)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
srcdir=A/'source/authoring/windows_relief_v2';srcdir.mkdir(parents=True,exist_ok=True)
for p in W.iterdir():
    if p.is_file() and p.suffix in ['.py','.json','.zig','.log']:
        text=p.read_text()
        for x,y in [(str(D),'${KURGEN_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(G),'${OPENRELIANT_HOME}'),('${IMAGEGEN_ARCHIVE}','${IMAGEGEN_ARCHIVE}')]:text=text.replace(x,y)
        (srcdir/p.name).write_text(text)
readme='''# Kurgen - Worn Paint

**Material revision 1.1 installed for review; unpublished.** Planned beta 0.1.0-beta.1. Pack baseline OpenReliant 0.8.1; local review uses official 0.18.0.

Worn grey hull and three Coalition small turrets, retaining the original red stars, caution paint and machinery. Window openings now contain inset warm amber panes with dark frame divisions and a dedicated emissive map. Hull panel-seam depth is 4.2 times the first pass, machinery recess depth 2.8 times and radiator-rib depth 3 times. Paint and weathering do not drive the bump map.

Only the existing window apertures changed in the accepted base artwork: 4.62% of atlas pixels. The rest of the hull albedo, all geometry, UVs, original mesh normals, six detail levels, mounts and animations are retained. Native exports are byte-identical to the first pass, including its 66 primitive-continuation corrections at UV joins.

The shared Coalition small turret remains at its first-pass material treatment. Its restoration affects other ships using 10_Rus_STUR.SHP. The large turret and shared DAM_1 damage atlas remain original.

Native checks pass on official 0.8.1 and 0.18.0. The 0.8.1 texture loader reads the emissive map and its mip levels correctly. Packed source, normal/ORM maps and exact installed file hashes are checked. Both sides, rear, belly and a dark emissive-only view were inspected in Blender. The new in-game appearance awaits user review.
'''
(A/'README.md').write_text(readme)
(A/'KNOWN_ISSUES.md').write_text('''# Remaining review

- Window brightness and stronger hull relief await in-game user review on official 0.18.0. Blender views are authoring checks, not engine captures.
- Enable MATERIALS for normal, reflection and emissive maps. Loadout colour previews intentionally omit emission; inspect in flight.
- Emissive textures keep windows lit in darkness. They do not add point lights to illuminate nearby hull geometry; no global shader or bloom changes are included.
- Full campaign, damage, turret tracking/firing and distance transitions still need gameplay checks. Original native records and detail levels are preserved.
- The small turret is shared and retains its accepted first-pass materials. The common DAM_1 damage texture remains original.
- Delivery maps are 4096 square, resampled from 1254-square reconstructed and edited artwork. Structural masks are separately authored.
- Publication requires fresh standard official-engine gallery photography after approval.
''')
ch=A/'CHANGELOG.md';ch.write_text('''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.1

Reauthored existing amber window strips as inset panes and frames, with a dedicated emission mask. Increased hull panel and machinery relief. Hull albedo outside window apertures, shared turret, native models and inspection mission preserved. In-game review pending.

'''+ch.read_text().replace('# Changelog\n\n','',1))
(A/'CREDITS.md').write_text('''# Credits

Restoration contributions by KonCyptFysh. Original StarLancer assets retain their respective ownership. OpenReliant supplies the engine and native tools.

Original atlas reconstructions and the targeted window edit use built-in image generation. Original prompts remain in source/authoring/imagegen_prompts.json; the window prompt is in source/authoring/windows_relief_v2/imagegen_prompt.json. Generated window artwork is applied only through traced aperture masks. Structural normals and material masks are authored separately.
''')
(A/'source/README.md').write_text('''# Kurgen editable source

Continue from **kurgen_worn_pbr_v2.blend**. It contains the window/emissive and hull-relief revision. kurgen_worn_pbr_v1.blend is preserved as the first-pass snapshot. Do not rebuild over the latest scene using an earlier recipe.

The native hull and damage mesh, three mounted turret instances, UVs, custom mesh normals and transforms are preserved. The v2 scene's packed textures and relative resources were verified by reopening it. Runtime retains separate native models and their original animation and detail levels.

maps/windows_relief_v2 contains current hull maps, generated window artwork and aperture/glass/structural masks. authoring/windows_relief_v2 contains the prompt, source recipes and validation. review/windows_relief_v2 contains Blender inspection views; these are not public gallery photos. Previous source, maps and evidence remain for provenance.
''')
compat=dict(status='passed',scope='Non-visual native-format, texture-loader and asset checks',checked_at_utc=now,minimum_engine='0.8.1',review_engine='Official OpenReliant 0.18.0',review_engine_sha256=sha(G/'releases/openreliant-v0.18.0-linux-x86_64/openreliant'),native_checks=native,texture_loader=checks['emissive_loader'],duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user_revision_1_1')
dump(W/'compatibility.json',compat);dump(A/'compatibility-0.8.json',compat)
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='material-revision-awaiting-user-review',ship='Kurgen',asset_revision='1.1',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
release=read(A/'release.json');release.update(asset_revision='1.1',status='held',hold_reason='Window emissive and stronger hull relief revision awaits user in-game review',user_approved=False,published=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));dump(A/'release.json',release)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,asset_revision='1.1',user_approved=False,packaging_ready=False,game_launched=False,review_engine='0.18.0',minimum_openreliant='0.8.1',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),checks=['Native models and mission pass official 0.8.1 and 0.18.0 checks','Emissive map and mip levels pass the official 0.8.1 texture-loader probe','Base colour unchanged outside window apertures; frames and hull non-emissive','Structural normal strength increased; flat painted graphics and normalized vectors verified','Native models, shared turret and mission byte-identical to first pass','Packed portable scene reopened and compared','Both sides, rear, belly and dark authoring views reviewed'],runtime_visual_review='pending_user_revision_1_1')
dump(A/'validation.json',validation)
# Install exact reviewed repository output, keeping a preserved first-pass rollback in this workspace.
with tempfile.TemporaryDirectory(prefix='.kurgen-v2-install-',dir=G) as tmp:
    tmp=Path(tmp);stage=tmp/O.name;shutil.copytree(A/'mods'/O.name,stage)
    for q in manifest:assert sha(stage/Path(q['path']).name)==q['sha256']
    os.rename(I,tmp/'prior')
    try:os.rename(stage,I)
    except BaseException:os.rename(tmp/'prior',I);raise
for q in manifest:assert sha(A/q['path'])==sha(I/Path(q['path']).name)==q['sha256']
subprocess.run(['bash','-n',str(G/'launch-kurgen-test.sh')],check=True)
assert sha(G/'launch-kurgen-test.sh')==sha(A/'tools/launch-kurgen-test.sh')
deployment=dict(status='installed_ready_for_review',installed_at_utc=now,repository_asset=str(A),installed_mod=str(I),runtime_files=manifest,exact_repository_bytes_verified=True,launcher=str(G/'launch-kurgen-test.sh'),game_launched=False,runtime_visual_review='pending_user_revision_1_1',rollback=str(W/'installed_before_v2'))
dump(W/'deployment.json',deployment)
state=read(D.parent/'project_state.json');state.update(status='windows_and_relief_revision_ready_for_review',latest_scene=str(D/'kurgen_worn_pbr_v2.blend'),upright_scene=str(D/'kurgen_worn_pbr_v2.blend'),latest_deliverables=str(O.parent.parent),updated_at_utc=now,user_approved=False,published=False,baseline_user_feedback='First-pass appearance positively reviewed; user requested window emissives and stronger hull depth on 2026-10-17.',progress=dict(texture_uv='window_apertures_reauthored_rest_preserved',pbr_authoring='v2_window_emissives_and_stronger_hull_relief_complete',pbr_tuning='v2_authoring_views_checked_runtime_pending',engine_validation='0_8_1_and_0_18_0_non_visual_checks_passed'),engine_validation=dict(build='Official OpenReliant 0.18.0',minimum='0.8.1',non_visual_checks='passed',visual_review='pending_user_revision_1_1',game_launched=False,evidence=str(W/'compatibility.json')),window_and_relief_revision=dict(artwork_revision='1.1',scene=val['scene'],maps=val['maps'],checks=str(W/'map_checks.json'),panel_depth_multiplier=4.2,machinery_depth_multiplier=2.8,emission='window panes',turret_materials_unchanged=True))
dump(D.parent/'project_state.json',state)
prior=read(W/'prior_manifest.json');maps=prior['maps'];maps['hull']=val['maps']
dump(D/'manifest.json',dict(ship='Kurgen',variant='worn',artwork_revision='1.1',status=state['status'],user_approved=False,published=False,scene=rec(D/'kurgen_worn_pbr_v2.blend',D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],runtime_exports=manifest,maps=maps,remaining=['User in-game review of window brightness and hull depth','Campaign, turret tracking/firing, damage and distance transitions','Standard gallery photos after publication approval']))
(D/'README.md').write_text(readme+'\nCurrent editable scene: kurgen_worn_pbr_v2.blend. Launch '+str(G/'launch-kurgen-test.sh')+' for the installed revision; restart any running game. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom. First-pass scene, maps and runtime export are preserved.\n')
dump(W/'final-review-verification.json',dict(status='passed',checked_at_utc=now,runtime_files_verified=len(manifest),source_manifest_files_verified=len(read(A/'source-manifest.json')['files']),native_models_unchanged=True,turret_materials_unchanged=True,installed_exact_repository_bytes=True,game_launched=False,user_visual_review='pending_revision_1_1',published=False))
print(json.dumps(dict(status=state['status'],runtime_files=len(manifest),changed_albedo_percent=checks['changed_albedo_percent'],emission_percent=checks['emission_percent'],launcher=str(G/'launch-kurgen-test.sh')),indent=2))
