from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn');W=D/'work/kanji_v3';H=D/'history/stages/pre_kanji_v3'
A=Path('/home/lva-8700/.codex/.chatgpt-projects/g-p-6ac04f0d792c8191903a4b87653b44f6/work/release-preparation/repositories/OpenReliant-Art-Packs/Alliance Fighters/Sai')
GAME=Path('/home/lva-8700/Games/OpenReliant');MOD='100-sai-worn-v1';O=D/'exports/openreliant_v3/mods'/MOD
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=json.loads((W/'scene_validation.json').read_text());art=json.loads((W/'placement.json').read_text());export=json.loads((W/'export_validation.json').read_text());snap=json.loads((W/'repository_snapshot.json').read_text())
assert export['passed'] and snap['packed_relative_resources_reopened'] and art['all_pixels_outside_decal_alpha_identical'];assert sha(r['scene'])==r['scene_sha256']==snap['canonical_sha256'];assert sha(r['prior_scene'])==r['prior_scene_sha256']
for p in art['placements']:assert p['mirrored'] is False and sha(p['source'])==p['source_sha256']
for name in ['README.md','KNOWN_ISSUES.md','CHANGELOG.md','asset-manifest.json','source-manifest.json','validation.json','release.json','publication.json']:
 p=H/'repository'/name;p.parent.mkdir(exist_ok=True)
 if not p.exists():shutil.copy2(A/name,p)
shutil.copy2(__file__,W/'sync.py')
for src,dest in [(D/'maps/kanji_v3',A/'source/maps/kanji_v3'),(D/'decals/kanji_v1',A/'source/decals/kanji_v1'),(D/'review/kanji_v3',A/'source/review/kanji_v3')]:shutil.copytree(src,dest,dirs_exist_ok=True)
author=A/'source/authoring/kanji_v3';author.mkdir(parents=True,exist_ok=True)
for name in ['placement.json','scene_validation.json','repository_snapshot.json','export_validation.json','inspection_script.txt','inspection.py','place-kanji.py','update-scene.py','portable-source.py','export.py','sync.py','panel_gap_protection.svg']:
 shutil.copy2(W/name,author/name)
for p in O.iterdir():shutil.copy2(p,A/'mods'/MOD/p.name)
readme='''# Sai - Worn Paint

Artwork revision 3.0 is installed locally for review. The public gallery and published beta remain unchanged.

The approved painted decals are now scaled to the original marking locations: red **侍飛将** vertically on the nose and black **神風** across the lower fin. Each side has an independent upright placement, with correct reading order and the original panel gaps visible through the paint. Both sides were checked in local Blender views. The generated PNG colours and the rest of the existing livery are retained.

The quiet inspection mission now explicitly plays the native `fin down` animation after spawning the Sai, matching the deployment command used by the original missions. This corrects the earlier folded-fin inspection setup. The native ship file, geometry, all distance-model UVs, normals, material maps and attachments are unchanged from revision 2.0. Flight and loadout use identical replacement textures.

The source images and placement layer remain separately editable. Native format, texture checks, source portability and exact repository-to-game hashes passed. In-game appearance and fin deployment still await user review on official OpenReliant 0.7.0.

Run `tools/launch-sai-test.sh` for the quiet scene. Current editable source: `source/sai_worn_pbr_v3.blend`.
'''
(A/'README.md').write_text(readme)
(A/'source/README.md').write_text('''# Sai editable source

Current scene: `sai_worn_pbr_v3.blend`, with the existing **Sai_Left_Right_UV_v2** layout. Images are packed and have verified portable relative resources.

`decals/kanji_v1/` contains the approved transparent source PNGs and their generation prompts. `maps/kanji_v3/sai_kanji_decals_lr_v3.png` is the full-size transparent placement layer; `maps/kanji_v3/sai_sam1_basecolor_lr_v3.png` is its composite over the revision 2 body atlas. All other material maps remain in `maps/decals_v2/`.

The nose reads 侍飛将 from top to bottom and the fin reads 神風 from left to right. Both atlas halves have independent placements; the characters themselves are not mirrored. `authoring/kanji_v3/placement.json` records scale, crop and placement coordinates, with the original source-image checksums. Physical panel gaps are protected by the separate placement mask.

The previous scenes and maps, wave artwork, rising-sun motif, native geometry, UVs, normals, animation records and attachments are preserved. Local review pictures use Blender studio lighting and the unanimated fin-down authoring pose. The inspection mission plays the preserved native deployment animation; in-game review is pending.
''')
(A/'KNOWN_ISSUES.md').write_text('''# Review status

- Revision 3.0 is unpublished and awaits user in-game review and approval. Both sides were checked locally for decal colour, scale and reading direction.
- The inspection mission now requests `fin down`; its native format and script round trip pass. In-game visual confirmation remains pending.
- Distance transitions, mounted weapons, firing and damage behavior still need broader gameplay review.
- Custom emissives are deferred. Other platforms have not been tested.
''')
p=A/'CHANGELOG.md';prior=p.read_text();heading='## Artwork 3.0 - local review, unpublished'
if heading not in prior:
 p.write_text('# Changelog\n\n'+heading+'\n\n- Placed red 侍飛将 and black 神風 at their original locations, reading normally on both sides.\n- Preserved panel gaps, other artwork, geometry, UVs, normals and material maps.\n- Corrected the inspection scene to play the original fin-down deployment animation.\n\n'+prior.removeprefix('# Changelog').lstrip())
def records(root):return [{'path':p.relative_to(A).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
assets=records(A/'mods');write(A/'asset-manifest.json',assets);write(A/'source-manifest.json',{'status':'working-snapshot-awaiting-review','ship':'Sai','asset_revision':'3.0','files':records(A/'source')})
validation={'status':'local-checks-passed-runtime-review-pending','checked_at_utc':now,'asset_revision':'3.0','engine_build':'Official OpenReliant 0.7.0','runtime_launched':False,'runtime_visual_review':'pending_user_review','user_approved':False,'native_and_map_checks':export,'art_checks':{k:v for k,v in art.items() if k!='maps'},'mesh_preservation':{k:v for k,v in r.items() if k!='maps'},'source_snapshot_verified':True,'local_visual_review':{'left':'passed: upright red 侍飛将 and black 神風','right':'passed: upright red 侍飛将 and black 神風','images':['source/review/kanji_v3/side_left.png','source/review/kanji_v3/side_right.png']},'asset_manifest_sha256':sha(A/'asset-manifest.json'),'source_manifest_sha256':sha(A/'source-manifest.json'),'remaining_work':['User in-game review and approval','Gameplay and distance transitions','Custom emissives deferred']}
write(A/'validation.json',validation);write(W/'validation.json',validation)
release=json.loads((A/'release.json').read_text());release.update(asset_revision='3.0',status='hold',hold_reason='Placed character decals and corrected inspection pose await user in-game review.',user_approved=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));write(A/'release.json',release)
target=GAME/'game-data/mods'/MOD
for rec in assets:
 src=A/rec['path'];shutil.copy2(src,target/src.name);assert sha(target/src.name)==rec['sha256']
assert {p.name for p in target.iterdir()}=={Path(q['path']).name for q in assets}
launcher=GAME/'launch-sai-test.sh';shutil.copy2(A/'tools/launch-sai-test.sh',launcher);launcher.chmod(0o755);subprocess.run(['bash','-n',str(launcher)],check=True)
deploy={'date_utc':now,'repository':str(A),'deployed_folder':str(target),'files':len(assets),'all_files_match':True,'asset_manifest_sha256':sha(A/'asset-manifest.json'),'launcher':str(launcher),'launcher_sha256':sha(launcher),'runtime_launched':False,'user_review':'pending','fin_down_command_in_inspection_scene':True};write(W/'deployment.json',deploy)
state=json.loads((D.parent/'project_state.json').read_text());state.update(latest_scene=r['scene'],latest_pass='kanji_v3',asset_revision='3.0',status='correctly_oriented_kanji_placed_and_deployed_for_review',style='Worn silver-grey and bronze with restored red 侍飛将 and black 神風, refined wave and preserved rising-sun motif',maps=r['maps'],texture_uv_status='both_sides_and_decal_colours_checked_locally',pbr_authoring='existing_material_maps_preserved',pbr_tuning='existing_values_preserved_in_game_review_pending',engine_validation='native_format_texture_and_deployment_checks_passed',runtime_visual_review='pending_user_review',runtime_launched=False,user_approved=False,published=False,repository_snapshot=snap['snapshot'],deployment=deploy,checks=str(W/'validation.json'),remaining_work=validation['remaining_work']);state['kanji_decal_assets'].update(status='scaled_and_placed_on_both_sides_pending_user_runtime_review',applied_to_ship=True,placement_manifest=str(W/'placement.json'),placement_layer=str(D/'maps/kanji_v3/sai_kanji_decals_lr_v3.png'));state['inspection_pose']={'clip':'fin down','requested_at_spawn':True,'native_animation_preserved':True,'runtime_review':'pending'}
write(D.parent/'project_state.json',state);write(D/'manifest.json',state)
(D/'README.md').write_text(readme.replace('`source/sai_worn_pbr_v3.blend`','`sai_worn_pbr_v3.blend`')+'\nCanonical maps: `maps/kanji_v3/` (body colour and editable placement layer) and `maps/decals_v2/` (remaining maps). Placement records: `work/kanji_v3/placement.json`.\n\nQuiet test launcher: `/home/lva-8700/Games/OpenReliant/launch-sai-test.sh`.\n')
print(json.dumps(deploy,indent=2))
