import os
from pathlib import Path
import json,hashlib,shutil,datetime,subprocess,os,tempfile
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/corrections_v4';O=W/'runtime_stage/111-haidar-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Coalition Fighters/Haidar';G=Path('/home/lva-8700/Games/OpenReliant');E=G/'releases/openreliant-v0.8.1-linux-x86_64'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,x):write(p,json.dumps(x,indent=2)+'\n')
def hashes(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
v=json.loads((W/'validation.json').read_text());pres=json.loads((W/'native_preservation.json').read_text());mc=json.loads((W/'map_checks.json').read_text());checks=json.loads((W/'native_checks.json').read_text());snap=json.loads((W/'repository_snapshot.json').read_text());local=json.loads((W/'independent_checks.json').read_text())
assert pres['passed'] and mc['passed'] and local['passed'] and all(c['exit_code']==0 for c in checks)
assert snap['canonical_sha256']==v['scene_sha256']==sha(v['scene']) and snap['snapshot_sha256']==sha(A/'source/haidar_worn_pbr_v4.blend') and snap['packed_relative_resources_reopened']
probe=R/'.local/texture-variant-cleanup/texture-probe';probe_src=R/'tools/loadout-texture-probe/texture-probe.zig';log=Path('/tmp/haidar-v4-texture-probe.log').read_text();assert 'PASS orhd1_hull:' in log and 'PASS orhd4_local:' in log
assert sha(E/'openreliant')=='aa5e81293be85b28884460476427d0942556d6945b3e89da390365d480d9c5ea'
assert len(list(O.iterdir()))==11 and not any(p.name.startswith(('g-','r-','orhd2_')) for p in O.iterdir())
compat=dict(status='passed',scope='Official 0.8.1 native format and texture-loader checks; revised appearance awaiting user review',checked_at_utc=now,engine='Official OpenReliant 0.8.1 linux-x86_64',engine_sha256=sha(E/'openreliant'),engine_source_commit='b91c70bba414b2b2dc16bcf687647b41701deb8a',native_checks=checks,texture_loader=dict(output=log.strip(),probe_binary_sha256=sha(probe),probe_source_sha256=sha(probe_src),green_and_red_generated=True,normal_and_orm_inherited_byte_identically=True),duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility-0.8.json',compat)
for p in (D/'maps/corrections_v4').glob('*.png'):
 dest=A/'source/maps/corrections_v4'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
for p in W.iterdir():
 if not p.is_file() or p.suffix not in ['.py','.json','.txt']:continue
 text=p.read_text()
 for source,repl in [(str(D),'${HAIDAR_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(E/'sltool'),'${OPENRELIANT_SLTOOL}')]:text=text.replace(source,repl)
 if p.suffix=='.py':text='import os\n'+text.replace("D=Path(os.environ['HAIDAR_WORKSPACE'])","D=Path(os.environ['HAIDAR_WORKSPACE'])").replace("tool=os.environ['OPENRELIANT_SLTOOL']","tool=os.environ['OPENRELIANT_SLTOOL']")
 write(A/'source/authoring/corrections_v4'/p.name,text)
for p in (D/'review/corrections_v4').glob('*.png'):
 dest=A/'source/review/corrections_v4'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)

expected=hashes(W/'prior_runtime');canonical=D/'exports/openreliant_0_8_v1/mods'/O.name;repo=A/'mods'/O.name;installed=G/'game-data/mods'/O.name
for dest in [canonical,repo,installed]:assert hashes(dest)==expected,('Files changed during revision',str(dest))
runtime_hash=hashes(O)
for dest,backup in [(canonical,W/'prior_canonical_runtime'),(repo,W/'prior_repository_runtime'),(installed,G/'mod-backups/haidar-before-artwork-1.3')]:
 assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.haidar-v4-',dir=G if dest==installed else W) as tmp:
  stage=Path(tmp)/O.name;shutil.copytree(O,stage);assert hashes(stage)==runtime_hash;os.rename(dest,backup)
  try:os.rename(stage,dest)
  except BaseException:os.rename(backup,dest);raise
 assert hashes(dest)==runtime_hash

summary='Local shoulder and wing panel registration, removal of stray panel-gap segments, undivided front/rear canopy panes, two roof struts aligned to the side struts, removal of the stray nose-top gap, and a regular red/white hatch border with its central herringbone artwork preserved.'
write(A/'README.md',f'''# Haidar - Worn Paint

**Artwork 1.3 installed for review; not approved or published.** Targets official OpenReliant 0.8.1. Planned package 0.1.0-beta.1.

{summary}

Original worn artwork, lamps, vents and insignia are retained. The canopy frames have their own chamfer and gasket relief above flat inset green glass. The lower shoulder no longer wraps its border into an unrelated part of the atlas. A compact local material isolates repairs on seven faces so shared original artwork elsewhere is preserved. Geometry, native corner normals, attachments and animation are unchanged.

One unprefixed PNG set per material: the 4K hull and a 2K local repair atlas. OpenReliant generates loadout colours; no duplicate green/red files ship. Native, map, portable-source and exact-install checks passed. In-game appearance awaits review. Run tools/launch-haidar-test.sh as described in INSTALL.md.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- Artwork 1.3 awaits user in-game review; publication remains held.
- Campaign combat, damage, ejection, distance transitions and other platforms remain untested.
- The mesh and atlas were audited for panel joins on both sides, roof, belly and wings. Original intentional chart boundaries remain; this does not claim that every legacy texture boundary is invisible.
- The 4096-square hull derives from the 1254-square restoration. The 2048-square local material preserves sampled original artwork on seven faces, with narrowly masked corrections.
- Dedicated emissive maps remain deferred. Review views are Blender authoring renders, not game validation.
''')
changelog=A/'CHANGELOG.md';previous=changelog.read_text();write(changelog,'# Changelog\n\n## Unreleased 0.1.0-beta.1 - artwork 1.3\n\n'+summary+' Preserve original mesh and historical scenes.\n\n'+previous.removeprefix('# Changelog\n\n'))
write(A/'source/README.md','''# Haidar editable source

Current scene: haidar_worn_pbr_v4.blend (artwork 1.3; awaiting review). Earlier scenes, original inputs and UV layers remain as history. Artwork 1.1 remains rejected.

Haidar_Delivery_UV_v4 retains the existing layout with small local corner, central-body and wing registration corrections. Two nose faces, four lower-shoulder faces and one rear-roof triangle use a compact separate atlas, preserving sampled original artwork and fixtures. That isolation prevents local nose-gap removal from erasing valid panels that share the original texels. The lower shoulder strip is continued without the original V-coordinate wrap into unrelated artwork.

The roof has two metal struts calculated from the side struts along shared native vertices 28 and 31. Front/rear internal dividers are removed from colour, height and material masks. Frames have height +0.18; glass depth is -0.90 with a smooth 2.5-master-pixel chamfer and gasket. Pane interiors are flat and contain no painted reflections.

Generated paint repairs are composited only through the recorded thin-line and perimeter masks. Herringbone centre pixels are bit-identical. Original vertex coordinates, topology, native normals, hidden caps, part records and earlier UV layers are preserved. All current images are packed and also stored through relative resource paths; the snapshot was reopened and verified.

maps/corrections_v4 contains maps, references and masks. authoring/corrections_v4 contains the audit, build_revision.py, refine_review.py, repair_roof.py and final_panel.py, exact prompts and validation/export records. review/corrections_v4 contains supplied corrections and before/after authoring views. Treat the saved scene as authoritative; do not rerun recipes over later edits. In-game review remains pending.
''')
write(A/'source/authoring/README.md','# Haidar authoring history\n\nCurrent scene: ../haidar_worn_pbr_v4.blend. Current recipes, prompts and checks are in corrections_v4/. build_revision.py is followed by refine_review.py, repair_roof.py and final_panel.py for exact shared-edge frame alignment, the remaining shoulder line and matching rear-roof artwork. Earlier revisions are history; seams_v2 was rejected for broad reauthoring. Do not rerun old recipes over later manual edits.\n')
credits=A/'CREDITS.md';write(credits,credits.read_text()+'\nArtwork 1.3 uses tightly masked local paint repairs from the built-in image-generation tool. Exact prompts are in source/authoring/corrections_v4/image_generation_prompts.json; generated references are in source/maps/corrections_v4/. Original artwork outside the recorded masks is preserved.\n')
category=R/'Coalition Fighters/README.md';category.write_text(category.read_text().replace('Worn artwork 1.2 installed; awaiting user in-game review','Worn artwork 1.3 installed; awaiting user in-game review'))
manifest=[rec(p,A) for p in sorted(repo.rglob('*')) if p.is_file()];dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='revision-awaiting-user-review',ship='Haidar',asset_revision='1.3',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
dump(A/'compatibility-0.8.json',compat)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,asset_revision='1.3',engine_build=compat['engine'],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),user_approved=False,packaging_ready=False,checks=['Locality checks preserve original hull outside correction masks.','Central herringbone artwork byte-identical.','Native SHP/DTE and all 1349 face continuation checks passed.','Two roof struts follow shared-edge side positions; front/rear divider relief removed.','Flat recessed glass and separate frame relief verified.','Geometry, native normals and original inputs preserved.','Packed source reopened and repository/export/installation hashes matched.','Official loader generates loadout colours for both canonical material sets.'],game_launched=False,runtime_visual_review='pending_user');dump(A/'validation.json',validation)
release=json.loads((A/'release.json').read_text());release.update(asset_revision='1.3',status='held',hold_reason='Awaiting user review of local panel, canopy and caution-border corrections',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),user_approved=False,published=False);dump(A/'release.json',release)
launcher=G/'launch-haidar-test.sh';assert sha(launcher)==sha(A/'tools/launch-haidar-test.sh') and os.access(launcher,os.X_OK);subprocess.run(['bash','-n',str(launcher)],check=True)
for dest in [repo,canonical,installed]:assert hashes(dest)==runtime_hash
game_closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
deploy=dict(status='revision-installed-ready-for-review',installed_at_utc=now,asset_revision='1.3',installed_mod=str(installed),repository_asset=str(A),launcher=str(launcher),launcher_sha256=sha(launcher),runtime_files=manifest,exact_repository_bytes_verified=True,previous_runtime_backup=str(G/'mod-backups/haidar-before-artwork-1.3'),game_was_closed=game_closed,game_launched=False,runtime_visual_review='pending_user');dump(W/'deployment.json',deploy)
state=json.loads((D.parent/'project_state.json').read_text());state.update(status='ready_for_user_review',latest_scene=v['scene'],previous_scene=v['source'],latest_deliverables=str(canonical.parent.parent),asset_revision='1.3',updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='local_panel_shoulder_wing_nose_and_border_corrections_complete_pending_review',pbr_authoring='front_rear_dividers_removed_two_aligned_roof_struts_and_recessed_glass',pbr_tuning='both_sides_roof_belly_authoring_views_checked_runtime_pending',engine_validation='official_0_8_1_non_visual_checks_passed_runtime_pending'),engine_validation=dict(build=compat['engine'],date_utc=now,non_visual_checks='passed',visual_review='pending_user_revision_1_3',game_launched=False,evidence=str(W/'compatibility-0.8.json')),review_notes=[summary,'Original worn character and detailed fixtures retained.','User in-game review pending.'])
dump(D.parent/'project_state.json',state)
dump(D/'manifest.json',dict(ship='Haidar',variant='worn',asset_revision='1.3',status=state['status'],user_approved=False,published=False,scene=rec(Path(v['scene']),D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],maps=v['maps'],runtime_exports=manifest,review_evidence=str(D/'review/corrections_v4'),remaining=['User in-game review','Campaign, damage, animation, ejection and distance transitions','Dedicated emissive maps']))
write(D/'README.md',f'''# Haidar worn workspace

Artwork 1.3 installed for user review, not approved or published. Current scene: haidar_worn_pbr_v4.blend. {summary}

The original worn artwork and historical scenes remain. The roof struts match the side struts in native model coordinates; front/rear panes have no internal divider. Flat glass remains inset beneath separately authored frame relief. The 4K hull plus a compact 2K local repair atlas ship as canonical unprefixed PNG materials, with loadout colours generated by the engine.

Official 0.8.1 native/map/loader checks, source reopening and exact installation hashes passed. Revised runtime appearance awaits review. The game was not launched automatically.

Run {launcher}. Restart an already-open game to load the revision. Press 7 to orbit, arrows to rotate, Shift+Up/Down to zoom and 0 for a screenshot.

work/corrections_v4 records the audit, final refinement, prompt provenance and checks. maps/corrections_v4 stores the final maps and isolated repair references; review/corrections_v4 contains the corrections and authoring views. Earlier scenes and original inputs remain intact.
''')
write(canonical.parent.parent/'README.md','# Haidar OpenReliant 0.8.1 review export\n\nArtwork 1.3: local panel/caution-border repairs and corrected canopy struts. Canonical unprefixed hull and small local repair materials; no green/red duplicates. Awaiting review; the game was not launched. Use launch-haidar-test.sh for mission 975, ship 39.\n')
print(json.dumps(dict(status='ready_for_user_review',revision='1.3',files=len(manifest),bytes=sum(x['bytes'] for x in manifest),launcher=str(launcher),game_was_closed=game_closed),indent=2))
