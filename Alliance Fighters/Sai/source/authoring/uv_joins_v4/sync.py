from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/uv_joins_v4';H=D/'history/stages/pre_uv_joins_v4'
A=Path('/home/lva-8700/.codex/.chatgpt-projects/g-p-6ac04f0d792c8191903a4b87653b44f6/work/release-preparation/repositories/OpenReliant-Art-Packs/Alliance Fighters/Sai')
GAME=Path('/home/lva-8700/Games/OpenReliant');MOD='100-sai-worn-v1';O=D/'exports/openreliant_v4/mods'/MOD
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();native=json.loads((W/'validation.json').read_text());source=json.loads((W/'source_validation.json').read_text());review=json.loads((W/'local_review.json').read_text())
assert native['passed'] and native['remaining_misread_faces']==0 and source['portable_snapshot_reopened'];assert sha(source['scene'])==source['scene_sha256'];assert sha(source['prior_scene'])==source['prior_scene_sha256'];assert sha(source['snapshot'])==source['snapshot_sha256']
for name in ['README.md','KNOWN_ISSUES.md','CHANGELOG.md','asset-manifest.json','source-manifest.json','validation.json','release.json','publication.json']:
 p=H/'repository'/name;p.parent.mkdir(exist_ok=True)
 if not p.exists():shutil.copy2(A/name,p)
shutil.copy2(__file__,W/'sync.py');author=A/'source/authoring/uv_joins_v4';author.mkdir(parents=True,exist_ok=True)
for name in ['validation.json','source_validation.json','local_review.json','native_groups.json','effective_uvs_before.json','effective_uvs_after.json','fix-native-uv-joins.py','review-exported-uvs.py','update-source.py','sync.py']:shutil.copy2(W/name,author/name)
shutil.copytree(D/'review/uv_joins_v4',A/'source/review/uv_joins_v4',dirs_exist_ok=True)
for p in O.iterdir():shutil.copy2(p,A/'mods'/MOD/p.name)
readme='''# Sai - Worn Paint

Artwork revision 4.0 is installed locally for user review. The public gallery and published beta remain unchanged.

This revision corrects the severe nose/canopy stretching introduced by the independent left/right texture remap. The native model still grouped triangles across the new UV seams. OpenReliant reuses shared texture coordinates inside those groups, which pulled unrelated artwork across the canopy and other surfaces. The export now splits the draw groups at incompatible UV joins at every detail level.

Only 140 primitive-continuation bytes change in the native model. All vertex data, face indices, individual UV coordinates, normals, winding, materials, attachments, animation, collision data and texture images are unchanged. The red **侍飛将** and black **神風** retain their approved scale, placement and readable orientation on both sides. The inspection scene retains its `fin down` command.

All 740 native faces were checked against the verified OpenReliant 0.7.0 corner-reuse rules. Local diagnostic renders reproduce the former streaks and show the corrected canopy from both sides. These are Blender diagnostic images, not in-game captures. Native-format round trips, portable source and repository-to-game file hashes passed. Final in-game appearance and gameplay remain pending user review.

Current scene: `source/sai_worn_pbr_v4.blend`. Run `tools/launch-sai-test.sh` for the quiet inspection scene.
'''
(A/'README.md').write_text(readme)
(A/'source/README.md').write_text('''# Sai editable source

Current scene: `sai_worn_pbr_v4.blend`, with the existing **Sai_Left_Right_UV_v2** layout. The scene's geometry, UVs, normals, materials and packed texture images are unchanged from revision 3. The added native draw-group metadata records the corrected runtime grouping at all detail levels; it is also embedded as `Sai_Native_Draw_Groups_v4.json`.

`authoring/uv_joins_v4/fix-native-uv-joins.py` splits native fan/strip continuations where their shared corners have different UV coordinates. This step is necessary after remapping individual faces: retaining the original groups across a new seam causes OpenReliant to reuse the wrong corner UVs. The exporter checks every continuation and preserves all bytes outside the grouping counters.

The verified engine references and detailed checks are in `authoring/uv_joins_v4/validation.json`. The existing `maps/kanji_v3/`, `maps/decals_v2/`, `decals/kanji_v1/` and decal placement records remain authoritative and unchanged. The red nose inscription reads 侍飛将 vertically and the black fin inscription reads 神風 horizontally on both sides.

`review/uv_joins_v4/` contains local diagnostic renders using the game's effective corner coordinates before and after the correction. These are not in-game captures. Previous source scenes, maps and authoring stages remain preserved.
''')
(A/'KNOWN_ISSUES.md').write_text('''# Review status

- Revision 4.0 is unpublished and awaits user in-game review. The earlier canopy stretching was reproduced locally using the native loader/draw rules and removed by correcting primitive continuations at UV seams.
- All 740 faces and all 20 detail meshes pass shared-corner checks. Broader gameplay, distance transitions and other platforms remain untested.
- Red nose and black tail lettering, material maps, model geometry and fin-deployment command are preserved.
- Custom emissives are deferred.
''')
p=A/'CHANGELOG.md';prior=p.read_text();heading='## Artwork 4.0 - local review, unpublished'
if heading not in prior:p.write_text('# Changelog\n\n'+heading+'\n\n- Fixed native triangle-fan/strip joins crossing the new left/right UV seams, including the stretched nose/canopy.\n- Checked shared corner coordinates across all 740 native faces and every detail level.\n- Preserved all authored UVs, geometry, markings, textures, materials and animation.\n\n'+prior.removeprefix('# Changelog').lstrip())
def records(root):return [{'path':p.relative_to(A).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
assets=records(A/'mods');write(A/'asset-manifest.json',assets);write(A/'source-manifest.json',{'status':'working-snapshot-awaiting-review','ship':'Sai','asset_revision':'4.0','files':records(A/'source')})
validation={'status':'local-checks-passed-runtime-review-pending','checked_at_utc':now,'asset_revision':'4.0','engine_build':'Official OpenReliant 0.7.0','user_approved':False,'runtime_launched':False,'runtime_visual_review':'pending_user_review','native_uv_join_checks':native,'source_checks':source,'local_rendering':review,'visual_checks':{'previous_streaking_reproduced':True,'corrected_canopy_both_sides':'passed','lettering_colour_placement_and_orientation':'preserved'},'asset_manifest_sha256':sha(A/'asset-manifest.json'),'source_manifest_sha256':sha(A/'source-manifest.json'),'remaining_work':['User in-game review and approval','Gameplay and distance transitions','Custom emissives deferred']};write(A/'validation.json',validation)
release=json.loads((A/'release.json').read_text());release.update(asset_revision='4.0',status='hold',hold_reason='Native UV-join correction awaits user in-game review.',user_approved=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));write(A/'release.json',release)
target=GAME/'game-data/mods'/MOD
for rec in assets:
 src=A/rec['path'];shutil.copy2(src,target/src.name);assert sha(target/src.name)==rec['sha256']
assert {p.name for p in target.iterdir()}=={Path(p['path']).name for p in assets}
launcher=GAME/'launch-sai-test.sh';assert launcher.is_file();subprocess.run(['bash','-n',str(launcher)],check=True)
deploy={'date_utc':now,'repository':str(A),'deployed_folder':str(target),'files':len(assets),'all_files_match':True,'asset_manifest_sha256':sha(A/'asset-manifest.json'),'launcher':str(launcher),'launcher_sha256':sha(launcher),'runtime_launched':False,'user_review':'pending','fin_down_command_in_inspection_scene':True};write(W/'deployment.json',deploy)
state=json.loads((D.parent/'project_state.json').read_text());assert state['latest_pass']=='kanji_v3'
for roles in state['maps'].values():
 for rec in roles.values():assert sha(rec['path'])==rec['sha256']
state.update(latest_scene=source['scene'],latest_pass='uv_joins_v4',asset_revision='4.0',status='native_uv_joins_corrected_and_deployed_for_review',texture_uv_status='native_uv_seams_validated_all_detail_levels_and_canopy_checked_both_sides',engine_validation='native_corner_reuse_format_and_deployment_checks_passed',runtime_visual_review='pending_user_review',runtime_launched=False,user_approved=False,published=False,repository_snapshot=source['snapshot'],deployment=deploy,checks=str(W/'validation.json'),remaining_work=validation['remaining_work'])
state['native_uv_join_repair']={'source_model':native['output'],'sha256':native['output_sha256'],'changed_continuation_records':native['changed_continuation_records'],'all_faces_checked':740,'all_other_native_fields_preserved':True,'texture_images_unchanged':True,'local_review':str(W/'local_review.json')};write(D.parent/'project_state.json',state);write(D/'manifest.json',state)
(D/'README.md').write_text(readme.replace('`source/sai_worn_pbr_v4.blend`','`sai_worn_pbr_v4.blend`')+'\nQuiet test launcher: `/home/lva-8700/Games/OpenReliant/launch-sai-test.sh`.\n')
print(json.dumps(deploy,indent=2))
