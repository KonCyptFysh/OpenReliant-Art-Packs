from pathlib import Path
import json,hashlib,datetime,shutil,subprocess,os
D=Path('${PROWLER_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_18_v1/mods/117-prowler-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Corvettes and Gunboats/Prowler';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.18.0-linux-x86_64'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,v):write(p,json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
checks=read(W/'native_checks.json');maps=read(W/'map_checks.json');pres=read(W/'native_preservation.json');snap=read(W/'repository_snapshot.json');tiers=read(W/'resolution_checks.json');art=read(W/'validation.json')
assert all(c['exit_code']==0 for c in checks) and maps['passed'] and pres['passed'] and snap['packed_relative_resources_reopened'] and tiers['status']=='passed'
assert sum(x['faces'] for p in pres['files'] for x in p['detail_meshes'])==1593
assert sha(art['scene'])==art['scene_sha256']
parts=read(D/'source/native_parts.json')
assert len(parts)==6 and len([a for a in parts[2]['attachments'] if a['kind']==1])==4
for p in parts:
 for track in p['tracks']:
  assert len({tuple(k['angles']+k['offset']) for k in track['keys']})<=1
mapping=dict(ship_type=30,model='US_Prowler.SHP',native_parts=6,intact_parts=5,detail_level_count_max=7,stored_faces_all_lods=1593,gun_mounts=4,shared_turret='14_al_STUR.SHP',shared_turret_art='Original shared Missiles texture retained; no global weapons-atlas override',hull_animation='Native clip records have identical keyframes; no deployment motion',preservation='Geometry, per-corner UVs, normals, collision, attachments, animation, flags and wreck data preserved byte-for-byte; only material names and incompatible continuation counts changed',window_scope='Only original PROW_1 blue glazing regions emit',dynamic_lighting='Window emission static for first appearance review. Kurgen damage/throttle/heat system has not been ported.',native_engine_effects='Preserved; no point lights or engine glows removed')
dump(W/'model_mapping_audit.json',mapping)
authoring=dict(kind='Blender authoring renders; not game captures',views=['front','opposite','rear','belly'],reviewed_at_utc=now,observations=['Original grey/green worn hull, caution bands, US flag, unit markings and machinery retained.','Four native turret instances included in review assembly; shared artwork unchanged.','Inset blue glazing with frames retained and emission only inside glass.','Structural normals separate from flat painted decals; vents remain non-emissive.'],runtime_visual_review='pending_user')
dump(W/'authoring_review.json',authoring)
compat=dict(status='passed',scope='Non-visual native format, map and official texture-loader checks',checked_at_utc=now,minimum_engine='0.18.0',review_engine='Official OpenReliant 0.18.0',review_engine_sha256=sha(E/'openreliant'),native_checks=checks,resolution_checks=tiers,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility.json',compat)
shutil.copy2(__file__,W/'finish_review.py');shutil.copy2('/tmp/prowler_tiers.py',W/'prepare_review_tiers.py')
for sub in ['source/originals','source/maps','source/authoring','source/review/reconstruction_v1','tools']:(A/sub).mkdir(parents=True,exist_ok=True)
shutil.copytree(D/'source',A/'source/originals',dirs_exist_ok=True)
for p in (D/'maps').glob('*.png'):shutil.copy2(p,A/'source/maps'/p.name)
replacements=[(str(D),'${PROWLER_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(G),'${OPENRELIANT_HOME}'),('${ART_SOURCE_ROOT}','${ART_SOURCE_ROOT}'),('${IMAGEGEN_ARCHIVE}','${IMAGEGEN_ARCHIVE}')]
for p in W.iterdir():
 if p.is_file() and p.suffix in ['.py','.json','.txt','.luau','.log']:
  s=p.read_text()
  for old,new in replacements:s=s.replace(old,new)
  write(A/'source/authoring'/p.name,s)
for p in (D/'review/reconstruction_v1').glob('*.png'):shutil.copy2(p,A/'source/review/reconstruction_v1'/p.name)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
launcher=A/'tools/launch-prowler-test.sh';shutil.copy2(O.parent.parent/'launch-prowler-test.sh',launcher);launcher.chmod(0o755);subprocess.run(['bash','-n',str(launcher)],check=True)
joins=sum(len(p['continuation_corrections']) for p in pres['files'])
write(A/'README.md',f'''# Prowler - Worn Paint

**First pass ready for in-game review. Not approved or published.** Artwork revision 1.0; planned beta 0.1.0-beta.1. Requires official OpenReliant 0.18.0.

Two reconstructed grey/green worn hull atlases, original national/unit markings and caution paint, structural normal/roughness/metallic maps, recessed blue glazing and restrained window emission. The stronger structural relief follows the capital-ship treatment; painted markings remain flat. Vents are not windows and do not emit.

Original geometry, normals, per-corner UVs, collision, attachments and animation are retained across all six parts and up to seven detail levels. All 1,593 stored faces checked; {joins} incompatible primitive continuation counts corrected at native texture joins. Engine assembly clips contain identical keyframes, with no deployment movement.

Four native Alliance small turrets remain active in normal gameplay. Their shared model and Missiles atlas are unchanged. Existing engine effects and lights are retained. Window emission is static in this first pass; the Kurgen damage/throttle/heat behaviour has not yet been adapted to this ship.

Native and texture-loader checks passed. Both sides, rear and belly inspected in Blender. Actual in-game appearance awaits user review. Local 1K/2K review exports are generated alongside the 4K master; public packages remain on hold until approval.
''')
write(A/'INSTALL.md','''# Installation and review

Copy `mods/117-prowler-worn-v1` into OpenReliant's `game-data/mods`. Requires your own StarLancer data and OpenReliant 0.18.0.

Place `tools/launch-prowler-test.sh` beside `launch-openreliant.sh`, or set OPENRELIANT_HOME to the installation. It opens mission 961 with a quiet, invulnerable, stationary Prowler and four native turret mounts.

Press 7 for orbit; arrows rotate; Shift+Up/Down zoom; 0 saves a screenshot. Restart the game after changing textures. The inspection mission disables combat and thrust; campaign behaviour is unchanged.

Install one texture resolution per asset. Replace the same native mod folder when switching; do not enable tiers side by side.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- In-game appearance awaits user review. No automated game photography was run.
- Full campaign, damage, turret aiming/firing, detail transitions and other platforms remain untested; native records are preserved and validated.
- Shared Alliance turret artwork remains the original Missiles atlas. No global weapons-atlas replacement is introduced.
- Window emission is static. The Kurgen's damage-responsive cabin lighting, throttle response and retained heat have not yet been adapted to Prowler geometry.
- Delivery maps are 4096 square, resampled from 1254-square reconstructions of the two original 256-square atlases. Lower tiers preserve aligned colour, normal, ORM and emissive maps.
- Original shared DAM_1 damage artwork remains unchanged.
- Publication requires user approval, fresh standard engine gallery photographs and verified 1K/2K/4K downloads.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.0

First worn Prowler restoration with two reconstructed hull atlases, structural surface maps, inset glazing and original-window emission. Native geometry and four turret mounts retained, with 65 primitive continuation repairs across all detail levels. Quiet inspection mission and local resolution exports prepared; user review pending.
''')
write(A/'CREDITS.md','''# Credits

Restoration contributions by KonCyptFysh. Original StarLancer assets retain their respective owners' rights. OpenReliant provides the engine and native tools.

Built-in image generation reconstructed the two original atlases and cleaned baked glass reflections. The exact three prompts are retained in source/authoring/imagegen-prow1.txt, imagegen-prow2.txt and imagegen-glass.txt; original outputs remain in source/maps. Structural masks and material maps are authored separately in the Blender recipe.
''')
write(A/'LICENSING.md',"# Licensing\n\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . Original StarLancer assets retain their respective ownership and rights. Requires your own StarLancer data.\n")
write(A/'source/README.md','''# Prowler editable source

Start from `prowler_worn_pbr_v1.blend`. It retains original geometry and UV layers, the active delivery UV layer, packed material maps and four mounted native turret instances for authoring review. The damage part is hidden in the intact view. Runtime still uses the native independent turret model and preserves original wreck data.

The saved source was reopened and its geometry, UVs, normals and relative packed resources verified. `originals/` preserves native models, original textures and decoded records; `maps/` preserves reconstructions, delivery maps and material masks. `authoring/` contains exact image-generation prompts, recipes and validation evidence. Recipes document authoring history and require the named environment paths; they are not a one-command portable rebuild.

`review/` contains Blender authoring views, not public gallery photography.
''')
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()]
dump(A/'asset-manifest.json',manifest);dump(A/'source-manifest.json',dict(status='first-pass-awaiting-user-review',ship='Prowler',asset_revision='1.0',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
# Public evidence uses portable paths, not local machine locations.
portable=json.dumps(compat)
for old,new in replacements:portable=portable.replace(old,new)
dump(A/'compatibility-0.18.json',json.loads(portable))
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,review_engine='0.18.0',minimum_openreliant='0.18.0',asset_revision='1.0',user_approved=False,packaging_ready=False,game_launched=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),checks=['Native SHP and quiet mission validated on official 0.18.0','1593 faces checked; geometry, UVs, normals, attachments and animations preserved','Normalized structural normals, flat decals and matching material-map dimensions','1K/2K/4K official material-loader probes passed','Packed source reopened and compared','Both sides, rear and belly reviewed in Blender'],runtime_visual_review='pending_user')
dump(A/'validation.json',validation)
dump(A/'release.json',dict(package_name='openreliant-prowler',version='0.1.0-beta.1',asset_revision='1.0',status='held',hold_reason='Awaiting user in-game review',minimum_openreliant='0.18.0',mod_folders=[O.name],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),channel='beta',user_approved=False,published=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json','compatibility-0.18.json','tools/launch-prowler-test.sh']))
catalog=read(R/'catalog.json');entry=next(x for x in catalog['assets'] if x['id']=='prowler');assert entry['status']=='coming-soon';entry.update(folder='Corvettes and Gunboats/Prowler',workStatus='in-progress',description='Worn Alliance escort-corvette restoration with recessed blue windows and structural surface maps. First pass awaiting in-game review.');entry['liveries'][0].update(engine='0.18.0',engineStatus='non-visual-checks-passed-review-pending',notes=['First pass ready for review; no public download yet.','Two reconstructed hull atlases, original-window emission and four preserved native turrets.','Local 1K/2K/4K texture exports checked.'])
dump(R/'catalog.json',catalog)
state=read(D.parent/'project_state.json');state.update(ship_type=30,status='ready_for_user_review',latest_scene=str(D/'prowler_worn_pbr_v1.blend'),upright_scene=str(D/'prowler_worn_pbr_v1.blend'),latest_deliverables=str(O.parent.parent),repository_asset=str(A),review_launcher=str(G/'launch-prowler-test.sh'),updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='first_pass_complete_pending_review',pbr_authoring='complete_structural_and_window_maps',pbr_tuning='authoring_views_checked_runtime_pending',engine_validation='native_and_all_resolution_loader_checks_passed'),engine_validation=dict(build='Official OpenReliant 0.18.0',minimum='0.18.0',non_visual_checks='passed',visual_review='pending_user',game_launched=False,evidence=str(W/'compatibility.json')),current_manifest=str(D/'manifest.json'),shared_component_scope='Native Alliance small turret and shared Missiles atlas preserved unchanged',resolution_exports=[dict(tier=x['tier'],runtime=x['runtime']) for x in tiers['tiers']],dynamic_lighting='Static window emissives only for first review; native engine effects retained')
dump(D.parent/'project_state.json',state)
dump(D/'manifest.json',dict(ship='Prowler',variant='worn',status='ready_for_user_review',user_approved=False,published=False,scene=rec(D/'prowler_worn_pbr_v1.blend',D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],runtime_exports=manifest,maps=art['maps'],resolution_exports=state['resolution_exports'],remaining=['User in-game review','Campaign, damage, turret firing and detail transition checks','Dynamic damage/throttle lighting adaptation after material review','Publication and standard gallery photography after approval']))
write(D/'README.md',f'''# Prowler worn workspace

First pass ready for in-game review; not approved or published. Current source: prowler_worn_pbr_v1.blend. Two grey/green worn hull atlases, preserved national/unit markings and machinery, structural normal/metallic/roughness maps, inset blue glazing and static emission confined to original windows.

All 1,593 native faces and up to seven detail levels checked. Geometry, UVs, normals, collision, mounts, wreck and animation records retained; 65 incompatible texture-strip joins corrected. The engine parts' animation records contain no movement. Four native Alliance turrets remain unchanged, including their shared weapons atlas. Original engine effects are retained; Kurgen-style dynamic lighting is not yet ported.

Run {G}/launch-prowler-test.sh for a quiet single-ship scene. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, 0 for screenshots. The launcher is installed after the final byte-for-byte deployment check.

Native checks, material-loader checks at 1K/2K/4K, portable-source reopening and Blender views passed. Actual in-game appearance awaits your review.

Built-in image generation produced the two reconstructed atlases and glass cleanup. Exact prompts: work/reconstruction_v1/imagegen-prow1.txt, imagegen-prow2.txt, imagegen-glass.txt. Original outputs and source textures are retained. The 4K maps are resampled from 1254-square reconstructions. See manifest.json and ../project_state.json for status and hashes.
''')
print('PROWLER_REVIEW_SNAPSHOT_READY',len(manifest),sum(x['bytes'] for x in manifest),flush=True)
