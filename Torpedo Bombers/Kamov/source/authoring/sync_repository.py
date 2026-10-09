import os
from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
D=Path(str(Path(os.environ['KAMOV_WORKSPACE'])));W=D/'work/reconstruction_v1'
R=Path(str(Path(os.environ['ART_PACKS_REPOSITORY'])));A=R/'Torpedo Bombers/Kamov';G=Path(str(Path(os.environ['OPENRELIANT_HOME'])));MOD='104-kamov-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
r=read(W/'validation.json');snap=read(W/'repository_snapshot.json');maps=read(W/'map_checks.json');native=read(W/'native_preservation.json');animation=read(W/'animation_preservation.json');runtime=read(W/'runtime_animation_checks.json');assert read(W/'source_animation_check.json')['passed']
assert maps['passed'] and native['passed'] and animation['passed'] and runtime['passed'] and snap['packed_relative_resources_reopened']
assert sha(r['scene'])==r['scene_sha256']==snap['canonical_sha256']
assert sha(snap['snapshot'])==snap['snapshot_sha256']
for sub in ['source/maps','source/originals','source/authoring','source/review/reconstruction_v1','source/review/animation_v1','source/audit','tools','mods/'+MOD]:(A/sub).mkdir(parents=True,exist_ok=True)
for source,dest in [(D/'maps',A/'source/maps'),(D/'source',A/'source/originals'),(W,A/'source/authoring'),(D/'work/model_audit_v1',A/'source/audit'),(D/'review/reconstruction_v1',A/'source/review/reconstruction_v1'),(D/'review/animation_v1',A/'source/review/animation_v1'),(D/'exports/openreliant_v1/mods'/MOD,A/'mods'/MOD)]:
 for p in source.iterdir():
  if p.is_file():shutil.copy2(p,dest/p.name)
for mode in ['stowed','deployed','launch']:
 p=D/f'exports/launch-kamov-{mode}-test.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nscript_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)\nexec "$script_dir/launch-kamov-test.sh" '+mode+' "$@"\n');p.chmod(0o755)
for p in (D/'exports').glob('*.sh'):shutil.copy2(p,A/'tools'/p.name);(A/'tools'/p.name).chmod(0o755);subprocess.run(['bash','-n',str(p)],check=True)
(A/'README.md').write_text('''# Kamov - Worn Paint

First worn pass installed for local review. Artwork is not approved or published.

The playable Kamov in mission 25 and the AI use the same ship type (45) and exterior model, `Rus_Kamov.SHP`. One replacement covers both. The separate `kamG_frm.SHP` cockpit interior is unchanged. Engine and mission-file findings are retained in `source/audit/model-audit.json`.

Restores the grey and red Coalition livery, stars, hazard bands and smooth amber glazing. Structural normal maps follow traced panel and radiator detail; painted markings stay flat. All 16 native parts, every deployment keyframe, mount, launch point and collision record are preserved. Native strip/fan continuation repairs prevent texture-coordinate reuse across seams throughout all 1,641 faces and detail levels.

The quiet test scene carries four torpedoes. Separate stowed, deployed, repeating-cycle and manual-launch modes exercise the native mechanism. The bounded official OpenReliant 0.7.0 test verified all four torpedoes move with their carriers and return to the initial position. Broader mission 25 play and user visual review remain pending.

Use `tools/launch-kamov-test.sh` to cycle the bays. Standalone stowed/deployed launchers are also provided. See `INSTALL.md` and `KNOWN_ISSUES.md`.
''')
(A/'INSTALL.md').write_text('''# Local review installation

Requires your own StarLancer files and official OpenReliant 0.7.0. Copy the flat `mods/104-kamov-worn-v1` folder into `game-data/mods` and enable it. This replaces the shared player/AI exterior.

Place all four `tools/launch-kamov*.sh` scripts in your OpenReliant installation, alongside its `releases` and `game-data` directories. Or set OPENRELIANT_HOME to that installation and run the scripts from their tools directory. The review launcher explicitly uses `releases/openreliant-v0.7.0-linux-x86_64/openreliant`.

- `launch-kamov-test.sh`: starts stowed for eight seconds, then repeatedly opens for four seconds, holds open for roughly eight, closes for four and holds closed for roughly eight.
- `launch-kamov-stowed-test.sh`: holds the bays closed.
- `launch-kamov-deployed-test.sh`: opens the bays over four seconds and holds them open.
- `launch-kamov-launch-test.sh`: use the game's Launch Missile control to release the torpedoes. After all four finish launching, the bays close. Manual firing remains for user review.

Press 7 for orbit view, arrow keys to rotate, Shift+Up/Down to zoom, and 0 to capture a screenshot. Missions 984–987 contain one Kamov and four carried torpedoes, no enemies or objectives. Engines are disabled for inspection. The first three modes disable firing to preserve all four torpedoes for viewing.

The torpedoes use the existing Coalition torpedo asset. If the approved ordnance pack is installed, its art is reused automatically; the Kamov pack does not duplicate it. Remove or disable this mod to restore the original exterior. Other ship inspection missions are unaffected.
''')
(A/'KNOWN_ISSUES.md').write_text('''# Review status

- User visual review and material tuning remain pending. First worn pass; not approved for beta publication.
- Player/AI asset identity is verified from official engine source and native mission records. Full mission 25 gameplay, AI combat, cloaking, damage, ejection and distance transitions have not been played through with this pack.
- Stowing, deploying and cycling with four carried torpedoes passed bounded runtime verification. Manual missile firing and the post-launch closing mode need user gameplay review.
- Cockpit interior assets are preserved unchanged. Custom emissive maps are deferred. Only Linux runtime has been tested.
- The original 256-square atlas was reconstructed at 1254-square, with 4096-square delivery maps; delivery size does not imply generated native 4K detail.
''')
(A/'CHANGELOG.md').write_text('''# Changelog

## Artwork 1.0 - awaiting review

- Confirmed shared player and AI exterior and retained the separate cockpit interior.
- Restored worn grey/red paint, stars, hazards and amber glazing, with structural PBR maps and editable masks.
- Preserved all 16 parts, including all four carriers, flaps and link rods, with original native deployment data.
- Checked all native LODs and repaired 173 primitive continuation counts at UV seams.
- Added four quiet native inspection missions, a cycling launcher, and a portable animated Blender source.
- Verified deployment, carried-torpedo travel and restowing in official OpenReliant 0.7.0.
''')
(A/'source/README.md').write_text('''# Kamov editable source

Current scene: `kamov_worn_pbr_v1.blend`. All 16 native parts and 670 highest-detail triangles are retained, with original custom normals and UVs. The earlier converted scene omitted two link rods and was not used as the master.

Timeline frame 1 is stowed; frame 101 is deployed (25 fps). Preview poses reproduce the native angle, offset and mount-axis transforms. The game export retains the original animation chunks verbatim and is not rebuilt from Blender or GLTF. The latter does not carry the native deployment tracks.

Images are packed and duplicated under relative `resources/` paths. The snapshot was reopened and checked against canonical geometry, UVs, normals and materials. `originals/native_parts.json` retains every LOD and native keyframe. `Original_Kamov_UV` and `Kamov_Delivery_UV_v1` initially match. Native primitive continuation corrections must be retained on future exports.

`maps/` holds the restored base colour, normal, roughness, metallic and supporting masks. `authoring/` holds exact generation prompts, region traces and build/check scripts. `audit/` records player/AI identity and native structure. Local Blender previews in `review/reconstruction_v1/` are authoring views; `review/animation_v1/` contains bounded in-game animation-state evidence.
''')
for name in ['CREDITS.md','LICENSING.md']:shutil.copy2(R/'Coalition Fighters/Basilisk'/name,A/name)
shutil.copy2(__file__,W/'sync_repository.py');shutil.copy2(__file__,A/'source/authoring/sync_repository.py')
def manifest(root):return [dict(path=p.relative_to(A).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(root.rglob('*')) if p.is_file()]
assets=manifest(A/'mods');write(A/'asset-manifest.json',assets);write(A/'source-manifest.json',dict(status='working-snapshot-awaiting-review',ship='Kamov',asset_revision='1.0',files=manifest(A/'source')))
now=datetime.datetime.now(datetime.timezone.utc).isoformat();engine=G/'releases/openreliant-v0.7.0-linux-x86_64/openreliant'
v=dict(status='animation-checks-passed-artwork-review-pending',checked_at_utc=now,asset_revision='1.0',engine_build='Official OpenReliant 0.7.0',engine_sha256=sha(engine),runtime_visual_review='pending_user_review',user_approved=False,shared_player_ai_exterior=True,native_preservation=native,animation_preservation=animation,runtime_animation=runtime,map_checks=maps,source_snapshot_verified=True,tested_platforms=['Linux x86_64'],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),remaining_work=['User in-game visual review','Manual missile launch and post-launch close review','Full mission 25 and AI combat, cloaking, damage, ejection and distance transitions','Custom emissives deferred'])
write(A/'validation.json',v)
write(A/'release.json',dict(package_name='openreliant-kamov',version='0.1.0-beta.1',asset_revision='1.0',status='hold',hold_reason='Awaiting user visual review and approval.',minimum_openreliant='0.7.0',mod_folders=[MOD],asset_manifest_sha256=v['asset_manifest_sha256'],source_manifest_sha256=v['source_manifest_sha256'],channel='beta',user_approved=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json']+[str(p.relative_to(A)) for p in sorted((A/'tools').glob('*.sh'))]))
target=G/'game-data/mods'/MOD;assert not target.exists(),'Reconcile existing deployment before overwrite';target.mkdir()
for rec in assets:
 p=A/rec['path'];shutil.copy2(p,target/p.name);assert sha(target/p.name)==rec['sha256']
assert {p.name for p in target.iterdir()}=={Path(x['path']).name for x in assets}
for p in (A/'tools').glob('*.sh'):
 dest=G/p.name;assert not dest.exists();shutil.copy2(p,dest);dest.chmod(0o755);assert sha(dest)==sha(p)
deploy=dict(date_utc=now,repository=str(A),deployed_folder=str(target),files=len(assets),all_files_match=True,asset_manifest_sha256=v['asset_manifest_sha256'],launcher=str(G/'launch-kamov-test.sh'),launcher_sha256=sha(G/'launch-kamov-test.sh'),user_review='pending');write(W/'deployment.json',deploy)
state=read(D.parent/'project_state.json');state.update(latest_scene=r['scene'],latest_pass='reconstruction_v1',asset_revision='1.0',status='first_worn_pass_and_animation_tests_ready_for_review',maps=r['maps'],texture_uv_status='first_pass_complete_original_UVs_retained_native_continuation_seams_fixed',pbr_authoring='complete',pbr_tuning='local_review_complete_user_game_review_pending',engine_validation='official_0.7.0_bounded_animation_checks_passed',engine_build=v['engine_build'],engine_sha256=v['engine_sha256'],runtime_visual_review='pending_user_review',user_approved=False,published=False,emissives='deferred',repository_snapshot=snap['snapshot'],deployment=deploy,launcher=deploy['launcher'],remaining_work=v['remaining_work']);write(D.parent/'project_state.json',state);write(D/'manifest.json',state)
(D/'README.md').write_text((A/'README.md').read_text()+'\nCanonical scene: `kamov_worn_pbr_v1.blend`. Launcher: `$OPENRELIANT_HOME/launch-kamov-test.sh`. PBR release gate is satisfied by installed official OpenReliant 0.7.0. Runtime animation evidence: `work/reconstruction_v1/runtime_animation_checks.json`.\n')
category=R/'Coalition Fighters/README.md';index=category.read_text();assert '[Kamov]' not in index;index=index.replace('\n\nFurther Coalition','\n| [Kamov](Kamov/README.md) | First worn pass installed; deployment cycle verified | Awaiting artwork approval |\n\nFurther Coalition');category.write_text(index)
print(json.dumps(deploy,indent=2))
