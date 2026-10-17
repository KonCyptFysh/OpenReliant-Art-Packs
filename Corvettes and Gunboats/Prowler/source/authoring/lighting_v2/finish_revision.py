from pathlib import Path
import json,hashlib,shutil,datetime,subprocess
D=Path('${PROWLER_WORKSPACE}');W=D/'work/lighting_v2';O=D/'exports/openreliant_0_18_v2/mods/117-prowler-worn-v1';R=Path('${ART_PACK_REPOSITORY}');A=R/'Corvettes and Gunboats/Prowler';G=Path('${OPENRELIANT_HOME}');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
log=Path('/tmp/prowler-lighting-v2-runtime.log').read_text();assert 'PROWLER_TEST PASS' in log and 'warning(scripts)' not in log and 'error(' not in log,log[-1500:]
assert 'PASS 36 response checks' in (W/'response-tests.log').read_text()
for name in ['material_edit_audit.json','repository_snapshot.json','nozzle_surface_audit.json','native_preservation.json']:assert (W/name).exists()
shutil.copy2('/tmp/prowler-lighting-v2-runtime.log',W/'runtime-integration.log')
shutil.copy2('/tmp/prowler-lighting-v2-probe/mods/117-prowler-worn-v1/test_runtime.luau',W/'test_runtime.luau')
shutil.copy2('/tmp/prowler-lighting-v2-functional.png',D/'review/lighting_v2/runtime-functional.png')
# Fresh file manifests after launcher, thumbnail and component-health adjustments.
tiers=read(W/'resolution_checks.json')
for row in tiers['tiers']:
 dest=Path(row['runtime']);row['files']=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.iterdir()) if p.is_file()]
 for p in O.glob('*.luau'):assert sha(p)==sha(dest/p.name)
 assert sha(O/'prowler_systems.glsl')==sha(dest/'prowler_systems.glsl')
dump(W/'resolution_checks.json',tiers)
summary='Muted green glazing with a softer emission, worn black-outlined AL-47 stencil, and thrust-responsive lighting centred on the three native exhaust nozzles.'
lighting='''# Prowler lighting and material revision 1.1

Ready for review on official OpenReliant 0.18.0; not approved or published.

The old intact-hull red lamp at local (-15.48, -57.69, -2156.43), intensity 8, is disabled. The original three exhaust attachments, four turret mounts, wreck lamp, geometry, UVs, normals and animation records are unchanged from the first restoration export.

The replacement local light sits aft of each nozzle: side pod 1 (6.418, -0.968, -780), side pod 2 (-10.572, 2.617, -791.5), central engine (-2.6, 289.3, -1640), each in its own native part frame. It follows forward thrust with 0.45-second rise and 0.22-second fall constants. Nozzle interiors heat over eight seconds and cool over fourteen seconds. Exact native face planes and normal directions restrict emission to the recessed interiors and local illumination to the nozzle/rim surfaces; exterior casings do not retain heat. All parts and all detail levels were sampled to exclude unrelated hull, support-arm and wreck surfaces. Simplified nozzles retain supported detail; coarse levels that omit the interiors omit their heat.

The cabin emission remains confined to the existing glass mask and mullions. Its RGB changes from (0.25, 0.43, 0.56) to (0.10, 0.16, 0.07), about 64% less encoded luminance. Base glass is dark muted green. The AL-47 stencil keeps its size, orientation and position, with a thin black outline, chips and scratches. Generated edits are composited only through local masks; surrounding hull texels and structural material maps are retained.

Cabin behaviour uses the Kurgen response: health dimming, an 8% armour-loss threshold within 0.35 seconds for hit flicker, and irregular power faults at or below 30% health with 3–6 seconds between bursts. Prowler health also includes its actual hull component. Its five damageable components are one hull and four turrets; the engine pods have no separate engine health. Engine-disable cuts drive, and retained nozzle heat cools naturally. Cloak, lights-off and destruction suppress the surface effect.

This is a scoped surface light, not a new scene light: it does not illuminate nearby ships or mounted turret models. Native plume response remains the engine's own. Enable MATERIALS, PER-PIXEL LIGHTING and MOD EFFECTS; BLOOM adds the halo. No engine binary or global shader is replaced. Adapted OpenReliant lighting code retains MPL-2.0 attribution. Revalidate against later engine shader versions.

Restart the Prowler launcher after installing. F5 cycles thrust through 0/50/100%, F6 applies a small review hit, F7 a large hit, F8 restores review armour, F9 toggles engine-disable. Hold full thrust for around 20 seconds, cut it, then watch the nozzle interiors cool. These controls exist only in mission 961. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom.

Native model/mission validation, 36 response checks, all-detail nozzle-scope audit, official shader compilation, real-object functional integration, all three resolution-loader probes, and portable-source reopening pass. The isolated functional test uses a twofold response clock; the installed scripts use ordinary simulation time and contain no test module. Game appearance remains pending user review. Functional images are test evidence, not gallery photography.
'''
(W/'LIGHTING.md').write_text(lighting);(D/'LIGHTING.md').write_text(lighting)
for n in ['README.md','INSTALL.md','KNOWN_ISSUES.md','CHANGELOG.md','CREDITS.md','LICENSING.md','asset-manifest.json','source-manifest.json','compatibility-0.18.json','validation.json','release.json']:
 p=A/n;q=W/'before/repository'/n;q.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and not q.exists():shutil.copy2(p,q)
# Preserve v1 runtime and install before updating the active review copies.
for src,name in [(A/'mods'/O.name,'repository-runtime'),(G/'game-data/mods'/O.name,'installed-runtime')]:
 dest=W/'before'/name
 if src.exists() and not dest.exists():shutil.copytree(src,dest)
for p in [G/'launch-prowler-test.sh']:
 dest=W/'before'/p.name
 if p.exists() and not dest.exists():shutil.copy2(p,dest)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
for p in (D/'maps').glob('*_v2.png'):shutil.copy2(p,A/'source/maps'/p.name)
shutil.copytree(W/'inputs',A/'source/authoring/lighting_v2/inputs',dirs_exist_ok=True)
replacements=[(str(D),'${PROWLER_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(G),'${OPENRELIANT_HOME}'),('${IMAGEGEN_ARCHIVE}','${IMAGEGEN_ARCHIVE}')]
for p in W.iterdir():
 if p.is_file() and p.suffix in ['.json','.py','.glsl','.luau','.txt','.log','.md']:
  s=p.read_text()
  for old,new in replacements:s=s.replace(old,new)
  q=A/'source/authoring/lighting_v2'/p.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
shutil.copytree(D/'review/lighting_v2',A/'source/review/lighting_v2',dirs_exist_ok=True)
shutil.copy2(D/'LIGHTING.md',A/'LIGHTING.md')
shutil.copy2(D/'exports/openreliant_0_18_v2/launch-prowler-test.sh',A/'tools/launch-prowler-test.sh')
(A/'README.md').write_text('# Prowler - Worn Paint\n\n**Revision 1.1 ready for review; not approved or published.** Requires official OpenReliant 0.18.0.\n\n'+summary+' Original hull detailing, geometry and UVs remain; shared native Alliance turrets are unchanged.\n\nAll 1K, 2K and 4K local review exports have been refreshed. See LIGHTING.md for behaviour, review controls and rendering scope.\n')
(A/'INSTALL.md').write_text('# Local review installation\n\nCopy mods/117-prowler-worn-v1 into your OpenReliant game-data/mods folder, replacing this pack\'s previous review copy. Enable the mod and restart the game. Requires official 0.18.0, MATERIALS, PER-PIXEL LIGHTING and MOD EFFECTS; BLOOM adds a halo.\n\nRun tools/launch-prowler-test.sh for mission 961. Press F5 for thrust, F6/F7 for review damage, F8 to restore, F9 for engine-disable. Press 7 for orbit; arrows rotate and Shift+Up/Down zoom. See LIGHTING.md.\n')
(A/'KNOWN_ISSUES.md').write_text('# Review status\n\nRevision 1.1 awaits user visual review and approval. Campaign, firing and changing-distance checks remain part of review.\n\nThe engine surface light affects nozzle/rim surfaces only; it does not cast onto other ships or mounted turrets. Native engine parts are not separately damageable. Coarse detail levels without nozzle interiors omit thermal emission. Revalidate shader helper integration for later engine releases.\n\nThe shared native Alliance turret artwork is preserved. The master maps are 4096-square deliveries from 1254-square generated artwork with separately authored material maps. Published gallery photography remains pending approval.\n')
(A/'CHANGELOG.md').write_text('# Changelog\n\n## 1.1 — review\n\n'+summary+' Replaced the misplaced steady red hull lamp with scoped nozzle lighting and retained heat, plus damage-responsive cabin intensity. Preserved native geometry, UVs, turret assets and plumes. Refreshed all resolution tiers and verified the official engine response.\n\n## 1.0 — first review\n\nTwo restored hull atlases, structural materials, inset glazing, 65 primitive-continuation repairs, and preserved native turrets.\n')
(A/'CREDITS.md').write_text((W/'before/repository/CREDITS.md').read_text()+'\nRevision 1.1 uses built-in image editing for green glazing and the outlined, worn stencil, integrated through local masks in the existing Blender source. Lighting composition is adapted from OpenReliant 0.18.0 under MPL-2.0; LICENSE-OpenReliant.txt is included in the runtime.\n')
(A/'LICENSING.md').write_text((W/'before/repository/LICENSING.md').read_text()+'\nThe adapted OpenReliant lighting shader is MPL-2.0; see mods/117-prowler-worn-v1/LICENSE-OpenReliant.txt.\n')
p=A/'source/README.md';s=p.read_text().replace('prowler_worn_pbr_v1.blend','prowler_worn_pbr_v2.blend');s+='\nRevision 1.1: source/authoring/lighting_v2 records the local glass/stencil edits, native lamp change, nozzle geometry audit, runtime shaders and scripts, and functional validation. Earlier scenes and resources remain authoring history.\n';p.write_text(s)
# Exactly the repository runtime is installed, never the instrumented probe.
installed=G/'game-data/mods'/O.name
assert not {p.name for p in installed.iterdir()}-{p.name for p in (A/'mods'/O.name).iterdir()}
shutil.copytree(A/'mods'/O.name,installed,dirs_exist_ok=True)
shutil.copy2(A/'tools/launch-prowler-test.sh',G/'launch-prowler-test.sh');(G/'launch-prowler-test.sh').chmod(0o755)
subprocess.run(['bash','-n',str(G/'launch-prowler-test.sh')],check=True)
for p in (A/'mods'/O.name).iterdir():assert sha(p)==sha(installed/p.name)==sha(O/p.name)
assert not (installed/'test_runtime.luau').exists() and 'dt *=' not in (installed/'prowler_lighting.luau').read_text()
compat=dict(status='passed',asset_revision='1.1',checked_at_utc=now,engine='Official OpenReliant 0.18.0',shader_compiled_by_official_engine=True,response_unit_checks=36,runtime_integration='passed',runtime_probe_clock_acceleration=2,game_launched=True,runtime_visual_review='pending_user',component_inventory='one hull, four turrets, no separate engines',resolution_tiers=['1k','2k','4k'],geometry_uv_normals_preserved=True,nozzle_scope_all_40_part_lods=True,source_snapshot_reopened=True,installed_bytes_match_repository=True)
dump(W/'compatibility.json',compat);dump(A/'compatibility-0.18.json',compat)
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='revision-1.1-awaiting-user-review',ship='Prowler',asset_revision='1.1',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
validation=dict(compat,status='checks-passed-awaiting-user-review',user_approved=False,packaging_ready=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));dump(A/'validation.json',validation)
release=read(A/'release.json');release.update(asset_revision='1.1',status='held',user_approved=False,published=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));release['include_documents']=list(dict.fromkeys(release['include_documents']+['LIGHTING.md']));dump(A/'release.json',release)
state=read(D.parent/'project_state.json');state.update(status='ready_for_user_review',latest_scene=str(D/'prowler_worn_pbr_v2.blend'),upright_scene=str(D/'prowler_worn_pbr_v2.blend'),latest_deliverables=str(O.parent.parent),updated_at_utc=now,user_approved=False,published=False,dynamic_lighting='Throttle-responsive three-nozzle illumination, retained interior heat, damage-responsive green cabin lighting',engine_validation=dict(compat,evidence=str(W/'compatibility.json')),resolution_exports=[dict(tier=x['tier'],runtime=x['runtime']) for x in tiers['tiers']],deployment=dict(installed_mod=str(installed),launcher=str(G/'launch-prowler-test.sh'),verified=True,files=len(manifest)),progress=dict(texture_uv='localized_glass_and_stencil_revision_complete',pbr_authoring='structural_maps_preserved_new_emissive_tint',pbr_tuning='ready_for_user_review',engine_validation='official_engine_functional_and_all_resolution_checks_passed'))
dump(D.parent/'project_state.json',state)
m=read(D/'manifest.json');m.update(scene=rec(D/'prowler_worn_pbr_v2.blend',D),asset_revision='1.1',engine_validation=state['engine_validation'],progress=state['progress'],runtime_exports=manifest,resolution_exports=state['resolution_exports'],remaining=['User visual review and approval','Campaign, firing and distance checks','Publication and standard gallery photography after approval'])
for role in ['hull1','hull2']:
 for key in ['basecolor']+(['emissive'] if role=='hull1' else []):
  p=D/'maps'/f'prowler_{role}_{key}_v2.png';m['maps'][role][key]=dict(path=str(p),sha256=sha(p),dimensions=[4096,4096])
dump(D/'manifest.json',m)
(D/'README.md').write_text('# Prowler worn workspace\n\nRevision 1.1 ready for user review; not approved or published. Current scene: prowler_worn_pbr_v2.blend.\n\n'+summary+'\n\nRun '+str(G/'launch-prowler-test.sh')+'. F5 changes thrust; F6/F7 small/heavy hit; F8 restores armour; F9 toggles engine-disable. See LIGHTING.md for behaviour and verification. Original scenes, native files and revision-one exports are preserved.\n')
catalog=read(R/'catalog.json');entry=next(x for x in catalog['assets'] if x['id']=='prowler');assert entry['status']=='coming-soon';entry['description']='Worn Alliance escort-corvette restoration with subdued green windows, outlined unit stencil and responsive engine lighting. Revision 1.1 awaiting in-game review.';entry['liveries'][0]['notes']=['Revision 1.1 ready for review; no public download yet.','Muted green glazing, worn outlined AL-47 and nozzle-centred thrust/heat lighting.','Local 1K/2K/4K exports and official 0.18.0 functional checks passed.'];entry['liveries'][0]['engineStatus']='functional-checks-passed-review-pending';dump(R/'catalog.json',catalog)
subprocess.run(['python3',str(R/'tools/build_site.py')],cwd=R,check=True)
dump(W/'deployment.json',dict(verified=True,installed=str(installed),launcher=str(G/'launch-prowler-test.sh'),files=[rec(p,installed) for p in sorted(installed.iterdir())],updated_at_utc=now))
print('PROWLER_REVISION_1_1_INSTALLED',len(manifest),'exact repository files')
