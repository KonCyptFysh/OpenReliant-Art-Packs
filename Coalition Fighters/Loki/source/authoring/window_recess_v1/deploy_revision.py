from pathlib import Path
import json,hashlib,shutil,datetime,subprocess,re,ast
D=Path(str(Path(os.environ['LOKI_WORKSPACE'])));W=D/'work/window_recess_v1';P=D/'work/reconstruction_v1';R=Path(str(Path(os.environ['ART_PACKS_REPOSITORY'])));A=R/'Coalition Fighters/Loki';G=Path(str(Path(os.environ['OPENRELIANT_HOME'])));MOD='105-loki-worn-v1';O=D/'exports/openreliant_v1/mods'/MOD;dest=G/'game-data/mods'/MOD
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
r=read(W/'validation.json');old=read(W/'before/validation.json');snap=read(W/'repository_snapshot.json');anim=read(W/'source_animation_check.json');assert anim['passed']
assert sha(r['scene'])==r['scene_sha256']==snap['canonical_sha256'];assert sha(snap['snapshot'])==snap['snapshot_sha256']
prior_assets=read(A/'asset-manifest.json');(W/'before/asset-manifest.json').write_text((A/'asset-manifest.json').read_text())
for rec in prior_assets:
 assert sha(A/rec['path'])==rec['sha256'] and sha(dest/Path(rec['path']).name)==rec['sha256']
for key,rec in old['maps']['hull'].items():
 if key not in ('normal','height'):assert r['maps']['hull'][key]==rec and sha(rec['path'])==rec['sha256']
for prefix in ['orlk1','gorlk1']:shutil.copy2(r['maps']['hull']['normal']['path'],O/(prefix+'_hull_normal.png'))
for key in ['normal','height','window_recess_mask']:
 rec=r['maps']['hull'][key];shutil.copy2(rec['path'],A/'source/maps'/Path(rec['path']).name)
# Only the two normal-map variants change in the runtime mod.
changed=[]
for rec in prior_assets:
 name=Path(rec['path']).name;p=O/name
 if sha(p)!=rec['sha256']:
  assert name in ['orlk1_hull_normal.png','gorlk1_hull_normal.png'];changed.append(name);shutil.copy2(p,A/rec['path'])
assert sorted(changed)==['gorlk1_hull_normal.png','orlk1_hull_normal.png']
check=read(P/'map_checks.json');check.pop('flat_graphics_and_glass_normals',None);check.update(flat_glass_interiors=True,recessed_window_bevels=True,unrelated_normal_texels_unchanged=True,normal_max_unit_error=read(W/'recess-regions.json')['normal_max_unit_error'],normal_sha256=r['maps']['hull']['normal']['sha256'],flight_and_loadout_maps_identical=True)
write(W/'map_checks.json',check)
# The SHP, base colour, material maps, missions and launchers remain byte-identical.
assert sha(O/'CRP_Loki.SHP')==read(P/'native_preservation.json')['output_sha256']
map_names=['orlk1_hull_normal.png','gorlk1_hull_normal.png'];assert sha(O/map_names[0])==sha(O/map_names[1])
S=A/'source/authoring/window_recess_v1';S.mkdir(exist_ok=True);V=A/'source/review/window_recess_v1';V.mkdir(exist_ok=True)
roots=[(str(D),'LOKI_WORKSPACE'),(str(R),'ART_PACKS_REPOSITORY'),(str(G),'OPENRELIANT_HOME')]
def cleantext(s):
 for root,key in roots:s=s.replace(root,'$'+key)
 return s
for p in W.iterdir():
 if p.is_file() and p.name!='user-window-feedback.png':
  q=S/p.name;shutil.copy2(p,q)
  if q.suffix in ('.py','.json','.txt'):
   s=q.read_text()
   if q.suffix=='.py':
    def repl(m):
     value=m.group(2)
     for root,key in roots:
      if value==root or value.startswith(root+'/'):
       suffix=value[len(root):].lstrip('/');return "str(Path(os.environ["+repr(key)+"])"+(" / "+repr(suffix) if suffix else '')+")"
     return m.group(0)
    s=re.sub(r"(['\"])(/[^'\"\n]+)\1",repl,s)
    if 'os.environ' in s and 'import os' not in s:s='import os\n'+s
    # A user review screenshot is local evidence, never an authoring dependency for the portable recipe.
    s='\n'.join(line for line in s.split('\n') if not line.startswith("shutil.copy2('/tmp/codex-clipboard-"))
   q.write_text(cleantext(s))
for p in (D/'review/window_recess_v1').glob('*.png'):shutil.copy2(p,V/p.name)
(A/'README.md').write_text((A/'README.md').read_text().replace('First worn pass prepared for local review. Artwork is not approved or published.','Artwork 1.1 is installed for review after the first in-game feedback. The window surrounds now have inward bevel normals so the amber panes sit below the frame; glass interiors stay flat. Awaiting review of this correction.').replace('Painted graphics and glass retain flat normals.','Painted graphics and glass interiors retain flat normals; the window surrounds slope inward.'))
p=A/'CHANGELOG.md';p.write_text(p.read_text().replace('# Changelog\n','# Changelog\n\n## Artwork 1.1 - recessed windows, awaiting review\n\n- Added shallow inward normal-map bevels around the four existing window islands, keeping glass interiors flat.\n- Preserved the original window outlines, paint, roughness, metallic response, UVs, geometry and native animations.\n- Only the flight and loadout normal maps changed in the runtime mod.\n'))
p=A/'KNOWN_ISSUES.md';p.write_text(p.read_text().replace('- User in-game visual review and material tuning are pending. Not approved for beta publication.','- User reviewed the first pass in game and requested recessed window shading. Artwork 1.1 addresses that revision; its in-game appearance remains pending review.'))
p=A/'source/README.md';p.write_text(p.read_text()+'\nArtwork 1.1 continues from this same scene. Current revision evidence and recipe: `authoring/window_recess_v1/`. The initial `authoring/` records are retained as history. New normal/height maps end in `_v1_1`; window interiors sit at a negative height beneath a smooth inward bevel. Every normal texel outside the window band is preserved. The mesh, original vertex normals, UVs, materials and animation poses were checked unchanged.\n')
def inventory(root):return [dict(path=p.relative_to(A).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(root.rglob('*')) if p.is_file()]
write(A/'asset-manifest.json',inventory(A/'mods'));write(A/'source-manifest.json',dict(status='working-snapshot-awaiting-review',ship='Loki',asset_revision='1.1',files=inventory(A/'source')))
now=datetime.datetime.now(datetime.timezone.utc).isoformat();v=read(A/'validation.json');v.update(asset_revision='1.1',checked_at_utc=now,map_checks=check,portable_animation_poses_verified=anim,window_recess=r['window_recess'],source_snapshot_verified=True,runtime_visual_review='window_revision_pending_user_review',user_feedback='First in-game pass: windows looked proud of the hull; requested normal-map recess.',runtime_files_changed=changed,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));write(A/'validation.json',v)
p=A/'release.json';j=read(p);j.update(asset_revision='1.1',asset_manifest_sha256=v['asset_manifest_sha256'],source_manifest_sha256=v['source_manifest_sha256'],status='hold',hold_reason='Awaiting in-game review of recessed-window correction.');write(p,j)
for name in changed:shutil.copy2(A/'mods'/MOD/name,dest/name)
for rec in read(A/'asset-manifest.json'):assert sha(dest/Path(rec['path']).name)==rec['sha256']
for p in (A/'tools').glob('*.sh'):assert sha(p)==sha(G/p.name)
for p in S.glob('*.py'):ast.parse(p.read_text())
deploy=read(P/'deployment.json');deploy.update(date_utc=now,asset_revision='1.1',asset_manifest_sha256=v['asset_manifest_sha256'],runtime_files_changed=changed,all_files_match=True,user_review='window_revision_pending');write(W/'deployment.json',deploy)
state=read(D.parent/'project_state.json');state.update(asset_revision='1.1',latest_pass='window_recess_v1',maps=r['maps'],status='window_recess_revision_ready_for_review',deployment=deploy,runtime_visual_review='window_revision_pending_user_review',user_feedback=v['user_feedback'],updated_at_utc=now);state['progress'].update(texture_uv='first_game_review_received_original_art_and_uvs_preserved',pbr_authoring='window_recess_normal_revision_complete',pbr_tuning='recess_bevel_checked_in_Blender_pending_game_review',engine_validation='native_format_unchanged_and_verified_revision_deployed')
write(D.parent/'project_state.json',state);write(D/'manifest.json',state)
(D/'README.md').write_text((A/'README.md').read_text()+'\nCanonical scene: `loki_worn_pbr_v1.blend`. Current pass: `work/window_recess_v1`. Launcher: `$OPENRELIANT_HOME/launch-loki-test.sh`. Official OpenReliant 0.7.0 is the satisfied PBR baseline; new in-game review is pending.\n')
print(json.dumps(dict(revision='1.1',runtime_files_changed=changed,all_other_runtime_files_unchanged=True,exact_repository_copy_deployed=True,publication='held'),indent=2))
