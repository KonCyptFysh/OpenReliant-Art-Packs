from pathlib import Path
import json,hashlib,datetime,shutil,tempfile,os,subprocess
D=Path('${KURGEN_WORKSPACE}');W=D/'work/window_scope_v3';M=D/'maps/window_scope_v3';O=D/'exports/openreliant_0_8_v3/mods/116-kurgen-worn-v1'
R=Path('${ART_PACK_REPOSITORY}');A=R/'Corvettes and Gunboats/Kurgen';G=Path('${OPENRELIANT_HOME}');I=G/'game-data/mods'/O.name
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def rec(p,root):return dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p))
v=read(W/'validation.json');maps=read(W/'map_checks.json');native=read(W/'native_checks.json');pres=read(W/'native_preservation.json');surface=read(W/'emission_surface_audit.json');snap=read(W/'repository_snapshot.json')
assert maps['passed'] and len(maps['materials'])==3 and pres['passed'] and surface['passed'] and snap['packed_relative_resources_reopened'] and all(q['exit_code']==0 for q in native)
assert len(pres['window_faces_remapped'])==18 and sha(v['scene'])==v['scene_sha256']
prior=read(A/'asset-manifest.json')
for q in prior:assert sha(I/Path(q['path']).name)==q['sha256']
if not (W/'installed_before_v3').exists():shutil.copytree(I,W/'installed_before_v3')
for p in ['README.md','KNOWN_ISSUES.md','CHANGELOG.md','release.json','validation.json','asset-manifest.json','source-manifest.json']:
 dest=W/'prior_repository_metadata'/p;dest.parent.mkdir(exist_ok=True)
 if not dest.exists():shutil.copy2(A/p,dest)
dump(W/'authoring_review.json',dict(reviewed_at_utc=now,kind='Blender authoring views, not game captures',views=['front','opposite','belly','rear','emissive_dark'],observations=['Original long vent artwork restored on nose top and both sides.','Lengthwise vent-rib relief replaces the mistaken window mullions.','Only the highlighted bridge front and side sections remain windows.','Reused rear strip and under-turret hardware restored to original unlit appearance.','Emission surfaces traced on the exported mesh at every detail level; four coarse side faces corrected.'],runtime_visual_review='pending_user'))
compat=dict(status='passed',checked_at_utc=now,scope='Native formats, texture loader, material maps and native surface-placement checks',minimum_engine='0.8.1',review_engine='Official OpenReliant 0.18.0',native_checks=native,texture_loader=maps['emissive_loader'],surface_scope_audit='source/authoring/window_scope_v3/emission_surface_audit.json',game_launched=False,runtime_visual_review='pending_user_revision_1_2')
dump(W/'compatibility.json',compat);dump(A/'compatibility-0.8.json',compat)
shutil.copytree(O,A/'mods'/O.name,dirs_exist_ok=True)
shutil.copytree(M,A/'source/maps/window_scope_v3',dirs_exist_ok=True)
shutil.copytree(D/'review/window_scope_v3',A/'source/review/window_scope_v3',dirs_exist_ok=True)
readme='''# Kurgen - Worn Paint

**Correction 1.2 installed for review; unpublished.** Planned beta 0.1.0-beta.1. Pack baseline OpenReliant 0.8.1; local review uses official 0.18.0.

Windows are limited to the user-highlighted bridge front and side sections. The long nose-top and side strips are restored to their accepted original vent artwork, with recessed channels and lengthwise rib normals. Unmarked amber hardware behind the bridge and beneath the rear turret is restored and non-emissive. The stronger hull panel and machinery relief is retained; painted stars and caution graphics remain flat.

Front and rear shoulder faces originally reused the same texture patch. A dedicated 512-square front-window crop now separates them. Four lower-detail side faces also needed a 256-by-1024 crop to prevent their windows stretching onto the rear platform. These small crops preserve the existing texture density without duplicating the 4K hull atlas.

Fourteen front-window faces and four coarse side faces have isolated material/UV mappings. Geometry, original mesh normals, collision, attachments, turret animations and all six detail levels are retained. The first pass's native seam repairs remain, with two additional primitive-continuation splits at the new material boundary. The shared small turret is unchanged by this correction; it still affects other ships using that component. DAM_1 remains original.

Native checks pass on official 0.8.1 and 0.18.0. Emissive loading, normal/ORM maps, restored pixels, native emission placement across all detail levels, packed source and installed hashes are checked. Both sides, rear, belly and a dark authoring view were inspected in Blender. In-game review of this correction is pending.
'''
(A/'README.md').write_text(readme)
(A/'KNOWN_ISSUES.md').write_text('''# Remaining review

- Correction 1.2 awaits in-game user review on official 0.18.0. Blender views are authoring evidence, not engine captures.
- MATERIALS must be enabled for material maps. Loadout colour previews intentionally omit emission; inspect in flight.
- Emission is restricted to the highlighted bridge windows. It does not add point lights or change global shaders/bloom.
- Full campaign, damage, turret tracking/firing and detail transitions need gameplay review. Native records and all six detail levels are retained, with targeted window mappings on eighteen faces.
- The shared small turret remains at its first-pass treatment. The global damage texture remains original.
- Hull and turret maps are 4096 square; isolated window crops are 512 square and 256 by 1024. Original generated artwork and all earlier revisions are preserved.
- Publication requires fresh standard official-engine gallery photography after approval.
''')
ch=A/'CHANGELOG.md';ch.write_text('''# Changelog

## Unreleased 0.1.0-beta.1 - artwork 1.2

Restrict windows to the user-marked bridge sections. Restore nose and side vents, rear shared strips and under-turret hardware to original artwork with no emission. Add longitudinal vent relief. Isolate front/rear shared UVs and correct four distance-model faces that extended the side windows onto the rear platform. Native geometry and gameplay data retained. Review pending.

'''+ch.read_text().replace('# Changelog\n\n','',1))
(A/'source/README.md').write_text('''# Kurgen editable source

Continue from **kurgen_worn_pbr_v3.blend**. It contains the corrected window scope and restored vents. Earlier v1 and v2 scenes are historical snapshots; do not rebuild over the latest scene from an earlier recipe.

Geometry, custom mesh normals, mounts and original UV layers are preserved. The added Kurgen_Front_Bridge_UV_v3 layer maps only four finest-detail front faces to a 512-square crop. Native exports apply matching isolation to the lower-detail front faces, plus a separate small crop for four coarsened side faces. The Blender scene displays the finest-detail model; the distance-model crop is retained under maps/window_scope_v3 with its native mapping evidence.

maps/window_scope_v3 holds current hull, bridge and bridge-LOD maps and semantic masks. authoring/window_scope_v3 records exact selected faces, native preservation, emission-surface placement, validation and restoration recipes. These document the sequence rather than forming a one-command portable rebuild. Start future work from the latest scene and project state. The prior generated window art is reused only in the explicitly approved sections; no new artwork generation was used for this correction.

Packed images and relative resources were reopened and verified. review/window_scope_v3 contains authoring views, not public gallery photos. Original models, atlases and earlier revisions remain preserved.
''')
(D/'README.md').write_text(readme+'\nCurrent editable scene: kurgen_worn_pbr_v3.blend. Review launcher: '+str(G/'launch-kurgen-test.sh')+'. Restart any running game, press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom.\n')
# Stage repository bytes, then replace only this installed review mod; retain rollback.
manifest=[rec(p,A) for p in sorted((A/'mods').rglob('*')) if p.is_file()];dump(A/'asset-manifest.json',manifest)
with tempfile.TemporaryDirectory(prefix='.kurgen-v3-install-',dir=G) as temp:
 temp=Path(temp);stage=temp/O.name;shutil.copytree(A/'mods'/O.name,stage)
 for q in manifest:assert sha(stage/Path(q['path']).name)==q['sha256']
 os.rename(I,temp/'prior')
 try:os.rename(stage,I)
 except BaseException:os.rename(temp/'prior',I);raise
for q in manifest:assert sha(A/q['path'])==sha(I/Path(q['path']).name)==sha(O/Path(q['path']).name)==q['sha256']
subprocess.run(['bash','-n',str(G/'launch-kurgen-test.sh')],check=True);assert sha(G/'launch-kurgen-test.sh')==sha(A/'tools/launch-kurgen-test.sh')
dump(W/'deployment.json',dict(status='installed_ready_for_review',installed_at_utc=now,repository_asset=str(A),installed_mod=str(I),runtime_files=manifest,exact_repository_bytes_verified=True,launcher=str(G/'launch-kurgen-test.sh'),game_launched=False,runtime_visual_review='pending_user_revision_1_2',rollback=str(W/'installed_before_v3')))
state=read(D.parent/'project_state.json');state.update(status='window_scope_corrected_ready_for_review',latest_scene=v['scene'],upright_scene=v['scene'],latest_deliverables=str(O.parent.parent),updated_at_utc=now,user_approved=False,published=False,progress=dict(texture_uv='only_marked_bridge_windows_native_mapping_isolated',pbr_authoring='vents_restored_with_longitudinal_relief_and_zero_emission',pbr_tuning='authoring_and_native_surface_audits_passed_runtime_pending',engine_validation='0_8_1_and_0_18_0_non_visual_checks_passed'),engine_validation=dict(build='Official OpenReliant 0.18.0',minimum='0.8.1',non_visual_checks='passed',visual_review='pending_user_revision_1_2',game_launched=False,evidence=str(W/'compatibility.json')))
state['window_and_relief_revision']=dict(artwork_revision='1.2',scene=v['scene'],maps=v['maps'],bridge_maps=v['bridge_maps'],bridge_lod_maps=v['bridge_lod_maps'],checks=str(W/'map_checks.json'),window_scope='Only originally user-marked bridge front and sides',restored='Unmarked nose top/side vents, rear strips and under-turret hardware',front_faces=14,coarse_side_faces=4,turret_materials_unchanged=True)
dump(D.parent/'project_state.json',state)
allmaps=read(W/'prior_manifest.json')['maps'];allmaps['hull']=v['maps'];allmaps['bridge']=v['bridge_maps'];allmaps['bridge_lod']=v['bridge_lod_maps']
dump(D/'manifest.json',dict(ship='Kurgen',variant='worn',artwork_revision='1.2',status=state['status'],user_approved=False,published=False,scene=rec(Path(v['scene']),D),pbr_release_gate=state['pbr_release_gate'],progress=state['progress'],engine_validation=state['engine_validation'],runtime_exports=manifest,maps=allmaps,remaining=['User in-game review of corrected window scope and vents','Campaign, turret tracking/firing, damage and distance transitions','Standard gallery photos after publication approval']))
dump(W/'final-review-verification.json',dict(status='passed',checked_at_utc=now,runtime_files_verified=len(manifest),native_geometry_preserved=True,targeted_uv_faces=18,emission_scope_verified_all_detail_levels=True,restored_vent_pixels_exact=True,installed_exact_repository_bytes=True,game_launched=False,user_visual_review='pending_revision_1_2',published=False))
author=A/'source/authoring/window_scope_v3';author.mkdir(parents=True,exist_ok=True)
for p in W.iterdir():
 if p.is_file() and p.suffix in ['.py','.json','.log']:
  s=p.read_text()
  for x,y in [(str(D),'${KURGEN_WORKSPACE}'),(str(R),'${ART_PACK_REPOSITORY}'),(str(G),'${OPENRELIANT_HOME}')]:s=s.replace(x,y)
  (author/p.name).write_text(s)
sourcefiles=[rec(p,A) for p in sorted((A/'source').rglob('*')) if p.is_file()];dump(A/'source-manifest.json',dict(status='correction-awaiting-user-review',ship='Kurgen',asset_revision='1.2',files=sourcefiles))
for q in sourcefiles:assert sha(A/q['path'])==q['sha256']
release=read(A/'release.json');release.update(asset_revision='1.2',status='held',hold_reason='Corrected window and vent scope awaits in-game review',user_approved=False,published=False,asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'));dump(A/'release.json',release)
dump(A/'validation.json',dict(status='non-visual-checks-passed-awaiting-user-review',checked_at_utc=now,asset_revision='1.2',user_approved=False,packaging_ready=False,game_launched=False,review_engine='0.18.0',minimum_openreliant='0.8.1',asset_manifest_sha256=sha(A/'asset-manifest.json'),source_manifest_sha256=sha(A/'source-manifest.json'),checks=['Official native model and mission checks on 0.8.1 and 0.18.0','Restored vent and unmarked hardware base pixels match first pass','No emission outside user-highlighted bridge surfaces across all six detail levels','Front bridge/rear shared texture isolation and four coarse side faces corrected','Geometry, original mesh normals, collision, attachments and animations preserved','Normal/ORM maps and three emissive texture sets pass validation','Packed source reopened and installed export hashes verified','Front, opposite, rear, belly and dark authoring views reviewed'],runtime_visual_review='pending_user_revision_1_2'))
print(json.dumps(dict(status=state['status'],runtime_files_verified=len(manifest),source_files_verified=len(sourcefiles),launcher=str(G/'launch-kurgen-test.sh')),indent=2))
