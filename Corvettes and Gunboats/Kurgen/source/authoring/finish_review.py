from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
from PIL import Image
D=Path('${KURGEN_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_8_v1/mods/116-kurgen-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Corvettes and Gunboats/Kurgen';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.18.0-linux-x86_64'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,r):write(p,json.dumps(r,indent=2,ensure_ascii=False)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
checks=read(W/'native_checks.json');maps=read(W/'map_checks.json');pres=read(W/'native_preservation.json');snap=read(W/'repository_snapshot.json')
assert maps['passed'] and pres['passed'] and snap['packed_relative_resources_reopened'];assert all(x['exit_code']==0 for x in checks)
assert sum(x['faces'] for p in pres['files'] for x in p['detail_meshes'])==1548
assert sorted(p.name for p in O.glob('*.png'))==['mod.png','orku1_hull.png','orku1_hull_normal.png','orku1_hull_orm.png','orku1_turret.png','orku1_turret_normal.png','orku1_turret_orm.png']
probe=R/'.local/texture-variant-cleanup/texture-probe';outputs=[]
for stem in ['orku1_hull','orku1_turret']:
 p=subprocess.run([str(probe),str(O),stem],capture_output=True,text=True,check=True);assert 'PASS '+stem in p.stdout+p.stderr;outputs.append(p.stdout+p.stderr)
write(W/'texture-loader-probe.log','\n'.join(outputs))
compat=dict(status='passed',scope='Non-visual native-format and texture-loader checks',checked_at_utc=now,minimum_engine='0.8.1',review_engine='Official OpenReliant 0.18.0',review_engine_sha256=sha(E/'openreliant'),native_checks=checks,texture_loader=dict(version='0.8.1 baseline',probe_binary_sha256=sha(probe),output=outputs),duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility.json',compat)
parts=read(D/'source/native_parts.json');turret=read(D/'source/turret_parts.json')
assert len(parts)==2 and len(turret)==4 and len([a for a in parts[0]['attachments'] if a['kind']==1])==3
assert all(not t['keys'] for p in parts for t in p['tracks'])
dump(W/'model_mapping_audit.json',dict(ship_type=60,model='Rus_Kurgan.SHP',hull_parts=2,detail_levels=6,gun_mounts=3,shared_turret='10_Rus_STUR.SHP',shared_turret_parts=4,hull_animation='No moving hull clips',turret_animation='Original native aiming and barrel fire/recoil tracks preserved',scope='The Coalition small-turret model is shared. Its visual restoration also applies wherever that same model is mounted. No weapon stats or attachment IDs changed.',wreck='Original DAM_1 texture and wreck geometry preserved. Separate Rus_Kurgan_dest.SHP is not overridden.'))
for view in ['front','opposite','rear','belly']:
 with Image.open(D/'review/reconstruction_v1'/f'material_{view}.png') as im:im.load();assert im.size==(1440,1080)
dump(W/'authoring_review.json',dict(kind='Blender authoring views; not in-game captures',reviewed_at_utc=now,views=['front','opposite','rear','belly'],observations=['Upright worn grey gunboat, red stars, caution paint and machinery preserved.','Three native small-turret instances included in authoring inspection.','Structural surface relief independent of painted artwork.','Both sides, rear and belly inspected; runtime appearance remains pending.'],runtime_visual_review='pending_user'))
if Path(__file__).resolve()!=(W/'finish_review.py').resolve():shutil.copy2(__file__,W/'finish_review.py')
shutil.copytree(D/'source',A/'source/originals',dirs_exist_ok=True)
for f in ['source/maps','source/authoring','source/review/reconstruction_v1','tools']:(A/f).mkdir(parents=True,exist_ok=True)
for p in (D/'maps').glob('*.png'):shutil.copy2(p,A/'source/maps'/p.name)
for p in W.iterdir():
 if p.is_file() and p.suffix in ('.py','.json','.txt','.luau','.log'):
  s=p.read_text()
  for x,y in [(str(D),'${KURGEN_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(G),'${OPENRELIANT_HOME}'),('${ART_SOURCE_ROOT}','${ART_SOURCE_ROOT}'),('${IMAGEGEN_ARCHIVE}','${IMAGEGEN_ARCHIVE}')]:s=s.replace(x,y)
  write(A/'source/authoring'/p.name,s)
for p in (D/'review/reconstruction_v1').glob('*.png'):shutil.copy2(p,A/'source/review/reconstruction_v1'/p.name)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
launcher=A/'tools/launch-kurgen-test.sh';shutil.copy2(O.parent.parent/'launch-kurgen-test.sh',launcher);launcher.chmod(0o755);subprocess.run(['bash','-n',str(launcher)],check=True)
joins=sum(len(p['continuation_corrections']) for p in pres['files'])
write(A/'README.md',f'''# Kurgen - Worn Paint

**First pass installed for review. Not approved or published.** Artwork revision 1.0; planned beta 0.1.0-beta.1. Native pack baseline 0.8.1; local review uses official OpenReliant 0.18.0.

Restores the worn grey Kurgen hull and its three Coalition small gun turrets: red stars, caution paint, panel seams, vent ribs and machinery, with restrained structural normal, roughness and metallic maps. Two canonical unprefixed PNG material sets, without generated green/red duplicates.

Original geometry, UVs, normals, collision, attachments, aiming and recoil tracks are retained across all six levels of detail. All 1,548 stored faces were audited; {joins} primitive continuation counts were corrected at incompatible UV joins. There is no animated hull deployment mechanism. The native damaged parts and original shared DAM_1 artwork are retained.

The small turret is the shared `10_Rus_STUR.SHP` model. Its visual upgrade also appears on other ships using that exact component; gun statistics, firing arcs and attachment IDs are unchanged. The larger Coalition turret is not replaced.

Native checks pass on official 0.8.1 and 0.18.0. Both sides, rear and belly inspected in Blender. In-game visual review is pending.
''')
write(A/'INSTALL.md','''# Installation and review

Copy `mods/116-kurgen-worn-v1` into OpenReliant's `game-data/mods`. Requires your own StarLancer data. Native pack baseline: 0.8.1. The review launcher uses official 0.18.0.

Place `tools/launch-kurgen-test.sh` beside `launch-openreliant.sh`, or set OPENRELIANT_HOME to the installation. It opens mission 962: a quiet, invulnerable, stationary Kurgen with all three native gun mounts. No combat or new gameplay mechanics.

Press 7 for orbit; arrows rotate; Shift+Up/Down zoom; 0 saves a screenshot. Close any running game before starting another.

This pack replaces the Kurgen hull and shared Coalition small turret. Disable or remove the pack to restore both originals.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- In-game appearance awaits user review; automatic gameplay photography was not run.
- Full campaign, damage, turret tracking/firing, distance transitions and other platforms need gameplay checks. Native records and six detail levels are retained and structurally validated.
- The small turret is a shared component, so its restoration also appears wherever that same model is mounted.
- Wreck artwork is the original shared DAM_1; no global damage-texture replacement is included.
- Dedicated emissive maps remain deferred; native effects are retained.
- Delivery maps are 4096 square, resampled from 1254-square reconstructions of the original 256-square hull and 128-square turret atlases.
- Source renders are authoring evidence. Publication requires fresh standard official-engine gallery photography after approval.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.0

First worn Kurgen hull and small-turret restoration, structural surface maps and six-level native seam audit. Native mesh, UVs, mounts, wreck data and recoil tracks retained. Quiet inspection mission supplied; user review pending.
''')
write(A/'CREDITS.md','''# Credits

Restoration contributions by KonCyptFysh. Original StarLancer assets retain their respective ownership. OpenReliant supplies the engine and native tools.

Hull and turret atlases reconstructed with built-in image generation from their original textures. The exact two prompts, outputs and hashes are retained in source/authoring/imagegen_prompts.json. Structural material masks authored separately.
''')
write(A/'LICENSING.md',"# Licensing\n\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . Original StarLancer assets retain their respective ownership and rights. Requires your own StarLancer data.\n")
write(A/'source/README.md','''# Kurgen editable source

Start future edits from `kurgen_worn_pbr_v1.blend`. Native hull and damage mesh are preserved, with three mounted turret instances for authoring review. Runtime exports retain independent native mounted models, turret hierarchy, all detail levels and animation. The damaged hull part is hidden in the intact authoring view.

Packed images and relative resource paths were verified by reopening the saved scene. `originals/` preserves SHP models, atlas images and decoded native records. `maps/` holds generated reconstructions, delivery maps and masks. `authoring/` retains exact prompts, recipes and validation records; these document the work rather than providing a one-command portable rebuild. `review/` contains Blender inspection images, not public gallery photos.
''')
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()]
dump(A/'asset-manifest.json',manifest);dump(A/'source-manifest.json',dict(status='first-pass-awaiting-user-review',ship='Kurgen',asset_revision='1.0',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
dump(A/'compatibility-0.8.json',compat)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,review_engine='0.18.0',minimum_openreliant='0.8.1',asset_revision='1.0',user_approved=False,packaging_ready=False,game_launched=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),checks=['Two native models and quiet mission on 0.8.1 and 0.18.0','1548 faces across all detail levels audited; original mesh, UVs, normals, attachments and animations preserved','Normalized structural normals; painted graphics flat; ORM channels verified','Unprefixed material sets pass engine texture-loader probe','Packed source reopened and compared','Both sides, rear and belly inspected in Blender'],runtime_visual_review='pending_user')
dump(A/'validation.json',validation)
dump(A/'release.json',dict(package_name='openreliant-kurgen',version='0.1.0-beta.1',asset_revision='1.0',status='held',hold_reason='Awaiting user in-game review',minimum_openreliant='0.8.1',mod_folders=[O.name],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),channel='beta',user_approved=False,published=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json','compatibility-0.8.json','tools/launch-kurgen-test.sh']))
write(A.parent/'README.md','# Corvettes and Gunboats\n\n| Ship | Artwork | Download |\n|---|---|---|\n| Prowler | Planned | Coming soon |\n| [Kurgen](Kurgen/README.md) | Worn first pass installed; awaiting in-game review | Unreleased |\n')
catalog=read(R/'catalog.json');cat=next(x for x in catalog['categories'] if x['id']=='corvettes-and-gunboats');cat['folder']='Corvettes and Gunboats';entry=next(x for x in catalog['assets'] if x['id']=='kurgen');entry.update(folder='Corvettes and Gunboats/Kurgen',workStatus='in-progress',description='Worn Coalition gunboat restoration with red stars, structural materials and three restored small turrets. First pass awaiting in-game review.')
entry['liveries'][0].update(engine='0.8.1',engineStatus='non-visual-checks-passed-review-pending',notes=['First pass installed for review on official OpenReliant 0.18.0; no published download.','Three native gun mounts and six detail levels preserved. Shared small-turret artwork is included.'])
dump(R/'catalog.json',catalog)
installed=G/'game-data/mods'/O.name;assert not installed.exists();assert not (G/launcher.name).exists()
names={x.name.lower() for x in O.iterdir() if x.suffix.lower() in ['.shp','.dte']};conflicts=[str(p) for p in (G/'game-data/mods').rglob('*') if p.is_file() and p.name.lower() in names];assert not conflicts,conflicts
closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
with tempfile.TemporaryDirectory(prefix='.kurgen-install-',dir=G) as staging:
 staged=Path(staging)/O.name;shutil.copytree(A/'mods'/O.name,staged)
 for rec_ in manifest:assert sha(staged/Path(rec_['path']).name)==rec_['sha256']
 os.rename(staged,installed)
shutil.copy2(launcher,G/launcher.name);(G/launcher.name).chmod(0o755)
for rec_ in manifest:assert sha(A/rec_['path'])==sha(installed/Path(rec_['path']).name)==rec_['sha256']
dump(W/'deployment.json',dict(status='installed-ready-for-user-review',installed_at_utc=now,repository_asset=str(A),installed_mod=str(installed),launcher=rec(G/launcher.name,G),runtime_files=manifest,exact_repository_bytes_verified=True,game_was_closed=closed,game_launched=False,runtime_visual_review='pending_user'))
state=read(D.parent/'project_state.json');state['originals']=[rec(p,D) for p in sorted((D/'source').iterdir()) if p.suffix in ['.SHP','.png']];state.update(status='ready_for_user_review',latest_scene=str(D/'kurgen_worn_pbr_v1.blend'),upright_scene=str(D/'kurgen_worn_pbr_v1.blend'),latest_deliverables=str(O.parent.parent),repository_asset=str(A),review_launcher=str(G/launcher.name),updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='first_pass_complete_pending_review',pbr_authoring='complete_structural_maps_for_hull_and_turret',pbr_tuning='authoring_preview_checked_runtime_pending',engine_validation='0_8_1_and_0_18_0_non_visual_checks_passed'),engine_validation=dict(build='Official OpenReliant 0.18.0',minimum='0.8.1',non_visual_checks='passed',visual_review='pending_user',game_launched=False,evidence=str(W/'compatibility.json')),current_manifest=str(D/'manifest.json'),shared_component_scope='10_Rus_STUR.SHP small turret upgrade applies wherever used')
dump(D.parent/'project_state.json',state)
dump(D/'manifest.json',dict(ship='Kurgen',variant='worn',status='ready_for_user_review',user_approved=False,published=False,scene=rec(D/'kurgen_worn_pbr_v1.blend',D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],runtime_exports=manifest,maps=read(W/'validation.json')['maps'],remaining=['User in-game review','Campaign, turret tracking/firing, damage and distance transition testing','Dedicated emissive maps','Standard gallery photos after publication approval']))
write(D/'README.md',f'''# Kurgen worn workspace

First pass installed for user review, not approved or published. Current scene: kurgen_worn_pbr_v1.blend. Worn grey armour, red stars, caution paint and native machinery restored, with structural normal, metallic and roughness maps. Original mesh, UVs, normals, all six detail levels, mounts and animations retained. Shared Coalition small-turret artwork is included; this also improves other ships using that exact model. Original damage texture retained.

Native checks passed on official 0.8.1 and 0.18.0, alongside map, texture-loader, portable-source and installed-hash checks. Both sides, belly and rear inspected in Blender. In-game review is pending.

Run {G}/launch-kurgen-test.sh for the quiet review scene. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, 0 for screenshots.

Both built-in image-generation prompts and original outputs, source models/textures and structural masks are retained. The 4K delivery maps are resampled from 1254-square reconstructed atlases. See manifest.json and ../project_state.json for status and evidence.
''')
write(O.parent.parent/'README.md','# Kurgen review export\n\nExact repository runtime installed. Two canonical PNG material sets for hull and small turret, no redundant colour variants. Native baseline 0.8.1; review launcher 0.18.0. User appearance review pending.\n')
print(json.dumps(dict(status=state['status'],launcher=state['review_launcher'],runtime_files=len(manifest),runtime_bytes=sum(r['bytes'] for r in manifest),continuation_corrections=joins,game_was_closed=closed),indent=2))
