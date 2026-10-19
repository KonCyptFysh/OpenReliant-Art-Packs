from pathlib import Path
import sys,json,hashlib,shutil,zipfile,datetime,numpy as np
D=Path('${RELIANT_WORKSPACE}');W=D/'work/uv_projection_v7';B=D/'history/stages/pre_uv_projection_v7';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';I=Path('${OPENRELIANT_HOME}/game-data/mods/119-reliant-worn-v1');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(D/'work/alignment_v3'));from audit_native import parse
oldraw,oldparts=parse(B/'exports/openreliant_0_18_v1/mods'/S.name/'Reliant.SHP');raw,parts=parse(S/'Reliant.SHP');rep=json.loads((W/'native_repairs.json').read_text());changes=rep['files'][0]['uv_changes'];allowed=set();metrics=[]
for r in changes:
 f=parts[r['part']]['lods'][r['lod']]['faces'][r['face']];p=parts[r['part']]['lods'][r['lod']]['vertices'][f['ids']];allowed.update(range(f['at']+24,f['at']+48));uv=f['uv'];jac=np.linalg.solve(uv[1:]-uv[0],p[1:]-p[0]);angle=float(np.degrees(np.arctan2(jac[0,1],abs(jac[0,2]))));assert abs(angle)<.0001;metrics.append(dict(lod=r['lod'],face=r['face'],stored_row_tilt_degrees=angle))
assert len(changes)==8 and len(raw)==len(oldraw) and all(i in allowed for i,(a,b) in enumerate(zip(raw,oldraw)) if a!=b)
# Every previously visible window remains wholly contained after rectification.
def in_tri(x,tri):
 a=np.array(tri);w=np.linalg.solve((a[1:]-a[0]).T,np.array(x)-a[0]);return min(w)>=-1e-5 and sum(w)<=1.00001
windows=json.loads((D/'work/windows_v5/window-material-regions.json').read_text())['windows'];contained=0
for side in [-1,1]:
 rs=[r for r in changes if r['lod']==0 and r['side']==side];old=[r['before'] for r in rs];new=[parts[r['part']]['lods'][0]['faces'][r['face']]['uv'] for r in rs]
 for w in windows:
  a,b,c,d=np.array(w['outer_frame'])/16;center=((a+c)/2,(b+d)/2)
  if not any(in_tri(center,t) for t in old):continue
  assert all(any(in_tri(q,t) for t in new) for q in [(a,b),(c,b),(c,d),(a,d)]),w['id'];contained+=1
assert contained==21,contained
scene=json.loads((W/'scene-validation.json').read_text());assert scene['passed']
evidence=['v6-forward-panel','v7-forward-panel','v7-forward-windows','v7-port-panel','v7-port-panel-rotated','v7-forward-panel-rotated']
for n in evidence:
 s=(W/(n+'.log')).read_text().lower();assert (W/(n+'.png')).exists();assert not any(x in s for x in ['warning(scripts)','warning(library)','error(']),n
state=json.loads((D.parent/'project_state.json').read_text())
for n,h in state['source_originals'].items():assert sha(D/'source'/n)==h,n
packages=[]
for tier,root in [('4k',D/'exports/openreliant_0_18_v1'),('2k',D/'exports/review_v1_2k'),('1k',D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name;O=B/'exports'/root.name/'mods'/S.name
 assert {p.name for p in T.iterdir()}=={p.name for p in O.iterdir()}
 for p in T.iterdir():
  if p.name not in ['Reliant.SHP','mod.ini']:assert sha(p)==sha(O/p.name),p.name
 assert sha(T/'Reliant.SHP')==sha(W/'native/Reliant.SHP')
 shutil.copy2(D/'README.md',root/'README.md');files=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-7-awaiting-review',resolution=tier,surface_revision=7,files=files),indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as a:
  for p in sorted(root.rglob('*')):
   if p.is_file():a.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as a:
  assert a.testzip() is None
  for f in files:assert hashlib.sha256(a.read('mods/'+S.name+'/'+f['file'])).hexdigest()==f['sha256']
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGED',tier,flush=True)
for name in ['Reliant.SHP','mod.ini']:shutil.copy2(S/name,I/name)
assert all(sha(p)==sha(I/p.name) for p in S.iterdir())
state.update(status='surface_revision_7_ready_for_review',surface_revision=7,latest_scene=str(D/'reliant_worn_pbr_v7.blend'),user_approved=False,published=False,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(texture_uv='Both intact forward window panels use a consistent longitudinal/vertical projection in native detail levels 0 and 1; 8 triangle UVs repaired',engine_validation='Official 0.18.0 native-format checks plus same-camera UV before/after and both sides under changed light. All maps byte-identical to revision 6',visual_review='Revision 7 forward panel UV projection awaits user review')
state['uv_projection_revision_7']=dict(changed_triangles=8,detail_levels=[0,1],visible_window_inserts_retained=contained,geometry_unchanged=True,all_material_pixels_unchanged=True,evidence=str(W/'validation.json'),coarse_lods_and_wreck='Original decimation and deformation retained')
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',native_uv_faces=8,detail_levels=[0,1],stored_uv_metrics=metrics,visible_windows_contained=contained,all_non_uv_native_bytes_unchanged=True,all_texture_maps_unchanged=True,originals_unchanged=True,scene=scene,native_checks=json.loads((W/'projection-validation.json').read_text())['native_checks'],packages=packages,installed_hashes_match=True,evidence=evidence,user_visual_approval_pending=True),indent=2)+'\n');print('V7_INSTALLED_VERIFIED',flush=True)
