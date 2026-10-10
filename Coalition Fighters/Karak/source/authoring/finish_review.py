from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
D=Path('${KARAK_WORKSPACE}')
W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_8_v1/mods/112-karak-worn-v1'
R=Path('${ART_PACK_REPOSITORY}')
A=R/'Coalition Fighters/Karak';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.8.1-linux-x86_64'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.replace('22',str(len(json.loads((W/'native_preservation.json').read_text())['continuation_corrections']))))
def dump(p,data):write(p,json.dumps(data,indent=2)+'\n')
def record(p,root):return {'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)}
def sanitize(s):
 for x,y in [(str(D),'${KARAK_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(E/'sltool'),'${OPENRELIANT_SLTOOL}'),(str(G),'${OPENRELIANT_HOME}'),('${STARLANCER_ASSETS}','${STARLANCER_ASSETS}')]:s=s.replace(x,y)
 return s
assert (A/'source/karak_worn_pbr_v1.blend').is_file()
assert not any(p.name.startswith(('gorkr','rorkr')) for p in O.iterdir())
checks=json.loads((W/'native_checks.json').read_text());maps=json.loads((W/'map_checks.json').read_text());pres=json.loads((W/'native_preservation.json').read_text());snapshot=json.loads((W/'repository_snapshot.json').read_text())
assert all(x['exit_code']==0 for x in checks) and maps['passed'] and pres['passed'] and snapshot['packed_relative_resources_reopened']
probe=R/'.local/texture-variant-cleanup/texture-probe';probe_src=R/'tools/loadout-texture-probe/texture-probe.zig'
assert sha(probe)=='b95e2d5089555231c6db847452ead080772a076a43b79ec504841a05462cb1fb'
assert sha(probe_src)=='d1f8a83dcf634af76d28eec0eb4e06b0bde4465b355de7274fd5b1929a5ec1e9'
log=Path('/tmp/karak-texture-probe.log').read_text();assert log.startswith('PASS orkr1_hull:')
compat={'status':'passed','scope':'Non-visual native format and texture-loader checks only','checked_at_utc':now,'engine':'Official OpenReliant 0.8.1 linux-x86_64','engine_sha256':sha(E/'openreliant'),'engine_source_commit':'b91c70bba414b2b2dc16bcf687647b41701deb8a','native_checks':checks,'texture_loader':{'probe_source_sha256':sha(probe_src),'probe_binary_sha256':sha(probe),'output':log.strip(),'read_original_pixels':True,'checked_output_longest_side':256,'green_and_red_generated':True,'normal_and_orm_inherited_byte_identically':True,'input_files':[record(O/f'Orkr1_hull{x}.png'.lower(),O) for x in ('','_normal','_orm')]},'duplicated_colour_textures':False,'game_launched':False,'runtime_visual_review':'pending_user'}
dump(W/'compatibility-0.8.json',compat)
# Record exact generation provenance and the inspected authoring views.
prompts=json.loads((W/'imagegen_prompts.json').read_text())
for item in prompts['passes']:
 item['input_sha256']=sha(D/item['input']);item['output_sha256']=sha(D/item['output'])
 item['output_dimensions']=[1254,1254]
dump(W/'imagegen_prompts.json',prompts)
dump(W/'authoring_review.json',{'reviewed_at_utc':now,'kind':'Blender authoring previews, not gameplay','views':[record(D/'review/reconstruction_v1'/name,D) for name in ['material_front.png','material_opposite.png','material_belly.png','material_rear.png']],'observations':['Native silhouette and original panel/marking layout retained.','Green panes are separated from metal framing; studio reflections are rendered, not painted into the glass.','Rear recesses and underside markings inspected; no collapsed or missing visible UV faces identified.'],'runtime_visual_review':'pending_user'})

# Keep a complete authoring snapshot, with portable image references and recipes.
for directory in ['source/originals','source/maps','source/authoring','source/review/reconstruction_v1','tools']:(A/directory).mkdir(parents=True,exist_ok=True)
for p in (D/'source').iterdir():
 if p.is_file():shutil.copy2(p,A/'source/originals'/p.name)
for p in (D/'maps').glob('*.png'):shutil.copy2(p,A/'source/maps'/p.name)
for p in W.iterdir():
 if p.is_file() and p.suffix in ('.py','.json','.txt'):
  text=sanitize(p.read_text())
  if p.name=='parse_native.py':text=text.replace('import struct,json,hashlib','import os,struct,json,hashlib').replace("D=Path('${KARAK_WORKSPACE}')","D=Path(os.environ['KARAK_WORKSPACE'])")
  if p.name=='export_native.py':text=text.replace("tool='${OPENRELIANT_SLTOOL}'","tool=os.environ['OPENRELIANT_SLTOOL']")
  write(A/'source/authoring'/p.name,text)
for p in (W/'audit').glob('*.json'):write(A/'source/authoring/audit'/p.name,sanitize(p.read_text()))
for p in (D/'review/reconstruction_v1').glob('*.png'):shutil.copy2(p,A/'source/review/reconstruction_v1'/p.name)
shutil.copy2('/tmp/launch-karak-test.sh',O.parent.parent/'launch-karak-test.sh');(O.parent.parent/'launch-karak-test.sh').chmod(0o755)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
launcher=A/'tools/launch-karak-test.sh';shutil.copy2('/tmp/launch-karak-test.sh',launcher);launcher.chmod(0o755);subprocess.run(['bash','-n',str(launcher)],check=True)
write(A/'README.md','''# Karak - Worn Paint

**First pass ready for user review. Not approved or published.** Targets official OpenReliant 0.8.1; planned package 0.1.0-beta.1, artwork revision 1.0.

Restores the native Karak model's worn silver-grey alloy, red and yellow Coalition markings, caution borders, mechanical recesses and green glazing. Structural normal, roughness and metallic maps add recessed glass edges, bounded radiator relief and panel seams. Glass interiors have flat normals and a smooth reflective response. Only one unprefixed PNG material set is shipped; the engine generates loadout colours.

The original UV coordinates are retained across every detail level. Native fan/strip continuity was checked across all 855 faces in 18 detail meshes; 22 continuation counts were corrected so joined triangles use their original per-face texture coordinates. RUSN_1 is the sole referenced material; the unused chin2d2 table slot is retained as a native reference. Geometry, vertex and face normals, winding, part records, attachments and animation bytes remain unchanged. All native keyframes are retained in the game export; the Blender source is a static authoring pose.

Official 0.8.1 native round-trip and texture-loader checks passed. Authoring views were inspected from both sides, rear and underside. These are Blender previews; in-game visual review is pending. Use the quiet single-ship launcher described in INSTALL.md.
''')
write(A/'INSTALL.md','''# Installation and inspection

Copy `mods/112-karak-worn-v1` into OpenReliant's `game-data/mods` directory and enable the mod. Keep all runtime files flat. Requires your own StarLancer installation and official OpenReliant 0.8.1.

Place `tools/launch-karak-test.sh` alongside `launch-openreliant.sh`, or set OPENRELIANT_HOME to your installation. This opens mission 974 as the Karak (ship type 40), with one ship, no enemies or objectives. The launcher uses official 0.8.1 directly, sound disabled, 1920x1080 and a 60 FPS limit.

Press 7 for orbit view, arrow keys to rotate, Shift+Up/Down to zoom and 0 to save an in-game screenshot. Additional engine options can be passed to the launcher. Remove or disable the mod to restore the original Karak.

No green/red texture duplicates are required. OpenReliant generates loadout colours from the unprefixed material set.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- User in-game appearance and material tuning are pending. This first pass has not been approved for publication.
- Campaign combat, damage, ejection, distance transitions and other platforms are untested. All original UV coordinates are retained across every detail level.
- Native animations and attachments are byte-preserved; their behaviour still needs gameplay review.
- Dedicated emissive maps remain deferred.
- The 4096-square delivery atlas is resampled from a 1254-square AI reconstruction of the 256-square source; it is not native 4K generated detail.
- Source review images are Blender authoring previews. Public gallery photos must come from the user's in-game review or a separately authorized capture.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.0

First Karak worn restoration, preserved original UV layout, smooth inset green glazing, structural normal and material maps, native continuity fixes and preserved geometry/animation. Adds an official OpenReliant 0.8.1 quiet review mission and launcher. Awaiting user review.
''')
write(A/'CREDITS.md','''# Credits

Original restoration contributions by KonCyptFysh. Original StarLancer artwork, model design and game assets belong to their respective rights holders. Requires the user's original game data. OpenReliant provides the runtime and native validation tools.

Worn atlas reconstruction and glazing refinement used the built-in image-generation tool. Exact prompts and input/output provenance are preserved in `source/authoring/imagegen_prompts.json`. UV continuity, structural map authoring and native-file preservation were independently checked.
''')
write(A/'LICENSING.md','''# Licensing

KonCyptFysh's original restoration contributions are licensed CC-BY-NC-SA-4.0: https://creativecommons.org/licenses/by-nc-sa/4.0/ . Retain attribution, use non-commercially and share adaptations under the same licence.

This licence does not grant rights to the original StarLancer assets, trademarks, OpenReliant code or other third-party contributions. Their existing ownership and notices remain applicable.
''')
write(A/'source/README.md','''# Karak editable source

`karak_worn_pbr_v1.blend` is the current first-pass scene, awaiting user review. Both native parts and all 284 finest-detail stored triangles (264 visible) are preserved. Images are packed and also saved with relative `resources/` paths; the reopened snapshot passed geometry, UV, normal, transform and material-assignment checks.

`Original_Karak_UV`, `Karak_Atlas_UV_v1` and `Karak_Delivery_UV_v1` preserve original coordinates. All visible finest-detail UV triangles passed the degeneracy and distortion checks. `authoring/native_preservation.json` records the fan/strip continuation fixes; preserve them on later exports. Native animation/keyframe data remains in the game model and decoded originals. The Blender scene is a static authoring pose.

`originals/` holds immutable decoded sources. `maps/` contains the generated atlas pass, delivered base/normal/roughness/metallic maps, height and region masks. Generation produced a 1254-square image from the original 256-square atlas; delivery maps are 4096-square. Full prompts are in `authoring/imagegen_prompts.json`.

`review/reconstruction_v1/` contains Blender authoring views, not in-game captures. Publication and runtime visual acceptance remain pending.
''')
write(A/'source/authoring/README.md','''# Authoring history

The packed editable scene in `../karak_worn_pbr_v1.blend` is the current source. Recipes record this initial pass; do not rerun them over later manual edits.

Set KARAK_WORKSPACE to a separate writable workspace, ART_PACK_REPOSITORY to the art-pack repository and OPENRELIANT_SLTOOL to the official 0.8.1 sltool executable. Recreate `source/` from `../originals/`, `maps/` from `../maps/`, `work/reconstruction_v1/` for recipes/reports and `review/reconstruction_v1/` for authoring previews. `build_materials.py` expects the source scene created by `parse_native.py` and `build_source.py`. Blender scripts require Blender; native export uses Python, NumPy and Pillow.

Machine-specific report paths are replaced by environment placeholders. Runtime review and publication status are recorded at the pack root. No duplicated g/r loadout maps are emitted by this exporter.
''')
manifest=[record(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];dump(A/'asset-manifest.json',manifest)
source_manifest={'status':'first-pass-awaiting-user-review','ship':'Karak','asset_revision':'1.0','files':[record(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]};dump(A/'source-manifest.json',source_manifest)
dump(A/'compatibility-0.8.json',compat)
validation={'status':'non-visual-checks-passed-awaiting-user-review','checked_at_utc':now,'engine_build':compat['engine'],'engine_sha256':compat['engine_sha256'],'asset_revision':'1.0','asset_manifest_sha256':sha(A/'asset-manifest.json'),'source_manifest_sha256':sha(A/'source-manifest.json'),'packaging_ready':False,'user_approved':False,'checks':['Official 0.8.1 native SHP and DTE round-trip checks passed.','All 855 native faces checked for shared-corner UV continuity.','Only the referenced texture name and 22 continuation counts changed; all other native bytes preserved.','Delivered 4096-square maps decode, normals are normalized and glass interiors flat; ORM channels match source maps.','Official 0.8.1 texture loader generates green/red colours and inherits normal/ORM bytes.','Packed relative Blender source reopened with geometry, UV, normal, transform and material parity.','Front, opposite, rear and underside Blender authoring previews inspected.','Review launcher passes shell syntax checks.'],'game_launched':False,'runtime_visual_review':'pending_user','limitations':['In-game material tuning and visual approval remain pending.','Campaign combat, damage, animation, ejection and distance transitions are untested.']};dump(A/'validation.json',validation)
release={'package_name':'openreliant-karak','version':'0.1.0-beta.1','asset_revision':'1.0','status':'held','hold_reason':'Awaiting user in-game visual review and approval','minimum_openreliant':'0.8.1','mod_folders':[O.name],'asset_manifest_sha256':sha(A/'asset-manifest.json'),'source_manifest_sha256':sha(A/'source-manifest.json'),'channel':'beta','user_approved':False,'published':False,'include_documents':['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','validation.json','release.json','compatibility-0.8.json','tools/launch-karak-test.sh']};dump(A/'release.json',release)
category=R/'Coalition Fighters/README.md';text=category.read_text();row='| [Karak](Karak/README.md) | Worn first pass installed; awaiting user in-game review | Unreleased |\n'
if '[Karak]' not in text:text=text.replace('\nTorpedo bombers',row+'\nTorpedo bombers')
text=text.replace('Karak has not been started.', 'Karak is installed locally for its first in-game review.');category.write_text(text)
# Deploy exactly the repository runtime snapshot, with no changes to other mods or settings.
game_was_closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
installed=G/'game-data/mods'/O.name
assert not installed.exists(),'Existing Karak install requires explicit comparison before replacement'
import tempfile
# New folder only: stage outside the scanned mods directory, verify, then rename
# atomically. Never overwrite files loaded by an existing game session.
with tempfile.TemporaryDirectory(prefix='.karak-install-',dir=G) as staging:
 staged=Path(staging)/O.name;shutil.copytree(A/'mods'/O.name,staged)
 for r in manifest:assert sha(staged/Path(r['path']).name)==r['sha256']
 os.rename(staged,installed)
installed_launcher=G/'launch-karak-test.sh';assert not installed_launcher.exists();shutil.copy2(launcher,installed_launcher);installed_launcher.chmod(0o755)
for r in manifest:assert sha(A/r['path'])==sha(installed/Path(r['path']).name)==r['sha256']
assert sha(launcher)==sha(installed_launcher);subprocess.run(['bash','-n',str(installed_launcher)],check=True)
deploy={'status':'installed-ready-for-user-review','installed_at_utc':now,'repository_asset':str(A),'installed_mod':str(installed),'launcher':str(installed_launcher),'launcher_sha256':sha(installed_launcher),'runtime_files':manifest,'exact_repository_bytes_verified':True,'game_was_closed':game_was_closed,'install_method':'Verified new folder staged outside mods and atomically renamed; no existing mod files or game settings touched','current_game_session':'No game session launched or changed; close any existing session before using the Karak launcher','engine_mod_index_evidence':'Official 0.8.1 src/engine/game/bigfile/mods.zig Mods.openOrdered and Mods.readFile use the opened mod list and index','game_launched':False,'runtime_visual_review':'pending_user'};dump(W/'deployment.json',deploy)
state_path=D.parent/'project_state.json';state=json.loads(state_path.read_text());state.update({'status':'ready_for_user_review','latest_scene':str(D/'karak_worn_pbr_v1.blend'),'latest_deliverables':str(O.parent.parent),'repository_asset':str(A),'review_launcher':str(installed_launcher),'updated_at_utc':now,'user_approved':False,'published':False,'progress':{'texture_uv':'first_pass_complete_pending_user_review','pbr_authoring':'complete_structural_maps_and_inset_glazing','pbr_tuning':'authoring_preview_checked_runtime_pending','engine_validation':'official_0_8_1_native_and_texture_loader_passed_runtime_visual_pending'},'engine_validation':{'build':compat['engine'],'date_utc':now,'non_visual_checks':'passed','visual_review':'pending_user','game_launched':False,'evidence':str(W/'compatibility-0.8.json')},'current_manifest':str(D/'manifest.json')});dump(state_path,state)
canonical_manifest={'ship':'Karak','variant':'worn','status':'ready_for_user_review','user_approved':False,'published':False,'scene':record(D/'karak_worn_pbr_v1.blend',D),'pbr_release_gate':state['pbr_release_gate'],'progress':state['progress'],'review_evidence':str(D/'review/reconstruction_v1'),'engine_validation':state['engine_validation'],'runtime_exports':manifest,'maps':json.loads((W/'validation.json').read_text())['maps'],'remaining':['User in-game visual review and material tuning','Campaign, damage, animation, ejection and distance transitions','Dedicated emissive maps']};dump(D/'manifest.json',canonical_manifest)
write(D/'README.md',f'''# Karak worn workspace

First pass installed and ready for user review; not approved or published. Current editable scene: `karak_worn_pbr_v1.blend`. Original model, original atlas and original UV layers remain preserved.

Completed worn atlas reconstruction, preserved original UV layout, structural normal/roughness/metallic maps, smooth inset green glazing, native fan/strip continuity corrections. One shared 4K PNG material set; no duplicated green/red textures.

Release gate satisfied: official OpenReliant 0.8.1. Texture/UV and PBR authoring first passes are complete. Authoring views inspected from both sides, rear and underside. Native round trips, material loading/generated colours, portable source and exact installed-file hashes passed. In-game visual review and tuning remain pending; the game was not automatically launched.

Run `{installed_launcher}` for a quiet single-ship scene. Press 7 for orbit, arrow keys to rotate, Shift+Up/Down to zoom and 0 for screenshots.

`source/` contains immutable originals; `maps/` retains generation outputs and all material masks; `work/reconstruction_v1/` records prompts, recipes and validation; `review/reconstruction_v1/` contains Blender authoring views. Built-in image-generation prompts: `work/reconstruction_v1/imagegen_prompts.json`. `manifest.json` and `../project_state.json` record current status.

Repository review snapshot: `{A}`. Runtime export: `exports/openreliant_0_8_v1/mods/112-karak-worn-v1`. Dedicated emissive maps and broader gameplay checks remain deferred.
''')
write(O.parent.parent/'README.md','''# Karak OpenReliant 0.8.1 review export

Installed from the exact repository snapshot. First pass awaiting user visual review; not approved or published. The executable `launch-karak-test.sh` opens the quiet mission 974 with ship 40. Files remain flat in `mods/112-karak-worn-v1`; only unprefixed base/normal/ORM PNG maps are required.

Native round-trip, structural-map, official texture-loader and installed hash checks passed. No automatic game capture was performed.
''')
print(json.dumps({'status':state['status'],'repository':str(A),'mod':str(installed),'launcher':str(installed_launcher),'runtime_files':len(manifest),'runtime_bytes':sum(x['bytes'] for x in manifest),'portable_source_files':len(source_manifest['files']),'visual_review':'pending'},indent=2))
