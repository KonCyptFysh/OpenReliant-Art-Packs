import os
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,tempfile,os
D=Path(os.environ['GALAHAD_WORKSPACE']);W=D/'work/canopy_v2';O=D/'exports/openreliant_0_8_v1/mods/113-galahad-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Torpedo Bombers/Galahad';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.8.1-linux-x86_64'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
def sanitize(s):
 for a,b in [(str(D),'${GALAHAD_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(E/'sltool'),'${OPENRELIANT_SLTOOL}'),(str(G),'${OPENRELIANT_HOME}')]:s=s.replace(a,b)
 return s
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
old_manifest=json.loads((A/'asset-manifest.json').read_text());installed=G/'game-data/mods'/O.name
for x in old_manifest:assert sha(A/x['path'])==sha(installed/Path(x['path']).name)==x['sha256'],'Unexpected manual runtime change'
r=json.loads((W/'validation.json').read_text());rev=json.loads((W/'revision_checks.json').read_text());snapshot=json.loads((W/'repository_snapshot.json').read_text());checks=json.loads((W/'native_checks.json').read_text());maps=json.loads((W/'map_checks.json').read_text())
assert rev['passed'] and maps['passed'] and all(x['exit_code']==0 for x in checks) and snapshot['packed_relative_resources_reopened']
assert sha(Path(r['scene']))==r['scene_sha256']
log=Path('/tmp/galahad-canopy-v2-probe.log').read_text();assert log.startswith('PASS orgl1_hull:')
compat=json.loads((A/'compatibility-0.8.json').read_text());compat.update(checked_at_utc=now,native_checks=checks,asset_revision='1.1',runtime_visual_review='pending_user')
compat['texture_loader'].update(output=log.strip(),input_files=[rec(O/f'orgl1_hull{x}.png',O) for x in ('','_normal','_orm')]);assert sha(E/'openreliant')==compat['engine_sha256']
dump(W/'compatibility-0.8.json',compat)
if Path(__file__).resolve()!=(W/'finish.py').resolve():shutil.copy2(__file__,W/'finish.py')
# Add a complete new revision without destroying the first-pass authoring history.
for p in (D/'maps').glob('*v2.png'):shutil.copy2(p,A/'source/maps'/p.name)
dest=A/'source/authoring/canopy_v2';dest.mkdir(parents=True,exist_ok=True)
for p in W.iterdir():
 if not p.is_file():continue
 if p.suffix in ('.py','.json','.txt'):
  s=sanitize(p.read_text())
  if p.suffix=='.py' and "Path(os.environ['GALAHAD_WORKSPACE'])" in s:s='import os\n'+s.replace("Path(os.environ['GALAHAD_WORKSPACE'])","Path(os.environ['GALAHAD_WORKSPACE'])")
  (dest/p.name).write_text(s)
 else:shutil.copy2(p,dest/p.name)
shutil.copytree(D/'review/canopy_v2',A/'source/review/canopy_v2',dirs_exist_ok=True)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
note='''\n## Cockpit revision 1.1 - awaiting in-game review\n\nReplaces the blurry, oversized mottling immediately around the two cockpit panes with a localized high-resolution wear patch. Approximately 2.72% of base-colour pixels changed. Glass colour, the silver RAF crest and pixels outside the cockpit crop remain byte-identical. The original panel layout, native model and all four review missions are unchanged.\n\nThe side-pane gloss mask is now contained within the painted glass; its seal and metal rim have separate material response and the glass remains inset. Normal, roughness and metallic maps were refreshed locally. Both cockpit sides were checked in Blender. Official 0.8.1 native/map/texture-loader checks passed; in-game appearance is awaiting review.\n\nCurrent editable scene: `source/galahad_worn_pbr_v2.blend`. The first-pass scene remains available. Exact built-in image-generation prompt, bounded compositing mask, user screenshots and preservation checks are in `source/authoring/canopy_v2/`.\n'''
p=A/'README.md';p.write_text(p.read_text()+note)
p=A/'CHANGELOG.md';p.write_text(p.read_text()+'\n## Unreleased artwork 1.1\n\nLocalized cockpit wear cleanup and glass/frame material-mask repair. Original RAF crest, glass colour, native geometry, deployment and inspection missions preserved. Awaiting user review.\n')
p=A/'source/README.md';s=p.read_text().replace('`galahad_worn_pbr_v1.blend` is the current first-pass scene.','`galahad_worn_pbr_v2.blend` is the current revised scene; `galahad_worn_pbr_v1.blend` preserves the first pass.');p.write_text(s+'\nThe canopy_v2 revision inserts a generated detail crop only through a protected local mask. Its exact prompt, source crop and pixel-preservation checks are in `authoring/canopy_v2/`. The rest of the atlas is unchanged. `review/canopy_v2/` contains the current cockpit views.\n')
p=A/'KNOWN_ISSUES.md';p.write_text(p.read_text()+'\nThe latest cockpit revision uses a separate generated high-detail crop, applied at delivery resolution. Corner sheen still needs confirmation in the game under the user\'s lighting.\n')
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];assert len(manifest)==12;dump(A/'asset-manifest.json',manifest)
dump(A/'source-manifest.json',dict(status='revised-pass-awaiting-user-review',ship='Galahad',asset_revision='1.1',files=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()]))
dump(A/'compatibility-0.8.json',compat)
validation=json.loads((A/'validation.json').read_text());validation.update(checked_at_utc=now,asset_revision='1.1',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),cockpit_revision=rev,runtime_visual_review='pending_user');validation['checks']+=['Localized cockpit revision verified: glass colour, RAF crest, native model and review missions unchanged.','Updated glazing mask stays within painted glass; both cockpit sides inspected in Blender.'];dump(A/'validation.json',validation)
release=json.loads((A/'release.json').read_text());release.update(asset_revision='1.1',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));dump(A/'release.json',release)
# Replace only the verified Galahad folder; retain the prior installation for rollback.
game_closed=subprocess.run(['pgrep','-x','openreliant'],capture_output=True).returncode==1
backup=G/'mod-backups/113-galahad-worn-v1-before-canopy-v2';assert not backup.exists();backup.parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='.galahad-canopy-v2-',dir=G) as temp:
 staged=Path(temp)/O.name;shutil.copytree(A/'mods'/O.name,staged)
 for x in manifest:assert sha(staged/Path(x['path']).name)==x['sha256']
 installed.rename(backup)
 try:os.rename(staged,installed)
 except Exception:backup.rename(installed);raise
for x in manifest:assert sha(A/x['path'])==sha(installed/Path(x['path']).name)==x['sha256']
dump(W/'deployment.json',dict(installed_at_utc=now,asset_revision='1.1',exact_repository_bytes_verified=True,installed_mod=str(installed),previous_install_backup=str(backup),game_was_closed=game_closed,game_launched=False,runtime_visual_review='pending_user',launcher=str(G/'launch-galahad-test.sh'),files=manifest))
p=D.parent/'project_state.json';state=json.loads(p.read_text());state.update(latest_scene=r['scene'],status='ready_for_user_review',asset_revision='1.1',updated_at_utc=now,current_review=str(D/'review/canopy_v2'));state['progress'].update(texture_uv='localized_cockpit_wear_revision_complete',pbr_authoring='cockpit_glazing_masks_refined',pbr_tuning='both_cockpit_sides_reviewed_runtime_pending');state['engine_validation'].update(date_utc=now,evidence=str(W/'compatibility-0.8.json'));state['last_revision']=dict(name='canopy_v2',evidence=str(W/'revision_checks.json'),user_visual_review='pending');dump(p,state)
p=D/'manifest.json';m=json.loads(p.read_text());m.update(asset_revision='1.1',scene=rec(Path(r['scene']),D),maps=r['maps'],runtime_exports=manifest,progress=state['progress'],engine_validation=state['engine_validation'],review_evidence=str(D/'review/canopy_v2'),cockpit_revision=rev);dump(p,m)
p=D/'README.md';p.write_text(p.read_text().replace('Current scene: `galahad_worn_pbr_v1.blend`','Current scene: `galahad_worn_pbr_v2.blend`')+'\nCurrent revision: canopy_v2 / artwork 1.1. Blurry cockpit mottling replaced locally; glass/metal reflection mask corrected. Original scene and runtime are retained in the v1 scene and `history/first_pass_runtime/`. Exact prompt: `work/canopy_v2/imagegen_prompt.json`; current review images: `review/canopy_v2/`. Installed for user review; no publication.\n')
print(json.dumps(dict(status='revised-pass-installed',asset_revision='1.1',runtime_files=len(manifest),runtime_bytes=sum(x['bytes'] for x in manifest),scene=r['scene'],game_was_closed=game_closed,launcher=state['review_launcher'],visual_review='pending'),indent=2))
