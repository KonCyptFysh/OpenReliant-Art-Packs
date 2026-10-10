import os
from pathlib import Path
import json,hashlib,shutil,datetime,subprocess,os,tempfile
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/alignment_v3';O=W/'runtime_stage/111-haidar-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Coalition Fighters/Haidar';G=Path('/home/lva-8700/Games/OpenReliant');E=G/'releases/openreliant-v0.8.1-linux-x86_64'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def dump(p,x):write(p,json.dumps(x,indent=2)+'\n')
def hashes(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
v=json.loads((W/'validation.json').read_text());pres=json.loads((W/'native_preservation.json').read_text());mc=json.loads((W/'map_checks.json').read_text());checks=json.loads((W/'native_checks.json').read_text());snap=json.loads((W/'repository_snapshot.json').read_text());local=json.loads((W/'independent_checks.json').read_text())
assert pres['passed'] and mc['passed'] and local['passed'] and all(c['exit_code']==0 for c in checks)
assert snap['canonical_sha256']==v['scene_sha256']==sha(v['scene']) and snap['snapshot_sha256']==sha(A/'source/haidar_worn_pbr_v3.blend') and snap['packed_relative_resources_reopened']
probe=R/'.local/texture-variant-cleanup/texture-probe';probe_src=R/'tools/loadout-texture-probe/texture-probe.zig';log=Path('/tmp/haidar-v3-texture-probe.log').read_text();assert 'PASS orhd1_hull:' in log
assert sha(E/'openreliant')=='aa5e81293be85b28884460476427d0942556d6945b3e89da390365d480d9c5ea'
assert len(list(O.iterdir()))==8 and not any(p.name.startswith(('g-','r-','orhd2_')) for p in O.iterdir())
compat=dict(status='passed',scope='Official 0.8.1 native format and texture-loader checks; revised appearance awaiting user review',checked_at_utc=now,engine='Official OpenReliant 0.8.1 linux-x86_64',engine_sha256=sha(E/'openreliant'),engine_source_commit='b91c70bba414b2b2dc16bcf687647b41701deb8a',native_checks=checks,texture_loader=dict(output=log.strip(),probe_binary_sha256=sha(probe),probe_source_sha256=sha(probe_src),green_and_red_generated=True,normal_and_orm_inherited_byte_identically=True),duplicated_colour_textures=False,game_launched=False,runtime_visual_review='pending_user')
dump(W/'compatibility-0.8.json',compat)
for p in (D/'maps/alignment_v3').glob('*.png'):
 dest=A/'source/maps/alignment_v3'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
for p in W.iterdir():
 if not p.is_file() or p.suffix not in ['.py','.json','.txt']:continue
 text=p.read_text()
 for source,repl in [(str(D),'${HAIDAR_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(E/'sltool'),'${OPENRELIANT_SLTOOL}')]:text=text.replace(source,repl)
 if p.suffix=='.py':text='import os\n'+text.replace("D=Path(os.environ['HAIDAR_WORKSPACE'])","D=Path(os.environ['HAIDAR_WORKSPACE'])").replace("tool=os.environ['OPENRELIANT_SLTOOL']","tool=os.environ['OPENRELIANT_SLTOOL']")
 write(A/'source/authoring/alignment_v3'/p.name,text)
for p in (D/'review/alignment_v3').glob('*.png'):
 dest=A/'source/review/alignment_v3'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)

# Replace complete folders so the rejected repair material cannot linger.
expected=hashes(W/'prior_runtime');canonical=D/'exports/openreliant_0_8_v1/mods'/O.name;repo=A/'mods'/O.name;installed=G/'game-data/mods'/O.name
for dest in [canonical,repo,installed]:assert hashes(dest)==expected,('Files changed during revision',str(dest))
runtime_hash=hashes(O)
for dest,backup in [(canonical,W/'rejected_canonical_runtime'),(repo,W/'rejected_repository_runtime'),(installed,G/'mod-backups/haidar-before-artwork-1.2')]:
 assert not backup.exists();backup.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.haidar-v3-',dir=G if dest==installed else W) as tmp:
  stage=Path(tmp)/O.name;shutil.copytree(O,stage);assert hashes(stage)==runtime_hash
  os.rename(dest,backup)
  try:os.rename(stage,dest)
  except BaseException:os.rename(backup,dest);raise
 assert hashes(dest)==runtime_hash

write(A/'README.md','''# Haidar - Worn Paint

**Artwork 1.2 installed for review; not approved or published.** Targets official OpenReliant 0.8.1. Planned package 0.1.0-beta.1.

Restores the original detailed nose and forward-body artwork after the rejected broad replacement in artwork 1.1. The original texture charts and material are restored on all 51 affected faces. Small shoulder-band coordinate adjustments align the existing artwork across adjacent surfaces.

Window frames follow the original divider locations with newly finished worn metal, a dedicated chamfer and gasket height profile, and flat inset dark green glass. Pane interiors have no painted reflections. Geometry, native normals, attachments and animation remain unchanged.

One unprefixed PNG hull material set; OpenReliant generates the loadout colours. The rejected extra repair atlas is removed from the current package and preserved in authoring history. Native, map, portable-source and exact-install checks passed; revised in-game appearance awaits user review. Run `tools/launch-haidar-test.sh` as described in INSTALL.md.
''')
write(A/'KNOWN_ISSUES.md','''# Remaining review

- Revised appearance awaits user in-game review. Publication remains held.
- Campaign combat, damage, ejection, distance transitions and other platforms remain untested.
- The correction preserves original UV charts. It aligns the existing shoulder bands; it does not claim that every original chart boundary is now seamless.
- The 4096-square hull delivery is based on the 1254-square restoration of the original 256-square atlas. Only window-frame finish and its structural maps were reauthored in this revision.
- Dedicated emissive maps remain deferred. Preview images are Blender authoring renders, not in-game validation.
''')
write(A/'CHANGELOG.md','''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.2

Restore original nose and forward-body detail and remove the rejected extra repair material. Align existing shoulder-band UV coordinates locally. Restore internal canopy dividers at their original positions with a new metal finish, dedicated chamfer/gasket normals and flat recessed glass. Preserve immutable source files and both earlier scenes.

## Artwork 1.1 - rejected

Removed internal window dividers and replaced broad nose/shoulder regions with a new projected material. User rejected the loss of original artwork and requested the frames back. Preserved as history only.

## Artwork 1.0

Initial worn restoration, structural normal/material maps, native continuity checks and quiet inspection mission.
''')
write(A/'source/README.md','''# Haidar editable source

Current scene: `haidar_worn_pbr_v3.blend` (artwork 1.2; awaiting review). Both earlier scenes and their maps remain as history. Artwork 1.1 is rejected and is not the current design.

The latest scene was opened and its 51 replacement-material faces restored to the preserved original UV charts and hull material. `Haidar_Delivery_UV_v3` makes only small shoulder-band alignment edits. Earlier UV layers, original vertex coordinates, triangle topology, native corner normals, transforms, hidden caps and part records are unchanged.

`maps/alignment_v3/` contains the framed-window maps and masks. The built-in image-generation tool supplied the local metal-frame finish; only narrow internal divider pixels were used. All other generated image changes are excluded. A separately authored analytic height profile raises the metal rim to 0.18 and recesses the pane to -0.90 in authoring units, with a smooth 2.5-pixel chamfer and dark gasket. Pane interiors remain flat. `authoring/alignment_v3/` records the layout, provenance, local UV changes, preservation checks and native export. `review/alignment_v3/` has both-side and close canopy authoring views.

All current scene images are packed and also referenced through relative resources paths. The snapshot was reopened and verified. The source is a static assembled authoring pose; native animation and attachment bytes are preserved in the export. In-game review remains pending.
''')
write(A/'source/authoring/README.md','# Haidar authoring history\n\nCurrent scene: ../haidar_worn_pbr_v3.blend. Current recipes and checks are in alignment_v3/. The seams_v2/ revision was rejected for broad reauthoring; retain it only as history. First-pass recipes remain at this level. Do not rerun old recipes over later manual edits.\n')
write(A/'source/authoring/alignment_v3/README.md','''# Local restoration and framed glazing

`build_revision.py` opens the previous scene recorded in prior_project_state.json, retains all existing mesh data and UV layers, restores original material/chart assignments, and creates a separate delivery layer for small band-registration fixes. It uses the generated frame reference only on traced internal dividers and independently bakes structural height, normal and material masks. The original hull artwork is preserved outside the window footprints.

The authoritative saved result is ../../haidar_worn_pbr_v3.blend. Do not rerun recipes over later manual edits. Set HAIDAR_WORKSPACE, ART_PACK_REPOSITORY and OPENRELIANT_SLTOOL for the export and snapshot helpers. Validation.json, independent_checks.json, native_preservation.json and repository_snapshot.json record exact outputs. Prompt and image provenance are in imagegen_prompts.json. Rejected runtime files remain archived in the canonical workspace and installation backups.
''')
write(A/'CREDITS.md','''# Credits

Restoration contributions by KonCyptFysh. Original StarLancer artwork, models and game assets remain the property of their respective rights holders; original game data is required. OpenReliant provides the runtime and validation tools.

The initial atlas and local window-frame finish used the built-in image-generation tool. Prompts and provenance are in source/authoring/imagegen_prompts.json and source/authoring/alignment_v3/imagegen_prompts.json. UV alignment, structural height/normal baking and native preservation checks are recorded separately. The rejected Naginata-derived repair material remains in historical source only.
''')
category=R/'Coalition Fighters/README.md';category.write_text(category.read_text().replace('Worn artwork 1.1 installed; awaiting user in-game review','Worn artwork 1.2 installed; awaiting user in-game review'))
manifest=[rec(p,A) for p in sorted(repo.rglob('*')) if p.is_file()];dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='revision-awaiting-user-review',ship='Haidar',asset_revision='1.2',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
dump(A/'compatibility-0.8.json',compat)
validation=dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,asset_revision='1.2',engine_build=compat['engine'],asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),user_approved=False,packaging_ready=False,checks=['Original detailed artwork/material restored on all 51 rejected faces.','Local existing shoulder-band UV registration only; no replacement panel layout.','Native SHP/DTE checks and all 1349 face continuations passed.','Frame relief present; inset pane interiors flat; original geometry and native normals retained.','Unrelated hull pixels preserved; independent locality and mirror checks passed.','Packed source reopened and exact repository/export/installation hashes matched.','Official loader generated both loadout colours from one unprefixed material set.'],game_launched=False,runtime_visual_review='pending_user')
dump(A/'validation.json',validation)
release=json.loads((A/'release.json').read_text());release.update(asset_revision='1.2',status='held',hold_reason='Awaiting user review of restored original hull and reframed canopy',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),user_approved=False,published=False);dump(A/'release.json',release)
launcher=G/'launch-haidar-test.sh';assert sha(launcher)==sha(A/'tools/launch-haidar-test.sh') and os.access(launcher,os.X_OK);subprocess.run(['bash','-n',str(launcher)],check=True)
for dest in [repo,canonical,installed]:assert hashes(dest)==runtime_hash
game_closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
deploy=dict(status='revision-installed-ready-for-review',installed_at_utc=now,asset_revision='1.2',installed_mod=str(installed),repository_asset=str(A),launcher=str(launcher),launcher_sha256=sha(launcher),runtime_files=manifest,exact_repository_bytes_verified=True,previous_runtime_backup=str(G/'mod-backups/haidar-before-artwork-1.2'),game_was_closed=game_closed,game_launched=False,runtime_visual_review='pending_user');dump(W/'deployment.json',deploy)
state=json.loads((D.parent/'project_state.json').read_text());state.update(status='ready_for_user_review',latest_scene=v['scene'],previous_scene=str(D/'haidar_worn_pbr_v2.blend'),latest_deliverables=str(canonical.parent.parent),asset_revision='1.2',updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='original_artwork_restored_local_shoulder_alignment_pending_review',pbr_authoring='new_frames_with_independent_relief_and_recessed_flat_glass_complete',pbr_tuning='both_side_authoring_previews_checked_runtime_pending',engine_validation='official_0_8_1_non_visual_checks_passed_runtime_pending'),engine_validation=dict(build=compat['engine'],date_utc=now,non_visual_checks='passed',visual_review='pending_user_revision_1_2',game_launched=False,evidence=str(W/'compatibility-0.8.json')),review_notes=['Restore original nose and forward-body artwork; broad repaint rejected.','Local alignment of existing artwork only.','Restore original divider locations with improved metal frames and independent relief.','Flat glass inset below frames; remove baked pane reflections.'],rejected_revision=dict(scene=str(D/'haidar_worn_pbr_v2.blend'),reason='Broad nose/shoulder reauthoring removed original artwork; window dividers removed contrary to revised preference.'))
dump(D.parent/'project_state.json',state)
dump(D/'manifest.json',dict(ship='Haidar',variant='worn',asset_revision='1.2',status=state['status'],user_approved=False,published=False,scene=rec(Path(v['scene']),D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],maps=v['maps'],runtime_exports=manifest,review_evidence=str(D/'review/alignment_v3'),remaining=['User in-game review','Campaign, damage, animation, ejection and distance transitions','Dedicated emissive maps']))
write(D/'README.md',f'''# Haidar worn workspace

Artwork 1.2 installed for user review, not approved or published. Current scene: haidar_worn_pbr_v3.blend. The original detailed hull artwork is restored; the rejected broad artwork 1.1 remains as history. Small UV edits register existing shoulder bands. Newly finished window dividers follow their old positions and have independent chamfer/gasket relief above flat recessed green glass.

Original geometry, native normals, UV history, attachments and animation are preserved. Official 0.8.1 native/map/loader checks, packed-source reopening and exact installation hashes passed. Revised runtime appearance awaits review. The game was not launched automatically.

Run {launcher}. Restart an already-open game to load the new maps. Press 7 to orbit, arrows to rotate, Shift+Up/Down to zoom and 0 for a screenshot.

work/alignment_v3 records the layout and checks; maps/alignment_v3 stores maps and the local generated frame reference; review/alignment_v3 contains authoring views. Complete frame prompt provenance: work/alignment_v3/imagegen_prompts.json. Earlier revisions and original inputs remain intact.
''')
write(canonical.parent.parent/'README.md','# Haidar OpenReliant 0.8.1 review export\n\nArtwork 1.2: restored original hull, local shoulder-band registration and reframed inset canopy glazing. One unprefixed hull material set. Awaiting user review; the game was not automatically launched. Run launch-haidar-test.sh for mission 975 and ship 39.\n')
print(json.dumps(dict(status='ready_for_user_review',revision='1.2',files=len(manifest),bytes=sum(x['bytes'] for x in manifest),launcher=str(launcher),game_was_closed=game_closed),indent=2))
