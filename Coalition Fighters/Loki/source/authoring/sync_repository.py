from pathlib import Path
import json,hashlib,shutil,datetime,subprocess,re,os
D=Path(str(Path(os.environ['LOKI_WORKSPACE'])));W=D/'work/reconstruction_v1'
R=Path(str(Path(os.environ['ART_PACKS_REPOSITORY'])));A=R/'Coalition Fighters/Loki';G=Path(str(Path(os.environ['OPENRELIANT_HOME'])));MOD='105-loki-worn-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
r=read(W/'validation.json');snap=read(W/'repository_snapshot.json');maps=read(W/'map_checks.json');native=read(W/'native_preservation.json');animation=read(W/'animation_preservation.json')
assert maps['passed'] and native['passed'] and animation['passed'] and read(W/'source_animation_check.json')['passed'] and snap['packed_relative_resources_reopened']
assert sha(r['scene'])==r['scene_sha256']==snap['canonical_sha256']
assert sha(snap['snapshot'])==snap['snapshot_sha256']
for sub in ['source/maps','source/originals','source/authoring','source/review','source/audit','tools','mods/'+MOD]:(A/sub).mkdir(parents=True,exist_ok=True)
for source,dest in [(D/'maps',A/'source/maps'),(D/'source',A/'source/originals'),(W,A/'source/authoring'),(D/'work/model_audit_v1',A/'source/audit'),(D/'review/reconstruction_v1',A/'source/review'),(D/'exports/openreliant_v1/mods'/MOD,A/'mods'/MOD)]:
 for p in source.iterdir():
  if p.is_file():shutil.copy2(p,dest/p.name)
for mode in ['folded','fighting']:
 p=D/f'exports/launch-loki-{mode}-test.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nscript_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)\nexec "$script_dir/launch-loki-test.sh" '+mode+' "$@"\n');p.chmod(0o755)
for p in (D/'exports').glob('*.sh'):shutil.copy2(p,A/'tools'/p.name);(A/'tools'/p.name).chmod(0o755);subprocess.run(['bash','-n',str(p)],check=True)
(A/'README.md').write_text('''# Loki - Worn Paint

First worn pass prepared for local review. Artwork is not approved or published.

Restored worn grey industrial panels, hazard bands, warnings and smooth amber glazing, with restrained structural normal maps and separate roughness/metallic maps. Painted graphics and glass retain flat normals.

The replacement preserves all seven native parts, their hierarchy, original geometry, UVs, normals, attachments and animation keyframes. The original lower-detail material tables name the unrelated LIMPET atlas; this model now uses its restored Loki atlas at every detail level. No shared LIMPET texture is overridden. Primitive continuation repairs stop strips/fans from reusing texture coordinates across UV seams.

Use `tools/launch-loki-test.sh` to inspect the folding mechanism in a quiet single-ship scene. Fixed folded and fighting-position modes are also provided. These scenes and the native export pass format checks; in-game visual and animation review remain pending.

Editable source and exact image-generation prompts are under `source/`. See `INSTALL.md` and `KNOWN_ISSUES.md`.
''')
(A/'INSTALL.md').write_text('''# Local review installation

Requires your own StarLancer files and official OpenReliant 0.7.0. Copy the flat `mods/105-loki-worn-v1` folder into `game-data/mods` and enable it.

Place the three `tools/launch-loki*.sh` scripts alongside the installation's `game-data` and `releases` folders, or set OPENRELIANT_HOME to that installation. The launcher explicitly selects official OpenReliant 0.7.0.

- `launch-loki-test.sh`: starts in the initial folded pose and repeatedly moves to fighting position and back, with pauses to inspect each state.
- `launch-loki-folded-test.sh`: holds the initial folded pose.
- `launch-loki-fighting-test.sh`: plays the native four-second animation, then holds the fighting pose.

Press 7 for orbit view, arrow keys to rotate, Shift+Up/Down to zoom, and 0 for a screenshot. Missions 981–983 contain one Loki (type 65), no enemies or objectives. Engines and weapons are disabled only in these inspection scenes. Native mission script disassembly verifies the full `fighting position` track name and forward/reverse commands.

The shared game launcher and other inspection missions are unchanged. Remove or disable this mod to restore the original exterior.
''')
(A/'KNOWN_ISSUES.md').write_text('''# Review status

- User in-game visual review and material tuning are pending. Not approved for beta publication.
- Native model/mission format, original animation preservation, structural maps and portable source checks pass. The new inspection missions and animation cycle have not yet been reviewed in OpenReliant.
- AI gameplay, damage, distance transitions and other platforms remain untested. Cockpit interiors and custom emissive maps are outside this pass.
- Native mirrored markings and original UV repeats are retained. No lettering redesign or geometry remodel was requested.
- Original atlas: 256 square. Restored master: 1254 square. Delivery maps: 4096 square; this does not imply native generated 4K detail.
''')
(A/'CHANGELOG.md').write_text(f'''# Changelog

## Artwork 1.0 - awaiting review

- Restored worn machinery, grey panels, hazard stripes and flat painted warnings.
- Prepared smooth amber glass, structural normal maps and PBR material masks.
- Preserved all seven parts and native fighting-position animation.
- Checked all 1,535 faces across all detail levels and repaired {len(native['continuation_corrections'])} primitive continuation counts at UV seams.
- Directed both original material names to a unique Loki atlas without a global LIMPET override.
- Added three quiet single-ship review modes and a packed editable Blender source.
''')
(A/'source/README.md').write_text('''# Loki editable source

Current scene: `loki_worn_pbr_v1.blend`. Seven native parts, 526 highest-detail triangles, original custom normals and UVs. Child parts remain attached to their native parents. Frame 1 is the initial folded pose; frame 101 is fighting position at 25 fps. Intermediate poses reproduce native angle interpolation and mount-axis transforms.

Images are packed and also stored under relative `resources/` paths. Reopening the snapshot preserves geometry, normals, UVs, materials and five checked animation poses. `originals/native_parts.json` contains every original detail level and keyframe. The game model retains original native animation bytes; Blender is not used for an animation export round trip.

`Original_Loki_UV` and `Loki_Delivery_UV_v1` initially match. Preserve repeat sampling: some original coordinates intentionally extend beyond the atlas. Both original model material slots are mapped to `orlk1_hull`; flight and loadout variants use identical maps.

`maps/` holds colour and structural material maps and masks. `authoring/imagegen_prompts.json` records the two builtin image-generation edits. The first atlas interpretation was refined after model inspection identified the amber cockpit panes. `authoring/regions.json` records traced structural regions. No albedo-noise-to-normal conversion is used. `review/` images are Blender authoring views, not game captures or gallery photographs.

For authoring scripts set LOKI_WORKSPACE to the canonical worn workspace, ART_PACKS_REPOSITORY to this repository and OPENRELIANT_HOME to the installation. Historical build recipes are retained for reproducibility; continue from the latest scene and preserve later edits.
''')
for name in ['CREDITS.md','LICENSING.md']:shutil.copy2(R/'Coalition Fighters/Basilisk'/name,A/name)
# Public records carry symbolic roots. No local runtime logs or private machine paths are published.
roots=[(str(D),'LOKI_WORKSPACE'),(str(R),'ART_PACKS_REPOSITORY'),(str(G),'OPENRELIANT_HOME'),(str(Path(os.environ['STARLANCER_ASSETS'])),'STARLANCER_ASSETS')]
def cleantext(s):
 for root,key in roots:s=s.replace(root,'$'+key)
 return s
for p in (A/'source').rglob('*'):
 if p.suffix not in ('.py','.json','.txt','.md'):continue
 s=p.read_text()
 if p.suffix=='.py':
  def replace(m):
   path=m.group(2)
   for root,key in roots:
    if path==root or path.startswith(root+'/'):
     suffix=path[len(root):].lstrip('/');return "str(Path(os.environ["+repr(key)+"])"+(" / "+repr(suffix) if suffix else '')+")"
   return m.group(0)
  s=re.sub(r"(['\"])(/[^'\"\n]+)\1",replace,s)
  if 'os.environ' in s and 'import os' not in s:s='import os\n'+s
 s=cleantext(s)
 p.write_text(s)
def inventory(root):return [dict(path=p.relative_to(A).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(root.rglob('*')) if p.is_file()]
assets=inventory(A/'mods');write(A/'asset-manifest.json',assets);write(A/'source-manifest.json',dict(status='working-snapshot-awaiting-review',ship='Loki',asset_revision='1.0',files=inventory(A/'source')))
now=datetime.datetime.now(datetime.timezone.utc).isoformat();engine=G/'releases/openreliant-v0.7.0-linux-x86_64/openreliant'
v=dict(status='format-and-source-checks-passed-runtime-review-pending',checked_at_utc=now,asset_revision='1.0',target_engine='Official OpenReliant 0.7.0',target_engine_sha256=sha(engine),runtime_visual_review='pending_user_review',runtime_animation_review='pending_user_review',user_approved=False,native_preservation=native,animation_preservation=animation,map_checks=maps,source_snapshot_verified=True,portable_animation_poses_verified=read(W/'source_animation_check.json'),tested_platforms=[],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),remaining_work=['User in-game visual and material review','Folding mechanism review in all three test modes','AI gameplay, damage, distance transitions and other platforms','Custom emissives deferred'])
write(A/'validation.json',v)
write(A/'release.json',dict(package_name='openreliant-loki',version='0.1.0-beta.1',asset_revision='1.0',status='hold',hold_reason='Awaiting in-game review and user approval.',minimum_openreliant='0.7.0',mod_folders=[MOD],asset_manifest_sha256=v['asset_manifest_sha256'],source_manifest_sha256=v['source_manifest_sha256'],channel='beta',user_approved=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json']+[str(p.relative_to(A)) for p in sorted((A/'tools').glob('*.sh'))]))
target=G/'game-data/mods'/MOD;assert not target.exists(),'Reconcile existing deployment before overwrite';target.mkdir()
for rec in assets:
 p=A/rec['path'];shutil.copy2(p,target/p.name);assert sha(target/p.name)==rec['sha256']
assert {p.name for p in target.iterdir()}=={Path(x['path']).name for x in assets}
for p in (A/'tools').glob('*.sh'):
 dest=G/p.name;assert not dest.exists();shutil.copy2(p,dest);dest.chmod(0o755);assert sha(dest)==sha(p)
deploy=dict(date_utc=now,repository=str(A),deployed_folder=str(target),files=len(assets),all_files_match=True,asset_manifest_sha256=v['asset_manifest_sha256'],launcher=str(G/'launch-loki-test.sh'),launcher_sha256=sha(G/'launch-loki-test.sh'),user_review='pending');write(W/'deployment.json',deploy)
state=read(D.parent/'project_state.json');state.update(latest_scene=r['scene'],latest_pass='reconstruction_v1',asset_revision='1.0',status='first_worn_pass_ready_for_in_game_review',maps=r['maps'],progress=dict(texture_uv='first_pass_complete_review_pending',pbr_authoring='complete',pbr_tuning='Blender_checked_user_game_review_pending',engine_validation='native_format_passed_runtime_pending'),engine_build=v['target_engine'],engine_sha256=v['target_engine_sha256'],runtime_visual_review='pending_user_review',runtime_animation_review='pending_user_review',user_approved=False,published=False,emissives='deferred',repository_snapshot=snap['snapshot'],deployment=deploy,launcher=deploy['launcher'],remaining_work=v['remaining_work'],updated_at_utc=now);write(D.parent/'project_state.json',state);write(D/'manifest.json',state)
(D/'README.md').write_text((A/'README.md').read_text()+'\nCanonical scene: `loki_worn_pbr_v1.blend`. PBR release gate satisfied by installed official OpenReliant 0.7.0. Texture/UV and PBR authoring first pass complete; in-game tuning and validation remain pending. Launcher: `$OPENRELIANT_HOME/launch-loki-test.sh`.\n')
print(json.dumps(deploy,indent=2))
