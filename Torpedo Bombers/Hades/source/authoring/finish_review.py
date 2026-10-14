import os
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, tempfile
from PIL import Image
D=Path(os.environ['HADES_WORKSPACE'])
W=D/'work/reconstruction_v1'; O=D/'exports/openreliant_0_8_v1/mods/114-hades-worn-v1'
R=Path('${ART_PACK_REPOSITORY}')
A=R/'Torpedo Bombers/Hades'; G=Path('${OPENRELIANT_HOME}'); E=G/'releases/openreliant-v0.8.1-linux-x86_64'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,r): write(p,json.dumps(r,indent=2,ensure_ascii=False)+'\n')
def record(p,root): return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
def read(p): return json.loads(p.read_text())
def sanitize(s):
 for x,y in [(str(D),'${HADES_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(E/'sltool'),'${OPENRELIANT_SLTOOL}'),(str(G),'${OPENRELIANT_HOME}'),('${STARLANCER_ASSETS}','${STARLANCER_ASSETS}')]:s=s.replace(x,y)
 return s
checks=read(W/'native_checks.json');maps=read(W/'map_checks.json');pres=read(W/'native_preservation.json');snapshot=read(W/'repository_snapshot.json')
assert all(x['exit_code']==0 for x in checks) and maps['passed'] and pres['passed'] and snapshot['packed_relative_resources_reopened']
assert len(pres['continuation_corrections'])==43 and sum(x['faces'] for x in pres['detail_meshes'])==881
assert sorted(p.name for p in O.glob('*.png'))==['mod.png','orhd1_hull.png','orhd1_hull_normal.png','orhd1_hull_orm.png']
assert sha(E/'openreliant')=='aa5e81293be85b28884460476427d0942556d6945b3e89da390365d480d9c5ea'
probe=R/'.local/texture-variant-cleanup/texture-probe'; probe_src=R/'tools/loadout-texture-probe/texture-probe.zig'
assert sha(probe)=='b95e2d5089555231c6db847452ead080772a076a43b79ec504841a05462cb1fb'
compat=dict(status='passed',scope='Non-visual native format and texture-loader checks',checked_at_utc=now,engine='Official OpenReliant 0.8.1 linux-x86_64',engine_sha256=sha(E/'openreliant'),native_checks=checks,texture_loader=dict(probe_source_sha256=sha(probe_src),probe_binary_sha256=sha(probe),output='PASS orhd1_hull: base, green, red; normal and ORM inherited byte-for-byte; generated colour channels verified',input_files=[record(O/f'orhd1_hull{x}.png',O) for x in ('','_normal','_orm')]),duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility-0.8.json',compat)
parts=read(D/'source/native_parts.json')
arms=[p for p in parts if any(t['name']=='deploy' for t in p['tracks'])]
assert len(arms)==4 and all(len([a for a in p['attachments'] if a['kind']==8])==1 for p in arms)
dump(W/'deployment_mechanism.json',dict(native_file='USTB_Hds.SHP',ship_type=26,native_parts=6,deploy_parts=[p['name'] for p in arms],animation_length=400,launch_mounts=[dict(part=p['name'],attachment=[a for a in p['attachments'] if a['kind']==8][0]) for p in arms],carried_ship_type=74,carried_ship_count=4,review_modes={'968':'stowed','967':'deployed','966':'cycle','965':'timed four-torpedo release'},animation_and_attachments_byte_identical=True,gameplay_verified=False))
model_source=R.parents[1]/'upstream/src/engine/game/create/models.zig'
assert model_source.is_file() and model_source.read_text().lower().count('ustb_hds.shp')==1
dump(W/'model_mapping_audit.json',dict(inspected_source=str(model_source),sha256=sha(model_source),entry='0x1A / type 26: ustb_hds.shp',distinct_hades_model_entries=1,conclusion='One shared native model identified; no separate player or AI model entry.',original_model_sha256=sha(D/'source/USTB_Hds.SHP')))
for v in ['front','opposite','rear','belly']:
 with Image.open(D/'review/reconstruction_v1'/f'material_{v}.png') as im: im.load();assert im.size==(1440,1080)
dump(W/'authoring_review.json',dict(reviewed_at_utc=now,kind='Blender static authoring views; not gameplay',views=[record(D/'review/reconstruction_v1'/f'material_{v}.png',D) for v in ['front','opposite','rear','belly']],observations=['Original upright silhouette, brown/green/grey livery and US markings retained.','Both sides, rear and underside inspected.','Original UV coordinates preserved; no collapsed visible faces.','Glass interiors have flat normals and a separate recessed height profile; preview highlights come from studio lights.'],runtime_visual_review='pending_user'))
shutil.copy2(__file__,W/'finish_review.py')
shutil.copytree(D/'source',A/'source/originals',dirs_exist_ok=True)
for folder in ['source/maps','source/authoring','source/review/reconstruction_v1','tools']:(A/folder).mkdir(parents=True,exist_ok=True)
for p in (D/'maps').glob('*.png'):shutil.copy2(p,A/'source/maps'/p.name)
for p in W.iterdir():
 if p.is_file() and p.suffix in ('.py','.json','.txt'):
  s=sanitize(p.read_text())
  if p.suffix=='.py':
   if "Path(os.environ['HADES_WORKSPACE'])" in s:s='import os\n'+s.replace("Path(os.environ['HADES_WORKSPACE'])","Path(os.environ['HADES_WORKSPACE'])")
   s=s.replace("tool=os.environ['OPENRELIANT_SLTOOL']","tool=os.environ['OPENRELIANT_SLTOOL']")
  write(A/'source/authoring'/p.name,s)
for p in (D/'review/reconstruction_v1').glob('*.png'):shutil.copy2(p,A/'source/review/reconstruction_v1'/p.name)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
launchers=[]
for p in sorted(O.parent.parent.glob('launch-hades-*.sh')):
 q=A/'tools'/p.name;shutil.copy2(p,q);q.chmod(0o755);subprocess.run(['bash','-n',str(q)],check=True);launchers.append(q)
assert len(launchers)==4
write(A/'README.md','''# Hades - Worn Paint

**First pass installed for user review. Not approved or published.** Targets official OpenReliant 0.8.1, planned package 0.1.0-beta.1, artwork revision 1.0.

Restores Hades' worn bronze-brown, grey and green armour, US insignia, caution markings, vents and mechanical recesses. Recessed dark green glazing, separate frame relief and restrained structural normal, roughness and metallic maps are included. A single unprefixed PNG material set serves the ship and engine-generated loadout colours.

The six-part native model has four sliding torpedo arms, each with its original launch mount. Original geometry, UVs, normals, attachments and animation bytes are preserved. All 881 faces across the native detail meshes were audited; 43 primitive continuation counts were corrected where adjacent faces require distinct UVs. The engine mapping contains one Hades model shared by player and AI uses.

Quiet review modes provide stowed, deployed, continuously cycling and timed four-torpedo release states. Format, material-map, texture-loader, portable-source and installed-file checks passed. Both sides, rear and underside were inspected in Blender. In-game appearance and animation still await user review; see INSTALL.md.
''')
write(A/'INSTALL.md','''# Installation and review

Copy `mods/114-hades-worn-v1` to OpenReliant's `game-data/mods`. Requires your own StarLancer data and official OpenReliant 0.8.1. This folder is already installed in the local review setup.

Keep the four launcher scripts together beside `launch-openreliant.sh`, or set OPENRELIANT_HOME to your installation. `launch-hades-test.sh` defaults to the cycle mode; it also accepts `stowed`, `deployed`, `cycle` or `launch`, followed by optional engine arguments.

| Launcher | Scene |
| --- | --- |
| launch-hades-test.sh | Start stowed, then repeatedly deploy and retract the four arms |
| launch-hades-stowed-test.sh | Hold stowed with four carried torpedoes |
| launch-hades-deployed-test.sh | Deploy and hold; allow about four seconds |
| launch-hades-launch-test.sh | Deploy, release four torpedoes in sequence, then retract |

Missions 968, 967, 966 and 965 respectively use Hades type 26 and four Allied torpedoes of type 74. The launch mode uses native mission StartLaunch commands, not a new player control. Release begins at about nine seconds, with roughly seven seconds between torpedoes.

No enemies or objectives; the ship is stationary and invulnerable. Sound is off. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, and 0 for a screenshot. Close an existing game session before starting another. Remove or disable this mod to restore the original Hades.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- In-game material, stowed/deployed and timed-release review are pending. No first-pass game captures were run automatically.
- Campaign combat, damage, ejection, cloaking, distance transitions and other platforms remain untested.
- Dedicated emissive maps remain deferred; native effects are retained.
- Delivery maps are 4096 square, resampled from a 1254-square generated reconstruction of the original 256-square atlas.
- The Blender scene is a static authoring pose. Native animations and their launch mounts remain in the game model.
- Publication requires fresh official-engine gallery photography following GALLERY_PREVIEWS.md; source renders are not gallery photos.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.0

First worn Hades restoration, recessed glass, structural materials and canonical PNG export. Preserves six native parts, four animated launch arms and all original UVs; fixes 43 primitive continuation counts at texture joins. Includes four quiet review modes. Awaiting user approval.
''')
write(A/'CREDITS.md','''# Credits

Restoration contributions by KonCyptFysh. Original StarLancer artwork, ship design and assets retain their respective ownership. OpenReliant supplies the engine and native tools.

The worn atlas was reconstructed with the built-in image-generation tool using the original Torp_2 atlas. The full prompt, input/output hashes and dimensions are retained in `source/authoring/imagegen_prompts.json`. Structural material masks were authored separately.
''')
write(A/'LICENSING.md',"# Licensing\n\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . Original StarLancer assets and other third-party material retain their existing ownership and rights. Requires your own StarLancer data.\n")
write(A/'source/README.md','''# Hades editable source

`hades_worn_pbr_v1.blend` is the first-pass scene. Six parts, 368 stored finest-detail triangles (364 visible), original geometry, normals and UVs. Packed images also have verified relative paths under `resources/`; the saved scene was reopened and checked.

`originals/` preserves the native model, extracted atlas and decoded part/animation data. `maps/` contains generated artwork, final 4K maps and semantic masks. `authoring/` holds recipes, prompts and validation. `review/` contains Blender authoring views, not game photography.

Native animation is preserved in the SHP export; Blender shows the static source pose. Retain the native continuation corrections during later export. Start future work from the current scene, not by rerunning old recipes over manual changes.
''')
write(A/'source/authoring/README.md','''# Authoring records

The packed scene is the editable deliverable. Scripts document the first pass and are not a one-command portable rebuild. Local paths in records use environment placeholders; configure HADES_WORKSPACE, ART_PACK_REPOSITORY, OPENRELIANT_HOME and OPENRELIANT_SLTOOL before adapting recipes. The initial preparation reused Galahad's established native pipeline; standalone Hades build/material/export scripts are retained here.

`regions.json` records semantic material masks in the generated 1254-square atlas coordinates. Height comes from authored structures, not painted noise or insignia. Glass interiors have flat normals, low roughness and zero metallic, with separate inset/frame relief. All native animation and attachment chunks passed byte comparisons. Runtime visual acceptance remains pending.
''')
manifest=[record(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];assert len(manifest)==12
dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='first-pass-awaiting-user-review',ship='Hades',asset_revision='1.0',files=[record(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
dump(A/'compatibility-0.8.json',compat)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,engine_build=compat['engine'],engine_sha256=compat['engine_sha256'],asset_revision='1.0',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),packaging_ready=False,user_approved=False,checks=['Native SHP and four DTE round trips','881 faces audited; 43 UV continuation counts corrected','Original geometry, per-face UVs, normals, attachments and animations preserved','4K maps decode; normalized normals, flat glass normals, zero glass metallic','Engine loader generates loadout colours and inherits material maps','Packed relative source reopened without geometry/UV/material changes','Four authoring views inspected','Four launchers pass shell syntax'],game_launched=False,runtime_visual_review='pending_user')
dump(A/'validation.json',validation)
dump(A/'release.json',dict(package_name='openreliant-hades',version='0.1.0-beta.1',asset_revision='1.0',status='held',hold_reason='Awaiting user visual and animation review',minimum_openreliant='0.8.1',mod_folders=[O.name],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),channel='beta',user_approved=False,published=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json','compatibility-0.8.json']+[str(p.relative_to(A)) for p in launchers]))
category=R/'Torpedo Bombers/README.md';s=category.read_text().replace('| [Hades](Hades/README.md) | Planned; artwork not started | Coming soon |','| [Hades](Hades/README.md) | Worn first pass installed; awaiting visual and animation review | Unreleased |').replace('Hades and Scimitar remain planned.','Hades is installed for review; Scimitar remains planned.');category.write_text(s)
catalog=read(R/'catalog.json');entry=next(x for x in catalog['assets'] if x['id']=='hades')
entry.update(workStatus='in-progress',description='Worn brown, grey and green Alliance torpedo bomber with recessed glazing and preserved sliding torpedo arms. First pass awaiting in-game review.')
entry['liveries'][0].update(engine='0.8.1',engineStatus='non-visual-checks-passed-review-pending',notes=['First pass installed for user review; no published download yet.','Four native sliding torpedo arms and launch mounts retained.'])
dump(R/'catalog.json',catalog)
installed=G/'game-data/mods'/O.name;assert not installed.exists()
for p in launchers:assert not (G/p.name).exists()
conflicts=[p for p in (G/'game-data/mods').rglob('*') if p.is_file() and p.name.lower() in {x.name.lower() for x in O.iterdir() if x.suffix.lower() in ['.shp','.dte']}]
assert not conflicts,conflicts
game_was_closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
with tempfile.TemporaryDirectory(prefix='.hades-install-',dir=G) as staging:
 staged=Path(staging)/O.name;shutil.copytree(A/'mods'/O.name,staged)
 for r in manifest:assert sha(staged/Path(r['path']).name)==r['sha256']
 os.rename(staged,installed)
for p in launchers:
 q=G/p.name;shutil.copy2(p,q);q.chmod(0o755);assert sha(q)==sha(p)
for r in manifest:assert sha(A/r['path'])==sha(installed/Path(r['path']).name)==r['sha256']
dump(W/'deployment.json',dict(status='installed-ready-for-user-review',installed_at_utc=now,repository_asset=str(A),installed_mod=str(installed),launchers=[record(G/p.name,G) for p in launchers],runtime_files=manifest,exact_repository_bytes_verified=True,game_was_closed=game_was_closed,install_method='New verified mod folder atomically installed; existing mods and settings untouched',game_launched=False,runtime_visual_review='pending_user'))
state=read(D.parent/'project_state.json');state.update(status='ready_for_user_review',latest_scene=str(D/'hades_worn_pbr_v1.blend'),upright_scene=str(D/'hades_worn_pbr_v1.blend'),latest_deliverables=str(O.parent.parent),repository_asset=str(A),review_launcher=str(G/'launch-hades-test.sh'),updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='first_pass_complete_pending_user_review',pbr_authoring='complete_structural_maps_and_inset_glazing',pbr_tuning='authoring_preview_checked_runtime_pending',engine_validation='official_0_8_1_native_and_texture_loader_passed_runtime_visual_pending'),engine_validation=dict(build=compat['engine'],date_utc=now,non_visual_checks='passed',visual_review='pending_user',game_launched=False,evidence=str(W/'compatibility-0.8.json')),current_manifest=str(D/'manifest.json'))
dump(D.parent/'project_state.json',state)
dump(D/'manifest.json',dict(ship='Hades',variant='worn',status='ready_for_user_review',user_approved=False,published=False,scene=record(D/'hades_worn_pbr_v1.blend',D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],runtime_exports=manifest,maps=read(W/'validation.json')['maps'],remaining=['User in-game appearance and four torpedo-arm review','Timed four-torpedo release review','Campaign combat, damage, ejection, cloaking and distance transitions','Dedicated emissive maps','Fresh standard gallery photographs on publication']))
write(D/'README.md',f'''# Hades worn workspace

First pass installed for user review; not approved or published. Current scene: `hades_worn_pbr_v1.blend`. Original worn brown/grey/green livery, US markings, geometry and UV coordinates are retained. Structural normal/roughness/metallic maps and inset dark glass are complete. Native model, four sliding torpedo arms, launch mounts and animation data are preserved. One shared 4K PNG material set.

Official OpenReliant 0.8.1 release gate is satisfied. Native-format, map, engine texture-loader, portable-source and installed-hash checks passed. Blender views were inspected from both sides, rear and underside. Runtime visual and animation review await the user; no automatic game launch occurred.

Run `{G}/launch-hades-test.sh` for the quiet cycle review. Stowed, deployed and timed four-torpedo release wrappers are alongside it. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, 0 for screenshots.

`source/` preserves originals; `maps/` holds artwork and material masks; `work/reconstruction_v1/` contains recipes, the full built-in image-generation prompt and validation. Review images are Blender renders. The 4K delivery is resampled from the 1254-square reconstruction of the 256-square original. See manifest.json and ../project_state.json for exact status.
''')
write(O.parent.parent/'README.md','''# Hades OpenReliant 0.8.1 review export

Installed from the exact repository snapshot. `launch-hades-test.sh` defaults to the native deploy/retract cycle; stowed, deployed and timed four-torpedo release wrappers are included. Missions 968 through 965 use Hades type 26 and four Allied torpedoes (74). One canonical base/normal/ORM PNG set. User in-game review is pending.
''')
print(json.dumps(dict(status=state['status'],launcher=state['review_launcher'],runtime_files=len(manifest),runtime_bytes=sum(x['bytes'] for x in manifest),source_files=len(read(A/'source-manifest.json')['files']),game_was_closed=game_was_closed),indent=2))
