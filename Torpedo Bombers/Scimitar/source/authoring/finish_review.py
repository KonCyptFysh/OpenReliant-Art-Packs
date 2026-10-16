from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
from PIL import Image
D=Path('${SCIMITAR_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_8_v1/mods/115-scimitar-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Torpedo Bombers/Scimitar';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.18.0-linux-x86_64'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,r):write(p,json.dumps(r,indent=2)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
checks=read(W/'native_checks.json');maps=read(W/'map_checks.json');pres=read(W/'native_preservation.json');snap=read(W/'repository_snapshot.json')
assert maps['passed'] and pres['passed'] and snap['packed_relative_resources_reopened']
assert all(x['exit_code']==0 for x in checks)
assert sum(x['faces'] for x in pres['detail_meshes'])==476
assert sorted(p.name for p in O.glob('*.png'))==['mod.png','orsc1_hull.png','orsc1_hull_normal.png','orsc1_hull_orm.png']
latest=[]
for kind,file in [('shp','Scimitar.SHP'),('dte','mission963.dte'),('dte','mission964.dte')]:
 p=subprocess.run([str(E/'sltool'),kind,'check',str(O/file)],capture_output=True,text=True,check=True);latest.append(dict(file=file,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(O/file)))
probe=R/'.local/texture-variant-cleanup/texture-probe'
p=subprocess.run([str(probe),str(O),'orsc1_hull'],capture_output=True,text=True,check=True)
assert 'PASS orsc1_hull' in p.stdout+p.stderr
write(W/'texture-loader-probe.log',p.stdout+p.stderr)
compat=dict(status='passed',scope='Non-visual native-format and texture-loader checks',checked_at_utc=now,minimum_engine='0.8.1',review_engine='Official OpenReliant 0.18.0',review_engine_sha256=sha(E/'openreliant'),native_checks_0_8_1=checks,native_checks_0_18_0=latest,texture_loader=dict(version='0.8.1 baseline',probe_binary_sha256=sha(probe),output=p.stdout+p.stderr),duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility.json',compat)
parts=read(D/'source/native_parts.json');assert len(parts)==1
assert len([a for a in parts[0]['attachments'] if a['kind']==8])==2
assert not any(t['name']=='deploy' for t in parts[0]['tracks'])
keys=parts[0]['tracks'][0]['keys'];assert keys[0]['angles']==keys[1]['angles'] and keys[0]['offset']==keys[1]['offset']
modeltext=(W/'engine-models-v0.18.zig').read_text();assert modeltext.lower().count('scimitar.shp')==1
dump(W/'model_mapping_audit.json',dict(engine='Official OpenReliant 0.18.0',ship_type=48,model='scimitar.shp',distinct_model_entries=1,conclusion='One shared player/AI model entry. Two fixed native launch mounts. No deploy animation; the unnamed clip has identical transforms.',source_sha256=sha(W/'engine-models-v0.18.zig')))
dump(W/'deployment_mechanism.json',dict(native_parts=1,native_launch_mounts=2,launch_mounts_preserved=True,deployment_motion=False,carried_ship_type=92,carried_ship_count=2,review_modes={'964':'carried/stowed','963':'timed two-torpedo release'},runtime_gameplay_verified=False))
for view in ['front','opposite','rear','belly']:
 with Image.open(D/'review/reconstruction_v1'/f'material_{view}.png') as im:im.load();assert im.size==(1440,1080)
dump(W/'authoring_review.json',dict(kind='Blender authoring views; not in-game captures',reviewed_at_utc=now,views=['front','opposite','rear','belly'],observations=['Original upright silhouette, grey/brown armour, red accents and warning markings preserved.','Six atlas glass regions have smooth amber interiors and separately authored frame and inset relief.','Both sides and underside inspected. Native vertex, UV and normal coordinates preserved.'],runtime_visual_review='pending_user'))
shutil.copy2(__file__,W/'finish_review.py')
shutil.copytree(D/'source',A/'source/originals',dirs_exist_ok=True)
for f in ['source/maps','source/authoring','source/review/reconstruction_v1','tools']:(A/f).mkdir(parents=True,exist_ok=True)
for p in (D/'maps').glob('*.png'):shutil.copy2(p,A/'source/maps'/p.name)
for p in W.iterdir():
 if p.is_file() and p.suffix in ('.py','.json','.txt','.luau','.log'):
  s=p.read_text()
  for x,y in [(str(D),'${SCIMITAR_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(G),'${OPENRELIANT_HOME}')]:s=s.replace(x,y)
  write(A/'source/authoring'/p.name,s)
for p in (D/'review/reconstruction_v1').glob('*.png'):shutil.copy2(p,A/'source/review/reconstruction_v1'/p.name)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
launchers=[]
for p in sorted(O.parent.parent.glob('launch-scimitar-*.sh')):
 q=A/'tools'/p.name;shutil.copy2(p,q);q.chmod(0o755);subprocess.run(['bash','-n',str(q)],check=True);launchers.append(q)
assert len(launchers)==2
write(A/'README.md',f'''# Scimitar - Worn Paint

**First pass installed for review. Not approved or published.** Artwork revision 1.0; planned beta 0.1.0-beta.1. Native pack baseline 0.8.1; local review launchers use official OpenReliant 0.18.0.

Restores the worn grey and brown alloy, red accents, caution markings and machinery. Includes smooth inset amber glazing, independent frame relief and restrained structural normal, roughness and metallic maps. One canonical unprefixed PNG material set supports engine-generated loadout colours.

Original geometry, UV coordinates, normals, attachments and the static animation clip are preserved. The 476 native triangles were audited; {len(pres['continuation_corrections'])} primitive continuation counts were corrected at incompatible UV joins. One shared model serves player and AI uses. Scimitar has two fixed torpedo mounts and no moving deployment mechanism.

Native-format checks pass on official 0.8.1 and 0.18.0. Map, loadout-colour and portable-source checks pass. Both sides, rear and belly were inspected in Blender. In-game appearance and timed torpedo release await user review.
''')
write(A/'INSTALL.md','''# Installation and review

Copy `mods/115-scimitar-worn-v1` into OpenReliant's `game-data/mods`. Requires your own StarLancer data. The native pack supports 0.8.1; these local review launchers use the newly installed official 0.18.0.

Keep both launcher scripts beside `launch-openreliant.sh`, or set OPENRELIANT_HOME to the installation.

- `launch-scimitar-test.sh`: quiet stationary ship with two carried Coalition torpedoes, mission 964.
- `launch-scimitar-launch-test.sh`: timed release, mission 963; first torpedo after about nine seconds, second roughly seven seconds later.

No moving deploy/stow geometry exists on this model. The two native launch points are preserved. The review uses native StartLaunch commands rather than new player controls. Ship type 48, torpedo type 92.

Press 7 for orbit; arrows rotate; Shift+Up/Down zoom; 0 saves a screenshot. No enemies, invulnerable ship, sound off. Close any running game before starting another. Disable or remove this mod to restore the original Scimitar.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- In-game appearance and timed torpedo release await user review; no automatic gameplay captures were run.
- Full campaign, damage, ejection, distance transitions and other platforms are untested.
- Dedicated emissive maps remain deferred; native effects are retained.
- Delivery maps are 4096 square, resampled from a 1254-square reconstruction of the original 256-square atlas.
- Source renders are authoring evidence. Publication will require fresh standard official-engine gallery photography.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.0

First worn Scimitar restoration, recessed amber glass, structural maps and canonical PNG export. Native geometry, UVs and two fixed launch mounts preserved. Two quiet inspection missions supplied. Awaiting user review.
''')
write(A/'CREDITS.md','''# Credits

Restoration contributions by KonCyptFysh. Original StarLancer assets retain their respective ownership. OpenReliant supplies the engine and native tools.

Atlas reconstructed with the built-in image-generation tool from the original SCIMITAR atlas, with a focused glazing cleanup. Both prompts, original outputs and hashes are preserved in source/authoring/imagegen_prompts.json. Material masks were authored separately.
''')
write(A/'LICENSING.md',"# Licensing\n\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . Original StarLancer assets retain their respective ownership and rights. Requires your own StarLancer data.\n")
write(A/'source/README.md','''# Scimitar editable source

`scimitar_worn_pbr_v1.blend` is the current first-pass scene: one native mesh, 476 triangles, original normals and UVs. Images are packed and have verified relative resource paths. The saved source was reopened and compared.

`originals/` preserves the native model and atlas. `maps/` includes reconstruction history, delivery maps and structural masks. `authoring/` contains first-pass recipes, prompts and checks. These scripts document authoring history rather than offering a one-command portable rebuild; records use local environment placeholders. Start further refinements from the current scene, preserving manual changes. `review/` contains Blender authoring views, not game photography.
''')
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()]
dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='first-pass-awaiting-user-review',ship='Scimitar',asset_revision='1.0',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
dump(A/'compatibility-0.8.json',compat)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,review_engine='0.18.0',minimum_openreliant='0.8.1',asset_revision='1.0',user_approved=False,packaging_ready=False,game_launched=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),checks=['Native SHP and two DTE round trips on 0.8.1 and 0.18.0','476 faces audited; original geometry, UVs, normals and launch mounts retained','Normalized normals; flat glass interiors with zero metallic; correct ORM packing','Engine-generated loadout variants inherit material maps','Packed portable scene reopened and compared','Both sides, rear and belly inspected in Blender','Two shell launchers verified'],runtime_visual_review='pending_user')
dump(A/'validation.json',validation)
dump(A/'release.json',dict(package_name='openreliant-scimitar',version='0.1.0-beta.1',asset_revision='1.0',status='held',hold_reason='Awaiting user appearance and torpedo-release review',minimum_openreliant='0.8.1',mod_folders=[O.name],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),channel='beta',user_approved=False,published=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json','compatibility-0.8.json']+[str(p.relative_to(A)) for p in launchers]))
category=R/'Torpedo Bombers/README.md';s=category.read_text().replace('| [Scimitar](Scimitar/README.md) | Planned; artwork not started | Coming soon |','| [Scimitar](Scimitar/README.md) | Worn first pass installed; awaiting in-game review | Unreleased |').replace('Scimitar remains planned.','Scimitar is installed for first-pass review.');category.write_text(s)
catalog=read(R/'catalog.json');entry=next(x for x in catalog['assets'] if x['id']=='scimitar');entry.update(workStatus='in-progress',description='Worn grey and brown Coalition torpedo bomber with recessed amber glazing and two preserved native launch mounts. First pass awaiting in-game review.')
entry['liveries'][0].update(engine='0.8.1',engineStatus='non-visual-checks-passed-review-pending',notes=['First pass installed for review on official OpenReliant 0.18.0; no published download.','Two fixed torpedo launch mounts preserved; no deployment animation on the original model.'])
dump(R/'catalog.json',catalog)
installed=G/'game-data/mods'/O.name;assert not installed.exists()
for p in launchers:assert not (G/p.name).exists()
names={x.name.lower() for x in O.iterdir() if x.suffix.lower() in ['.shp','.dte']}
assert not [p for p in (G/'game-data/mods').rglob('*') if p.is_file() and p.name.lower() in names]
closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
with tempfile.TemporaryDirectory(prefix='.scimitar-install-',dir=G) as staging:
 staged=Path(staging)/O.name;shutil.copytree(A/'mods'/O.name,staged)
 for r in manifest:assert sha(staged/Path(r['path']).name)==r['sha256']
 os.rename(staged,installed)
for p in launchers:shutil.copy2(p,G/p.name);(G/p.name).chmod(0o755)
for r in manifest:assert sha(A/r['path'])==sha(installed/Path(r['path']).name)==r['sha256']
dump(W/'deployment.json',dict(status='installed-ready-for-user-review',installed_at_utc=now,repository_asset=str(A),installed_mod=str(installed),launchers=[rec(G/p.name,G) for p in launchers],runtime_files=manifest,exact_repository_bytes_verified=True,game_was_closed=closed,game_launched=False,runtime_visual_review='pending_user'))
state=read(D.parent/'project_state.json');state.update(status='ready_for_user_review',latest_scene=str(D/'scimitar_worn_pbr_v1.blend'),upright_scene=str(D/'scimitar_worn_pbr_v1.blend'),latest_deliverables=str(O.parent.parent),repository_asset=str(A),review_launcher=str(G/'launch-scimitar-test.sh'),updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='first_pass_complete_pending_review',pbr_authoring='complete_structural_maps_and_inset_amber_glass',pbr_tuning='authoring_preview_checked_runtime_pending',engine_validation='0_8_1_and_0_18_0_non_visual_checks_passed'),engine_validation=dict(build='Official OpenReliant 0.18.0',minimum='0.8.1',non_visual_checks='passed',visual_review='pending_user',game_launched=False,evidence=str(W/'compatibility.json')),current_manifest=str(D/'manifest.json'))
dump(D.parent/'project_state.json',state)
dump(D/'manifest.json',dict(ship='Scimitar',variant='worn',status='ready_for_user_review',user_approved=False,published=False,scene=rec(D/'scimitar_worn_pbr_v1.blend',D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],runtime_exports=manifest,maps=read(W/'validation.json')['maps'],remaining=['User in-game appearance and torpedo-release review','Full campaign and combat testing','Dedicated emissive maps','Fresh standard gallery photos when approved for publication']))
write(D/'README.md',f'''# Scimitar worn workspace

First pass installed for user review, not approved or published. Current scene: scimitar_worn_pbr_v1.blend. Worn grey/brown armour, red accents and original markings preserved. Recessed amber glazing and structural normal, metallic and roughness maps included. Native geometry, UVs, normals and two fixed launch mounts preserved. No deployment animation exists in the original model.

Native format checks pass on official 0.8.1 and 0.18.0, with map, loadout-colour, portable-source and installed-hash checks. Both sides, belly and rear inspected in Blender. In-game review is pending; no automatic gameplay captures were run.

Use {G}/launch-scimitar-test.sh for carried torpedoes, or launch-scimitar-launch-test.sh for timed release. Both use the newly installed official 0.18.0. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, 0 for screenshots.

Originals, both built-in image-generation prompts and output history, semantic masks, validation and editable sources are retained. Delivery maps are 4K, resampled from the 1254-square reconstruction. See manifest.json and ../project_state.json for exact status.
''')
write(O.parent.parent/'README.md','# Scimitar review export\n\nExact repository runtime installed. Canonical base/normal/ORM PNG set, no redundant colour variants. Native compatibility baseline 0.8.1, current review launchers 0.18.0. Carried and timed-launch modes supplied. User review pending.\n')
print(json.dumps(dict(status=state['status'],launcher=state['review_launcher'],runtime_files=len(manifest),runtime_bytes=sum(r['bytes'] for r in manifest),continuation_corrections=len(pres['continuation_corrections']),game_was_closed=closed),indent=2))
