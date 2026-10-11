import os
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
D=Path(os.environ['GALAHAD_WORKSPACE'])
W=D/'work/reconstruction_v1'; O=D/'exports/openreliant_0_8_v1/mods/113-galahad-worn-v1'
R=Path('${ART_PACK_REPOSITORY}')
A=R/'Torpedo Bombers/Galahad'; G=Path('${OPENRELIANT_HOME}'); E=G/'releases/openreliant-v0.8.1-linux-x86_64'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,r):write(p,json.dumps(r,indent=2)+'\n')
def record(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
def sanitize(s):
 for x,y in [(str(D),'${GALAHAD_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(E/'sltool'),'${OPENRELIANT_SLTOOL}'),(str(G),'${OPENRELIANT_HOME}'),('${STARLANCER_ASSETS}','${STARLANCER_ASSETS}')]:s=s.replace(x,y)
 return s
assert (A/'source/galahad_worn_pbr_v1.blend').is_file()
assert sorted(p.name for p in O.glob('*.png'))==['mod.png','orgl1_hull.png','orgl1_hull_normal.png','orgl1_hull_orm.png']
checks=json.loads((W/'native_checks.json').read_text());maps=json.loads((W/'map_checks.json').read_text());pres=json.loads((W/'native_preservation.json').read_text());snapshot=json.loads((W/'repository_snapshot.json').read_text())
assert all(x['exit_code']==0 for x in checks) and maps['passed'] and pres['passed'] and snapshot['packed_relative_resources_reopened']
assert len(pres['continuation_corrections'])==6 and len(pres['detail_meshes'])==37
probe=R/'.local/texture-variant-cleanup/texture-probe';probe_src=R/'tools/loadout-texture-probe/texture-probe.zig'
assert sha(probe)=='b95e2d5089555231c6db847452ead080772a076a43b79ec504841a05462cb1fb'
assert sha(probe_src)=='d1f8a83dcf634af76d28eec0eb4e06b0bde4465b355de7274fd5b1929a5ec1e9'
assert sha(E/'openreliant')=='aa5e81293be85b28884460476427d0942556d6945b3e89da390365d480d9c5ea'
log=Path('/tmp/galahad-texture-probe.log').read_text();assert log.startswith('PASS orgl1_hull:')
compat=dict(status='passed',scope='Non-visual native format and texture-loader checks only',checked_at_utc=now,engine='Official OpenReliant 0.8.1 linux-x86_64',engine_sha256=sha(E/'openreliant'),engine_source_commit='b91c70bba414b2b2dc16bcf687647b41701deb8a',native_checks=checks,texture_loader=dict(probe_source_sha256=sha(probe_src),probe_binary_sha256=sha(probe),output=log.strip(),read_original_pixels=True,checked_output_longest_side=256,green_and_red_generated=True,normal_and_orm_inherited_byte_identically=True,input_files=[record(O/f'orgl1_hull{x}.png',O) for x in ('','_normal','_orm')]),duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility-0.8.json',compat)
dump(W/'authoring_review.json',dict(reviewed_at_utc=now,kind='Blender authoring previews, not gameplay',views=[record(D/'review/reconstruction_v1'/f'material_{v}.png',D) for v in ('front','opposite','belly','rear')],observations=['Native upright silhouette and original panel layout retained.','Both upper rear crests show the corrected silver RAF bird using the accepted Crusader treatment.','The front windshield is a single dark green pane; other glass retains separate metal framing.','Glass highlights in the preview are studio reflections, not diffuse painted highlights.','Rear and underside surfaces inspected; no collapsed visible UV faces identified.'],runtime_visual_review='pending_user'))
dump(W/'deployment_mechanism.json',dict(native_file='BTB_Glhd.SHP',ship_type=25,parts=6,deploy_parts=['Galahad foot 1','Galahad foot 2','Galahad foot 03','Galahad foot 04'],launch_points=dict(part='Galahad Body',count=2,positions=[[-83,58,56],[83,58,56]]),distinction='The two launch mounts belong to the body, not the four animated feet. No torpedo-bay geometry or attachment movement has been invented.',review_modes={'973':'stowed','972':'native deploy held','971':'native deploy/reverse cycle','970':'deploy; timed StartLaunch for torpedo 1, then torpedo 2; wait until launched; reverse deploy'},launch_control='Native player carried-torpedo input is Kamov-specific; Galahad review uses mission StartLaunch (0x14).',carried_ship_type=74,carried_ship_count=2,animation_bytes_preserved=True,gameplay_verified=False))
# Preserve this exact finishing recipe before taking the authoring snapshot.
if Path(__file__).resolve()!=(W/'finish_review.py').resolve():shutil.copy2(__file__,W/'finish_review.py')
shutil.copytree(D/'source',A/'source/originals',dirs_exist_ok=True)
for directory in ['source/maps','source/authoring','source/review/reconstruction_v1','tools']:(A/directory).mkdir(parents=True,exist_ok=True)
for p in (D/'maps').glob('*.png'):shutil.copy2(p,A/'source/maps'/p.name)
for p in W.iterdir():
 if p.is_file() and p.suffix in ('.py','.json','.txt'):
  s=sanitize(p.read_text())
  if p.suffix=='.py':
   if "Path(os.environ['GALAHAD_WORKSPACE'])" in s:s='import os\n'+s.replace("Path(os.environ['GALAHAD_WORKSPACE'])","Path(os.environ['GALAHAD_WORKSPACE'])")
   s=s.replace("tool=os.environ['OPENRELIANT_SLTOOL']","tool=os.environ['OPENRELIANT_SLTOOL']")
  write(A/'source/authoring'/p.name,s)
for p in (D/'review/reconstruction_v1').glob('*.png'):shutil.copy2(p,A/'source/review/reconstruction_v1'/p.name)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
launchers=[]
for p in sorted(O.parent.parent.glob('launch-galahad-*.sh')):
 dest=A/'tools'/p.name;shutil.copy2(p,dest);dest.chmod(0o755);subprocess.run(['bash','-n',str(dest)],check=True);launchers.append(dest)
assert len(launchers)==4
write(A/'README.md','''# Galahad - Worn Paint

**First pass ready for user review. Not approved or published.** Targets official OpenReliant 0.8.1; planned package 0.1.0-beta.1, artwork revision 1.0.

Restores the native Galahad's worn grey alloy, British markings, caution borders, mechanical recesses and dark green glazing. The RAF crest uses the same corrected silver, short-tailed bird treatment as Crusader, upright within Galahad's original emblem. Structural normal, roughness and metallic maps give the glass recessed edges and separate metal framing. One unprefixed PNG material set is supplied; OpenReliant generates loadout colours.

All native UV coordinates are retained. The export checks 1,012 faces across 37 detail meshes and corrects six fan/strip continuation counts at texture joins. Geometry, vertex and face normals, winding, part records, attachments and animation bytes are unchanged. The six-part BTB_Glhd model is the only Galahad model identified in the inspected engine mapping.

Four native feet carry the deploy animation. The body's two torpedo launch points are separate from those feet. Review missions provide stowed, deployed, continuous-cycle and timed two-torpedo release modes without changing the original mechanism. Blender is a static authoring pose; all native animation data remains in the game export.

Official 0.8.1 format and texture-loader checks passed. Blender views were inspected from both sides, rear and underside. In-game visual and animation review are pending. See INSTALL.md for the quiet review launchers.
''')
write(A/'INSTALL.md','''# Installation and inspection

Copy `mods/113-galahad-worn-v1` into OpenReliant's `game-data/mods` directory and enable it. Runtime files stay flat. Requires your own StarLancer installation and official OpenReliant 0.8.1.

Copy all four `tools/launch-galahad-*.sh` scripts together alongside `launch-openreliant.sh`, or set OPENRELIANT_HOME to the installation. The main script accepts a mode followed by optional engine options:

| Launcher or mode | Review |
| --- | --- |
| launch-galahad-test.sh (default cycle) | Start stowed, repeatedly deploy and reverse the four native feet |
| launch-galahad-stowed-test.sh | Hold original stowed pose with two carried torpedoes |
| launch-galahad-deployed-test.sh | Deploy and hold; allow about four seconds for the native animation |
| launch-galahad-launch-test.sh | Deploy, release torpedo 1 after about nine seconds and torpedo 2 about seven seconds later, then stow |

The launch sequence uses native mission StartLaunch commands. Galahad does not share Kamov's player carried-torpedo Launch Missile shortcut. Torpedoes use the existing Allied torpedo asset and launch mounts. The review does not add new gameplay controls.

These are missions 973, 972, 971 and 970 respectively, with Galahad ship type 25 and two torpedoes of type 74. There are no enemies or objectives; engines, guns and ejection are disabled and the three objects are invulnerable. Launchers use official 0.8.1 directly, sound disabled, 1920x1080, 60 FPS. Close an existing session before launching a new one.

Press 7 for orbit, arrow keys to rotate, Shift+Up/Down to zoom and 0 for screenshots. Remove or disable the mod to restore the original Galahad. OpenReliant generates green/red loadout textures; duplicated colour files are unnecessary.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- User in-game visual review, deployment and timed-release testing are pending. This first pass has not been approved for publication.
- Campaign combat, damage, ejection, cloaking, distance transitions and other platforms are untested.
- Native launch mounts and the four animated feet are separate mechanisms. Their original placement and all animation bytes are retained.
- Dedicated emissive maps remain deferred.
- The 4096-square delivery atlas is resampled from a 1254-square AI reconstruction of the 256-square source, not native 4K generated detail.
- Source preview images are Blender renders. Public gallery photographs await user in-game review or separately authorized capture.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.0

First Galahad worn restoration with original UVs, corrected silver RAF bird matching Crusader, inset green glazing, structural surface maps, six native continuity corrections, preserved deployment animation and two launch mounts. Includes official OpenReliant 0.8.1 review modes for stowed, deployed, cycling and timed torpedo release. Awaiting user review.
''')
write(A/'CREDITS.md','''# Credits

Original restoration contributions by KonCyptFysh. Original StarLancer artwork, model design and game assets retain their respective ownership. Requires the user's original game data. OpenReliant supplies the runtime and native tools.

Worn reconstruction, front-glass refinement and the RAF bird correction used the built-in image-generation tool. The previously accepted Crusader bird treatment and a saved RAF-badge reference informed the correction. Exact prompts, reference hashes and output provenance are in `source/authoring/imagegen_prompts.json`; reference images and their existing provenance are in `source/originals/references/`.
''')
write(A/'LICENSING.md','''# Licensing

KonCyptFysh's original restoration contributions are licensed CC-BY-NC-SA-4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/ . Retain attribution, use non-commercially and share adaptations under the same licence.

This licence grants no additional rights to original StarLancer assets, RAF insignia, reference artwork, trademarks, OpenReliant code or other third-party contributions. Their existing ownership and notices remain applicable.
''')
write(A/'source/README.md','''# Galahad editable source

`galahad_worn_pbr_v1.blend` is the current first-pass scene. Six parts and 420 finest-detail stored triangles (412 visible) are preserved. Images are packed and also saved with relative `resources/` paths; reopening passed geometry, UV, normal, transform and material-assignment checks. This scene is a static authoring pose; the native game export preserves the animations.

`Original_Galahad_UV`, `Galahad_Atlas_UV_v1` and `Galahad_Delivery_UV_v1` retain original coordinates. `authoring/native_preservation.json` records six continuation corrections across 37 native detail meshes and 1,012 faces; retain these corrections on later exports.

`originals/` contains immutable decoded source files and the RAF references. `maps/` retains both generated atlas passes, all delivered material maps and structural masks. The original atlas is 256 square, generation produced 1254-square images and delivery maps are 4096 square. Full built-in image-generation prompts and provenance are in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains Blender views, not gameplay. In-game visual and animation acceptance remain pending.
''')
write(A/'source/authoring/README.md','''# Authoring history

The packed scene in `../galahad_worn_pbr_v1.blend` is the current source. Recipes document this first pass; do not regenerate over later manual changes. Native animations and launch mounts remain in the SHP and decoded source records. The editable Blender scene is a static pose.

Machine-specific report paths use environment placeholders. A reconstruction workspace needs `source/` from `../originals/`, `maps/` from `../maps/`, and named work and review folders. Set GALAHAD_WORKSPACE, ART_PACK_REPOSITORY and OPENRELIANT_SLTOOL appropriately before adapting/running the historical recipes. Blender scripts require Blender; map/native export uses Python, NumPy and Pillow. Packaging/install recipes are records of the original local operation and need destination review before reuse.

Prompts, reference images and generation output hashes are retained. Structural masks keep the painted RAF crest flat while glass has an independent inset and metal frame. Native join corrections preserve the original per-face UV coordinates.
''')
manifest=[record(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];assert len(manifest)==12
dump(A/'asset-manifest.json',manifest)
source_manifest=dict(status='first-pass-awaiting-user-review',ship='Galahad',asset_revision='1.0',files=[record(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]);dump(A/'source-manifest.json',source_manifest)
dump(A/'compatibility-0.8.json',compat)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,engine_build=compat['engine'],engine_sha256=compat['engine_sha256'],asset_revision='1.0',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),packaging_ready=False,user_approved=False,checks=['Official 0.8.1 SHP and four DTE round-trip checks passed.','All 1,012 native faces checked for UV continuity; six continuation counts corrected.','Only texture names and continuation counts changed; all other native bytes preserved.','4096-square maps decode; normals normalized, glass interior normals flat and metallic zero.','Official-engine loader generates green/red colours and inherits normal/ORM bytes.','Packed relative Blender scene reopened with geometry/UV/normal/transform/material parity.','Front, opposite, rear and belly authoring renders inspected.','Four launchers pass shell syntax checks.'],game_launched=False,runtime_visual_review='pending_user',limitations=['In-game material and animation tuning await user review.','Timed release, campaign combat, damage, ejection, cloaking and distance transitions need gameplay testing.'])
dump(A/'validation.json',validation)
dump(A/'release.json',dict(package_name='openreliant-galahad',version='0.1.0-beta.1',asset_revision='1.0',status='held',hold_reason='Awaiting user in-game visual review and approval',minimum_openreliant='0.8.1',mod_folders=[O.name],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),channel='beta',user_approved=False,published=False,include_documents=['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json','compatibility-0.8.json']+[str(p.relative_to(A)) for p in launchers]))
category=R/'Torpedo Bombers/README.md';s=category.read_text()
if '[Galahad]' not in s:s=s.replace('\nKamov\'s current beta', '| [Galahad](Galahad/README.md) | Worn first pass installed; awaiting visual and animation review | Unreleased |\n\nKamov\'s current beta')
category.write_text(s)
catalog=R/'catalog.json';r=json.loads(catalog.read_text());entry=next(x for x in r['assets'] if x['id']=='galahad')
entry.update(folder='Torpedo Bombers/Galahad',workStatus='in-progress',description='Worn grey Alliance torpedo bomber with corrected silver RAF crests, recessed green glazing and preserved native deployment parts. First pass awaiting in-game review.')
entry['liveries'][0].update(engine='0.8.1',engineStatus='non-visual-checks-passed-review-pending',notes=['First pass installed for user review; no published download yet.','Native six-part model retains its deploy animation and two body-mounted torpedo launch points.'])
dump(catalog,r)
# Install only this new mod folder, from the exact repository snapshot.
installed=G/'game-data/mods'/O.name;assert not installed.exists(),'Existing Galahad install requires comparison before replacement'
for p in launchers:assert not (G/p.name).exists()
game_was_closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
with tempfile.TemporaryDirectory(prefix='.galahad-install-',dir=G) as staging:
 staged=Path(staging)/O.name;shutil.copytree(A/'mods'/O.name,staged)
 for r in manifest:assert sha(staged/Path(r['path']).name)==r['sha256']
 os.rename(staged,installed)
for p in launchers:
 q=G/p.name;shutil.copy2(p,q);q.chmod(0o755);assert sha(q)==sha(p);subprocess.run(['bash','-n',str(q)],check=True)
for r in manifest:assert sha(A/r['path'])==sha(installed/Path(r['path']).name)==r['sha256']
dump(W/'deployment.json',dict(status='installed-ready-for-user-review',installed_at_utc=now,repository_asset=str(A),installed_mod=str(installed),launchers=[record(G/p.name,G) for p in launchers],runtime_files=manifest,exact_repository_bytes_verified=True,game_was_closed=game_was_closed,install_method='Verified new mod folder staged outside mods and atomically renamed; no existing mods or settings modified',game_launched=False,runtime_visual_review='pending_user'))
state_path=D.parent/'project_state.json';state=json.loads(state_path.read_text())
state.update(status='ready_for_user_review',latest_scene=str(D/'galahad_worn_pbr_v1.blend'),latest_deliverables=str(O.parent.parent),repository_asset=str(A),review_launcher=str(G/'launch-galahad-test.sh'),updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='first_pass_complete_pending_user_review',pbr_authoring='complete_structural_maps_and_inset_glazing',pbr_tuning='authoring_preview_checked_runtime_pending',engine_validation='official_0_8_1_native_and_texture_loader_passed_runtime_visual_pending'),engine_validation=dict(build=compat['engine'],date_utc=now,non_visual_checks='passed',visual_review='pending_user',game_launched=False,evidence=str(W/'compatibility-0.8.json')),current_manifest=str(D/'manifest.json'))
dump(state_path,state)
dump(D/'manifest.json',dict(ship='Galahad',variant='worn',status='ready_for_user_review',user_approved=False,published=False,scene=record(D/'galahad_worn_pbr_v1.blend',D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],review_evidence=str(D/'review/reconstruction_v1'),engine_validation=state['engine_validation'],runtime_exports=manifest,maps=json.loads((W/'validation.json').read_text())['maps'],remaining=['User visual review and material tuning','Deployment and timed two-torpedo release review','Campaign, damage, ejection, cloaking and distance transitions','Dedicated emissive maps']))
write(D/'README.md',f'''# Galahad worn workspace

First pass installed for user review; not approved or published. Current scene: `galahad_worn_pbr_v1.blend`. The worn restoration retains original geometry and UVs, includes the corrected silver RAF bird matching Crusader, inset green glazing and structural normal/roughness/metallic maps. Original geometry, animation, attachments and source atlas are preserved. One shared 4K PNG material set; no redundant green/red copies.

Official OpenReliant 0.8.1 release gate is satisfied. Native and texture-loader checks, portable-source reopen and exact installed-file hashes passed. Blender views were inspected from both sides, rear and underside. Runtime visual and animation review remain pending; no game session was automatically launched.

Run `{G}/launch-galahad-test.sh` for the quiet cycle review. Separate `stowed`, `deployed` and `launch` wrappers are alongside it. The latter is a timed two-torpedo release using native mission commands. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom, 0 for screenshots.

`source/` contains immutable originals and Crusader/RAF references; `maps/` contains both generated atlases and all materials/masks; `work/reconstruction_v1/` holds recipes, prompts and validation. Full built-in image-generation prompts: `work/reconstruction_v1/imagegen_prompts.json`. `review/reconstruction_v1/` contains Blender views. Repository snapshot: `{A}`. See `manifest.json` and `../project_state.json` for progress.
''')
write(O.parent.parent/'README.md','''# Galahad OpenReliant 0.8.1 review export

First pass installed from the exact repository snapshot; awaiting user visual and animation review. `launch-galahad-test.sh` defaults to cycling the native deploy animation. Separate stowed, deployed and timed-launch wrappers are included. Missions 973 through 970 use ship type 25 with two Allied torpedoes (type 74).

Flat runtime folder: `mods/113-galahad-worn-v1`. One unprefixed PNG base/normal/ORM set. Native format, map, official-engine loader, portable-source and installed-hash checks passed. No automated game capture was performed.
''')
print(json.dumps(dict(status=state['status'],repository=str(A),mod=str(installed),launcher=state['review_launcher'],runtime_files=len(manifest),runtime_bytes=sum(x['bytes'] for x in manifest),source_files=len(source_manifest['files']),visual_review='pending'),indent=2))
