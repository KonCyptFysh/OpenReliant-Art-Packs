from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,datetime,numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/windows_v5';M=D/'maps/windows_v5';B=D/'history/stages/pre_windows_v5';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';G=Path('${OPENRELIANT_HOME}');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((B/'project_state.json').read_text());before=B/'exports/openreliant_0_18_v1/mods'/S.name
changed={'orr2_hull.png','orr2_hull_emissive.png','orr2_hull_normal.png','orr2_hull_orm.png','mod.ini'}
for p in S.iterdir():
 if p.name not in changed:assert sha(p)==sha(before/p.name),p.name
for name,digest in old['source_originals'].items():assert sha(D/'source'/name)==digest,name
mask=np.asarray(Image.open(W/'window-edit-mask.png'))>0;nm=np.asarray(Image.open(W/'window-normal-edit-mask.png'))>0
for suffix in ['','_emissive','_normal','_orm']:
 a=np.asarray(Image.open(M/f'orr2_hull{suffix}.png'));b=np.asarray(Image.open(D/f'maps/alignment_v4/orr2_hull{suffix}.png'));m=nm if suffix=='_normal' else mask;assert np.array_equal(a[~m],b[~m]),suffix
 assert sha(M/f'orr2_hull{suffix}.png')==sha(S/f'orr2_hull{suffix}.png')
glass=np.asarray(Image.open(M/'orr2_hull_glass.png'))/255;frame=np.asarray(Image.open(M/'orr2_hull_window_frame.png'))/255;e=np.asarray(Image.open(M/'orr2_hull_emissive.png'));o=np.asarray(Image.open(M/'orr2_hull_orm.png'))
assert e[frame>.9].max()==0;assert o[:,:,2][glass>.99].max()==0
assert (D/'reliant_worn_pbr_v5.blend').exists()
reg=json.loads((W/'window-material-regions.json').read_text());assert reg['window_count']==64
polys=json.loads((D/'work/alignment_v4/measured-geometry.json').read_text())['pockets']
def ins(p,xy):
 x,y=xy;v=False
 for (a,b),(c,d) in zip(p,p[1:]+p[:1]):
  if d!=b and ((b>y)!=(d>y)) and x<(c-a)*(y-b)/(d-b)+a:v=not v
 return v
contained=0
for w in reg['windows']:
 a,b,c,d=np.array(w['outer_frame'])/4;center=((a+c)/2,(b+d)/2)
 p=next((p for p in polys if ins(p,center)),None)
 if p:
  assert all(ins(p,q) for q in [(a,b),(c,b),(c,d),(a,d)]),w['id'];contained+=1
 assert w['orientation']['strength']>.7
assert contained==61
checks=[]
for p in S.iterdir():
 if p.suffix in ['.SHP','.dte']:
  q=subprocess.run([str(G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'),'shp' if p.suffix=='.SHP' else 'dte','check',str(p)],capture_output=True,text=True,check=True);checks.append(dict(file=p.name,result=q.stdout.strip()))
evidence=['v5-bridge-cell','v5-forward-windows','v5-bridge-other-rotated','v5-bridge-cell-rotated-light0','v5-bridge-cell-rotated-light0.25','v5-bridge-cell-rotated-light1','v5-bridge-cell-1k','v5-forward-windows-2k']
for name in evidence:
 s=(W/(name+'.log')).read_text();assert not any(x in s.lower() for x in ['warning(scripts)','warning(library)','error(']),name;assert (W/(name+'.png')).exists()
# Controlled camera/lighting only: inspect the same central pane at 0,25,100% cabin power.
levels=[]
for power in ['0','0.25','1']:
 im=np.asarray(Image.open(W/f'v5-bridge-cell-rotated-light{power}.png')).astype(float)
 levels.append(float(im[381:407,368:549,:3].mean()))
assert levels[0]<levels[1]<levels[2],levels
packages=[];normals=[]
for tier,n,root in [('4k',4096,S.parent.parent),('2k',2048,D/'exports/review_v1_2k'),('1k',1024,D/'exports/review_v1_1k')]:
 T=root/'mods'/S.name
 for p in T.glob('*.png'):
  if p.name=='mod.png':continue
  im=Image.open(p);assert im.size==(n,n),(p,im.size)
  if p.stem.endswith('_normal'):
   a=np.asarray(im.convert('RGB')).astype('float32')/127.5-1;err=float(abs(np.linalg.norm(a,axis=-1)-1).max());assert err<.015;normals.append(dict(tier=tier,file=p.name,max_unit_error=err))
 for name in ['launch-reliant-test.sh','launch-reliant-doors-test.sh']:subprocess.run(['bash','-n',str(root/name)],check=True)
 shutil.copy2(D/'README.md',root/'README.md');records=[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(T.iterdir()) if p.is_file()]
 (root/'manifest.json').write_text(json.dumps(dict(ship='Reliant',status='surface-revision-5-awaiting-review',resolution=tier,surface_revision=5,files=records),indent=2)+'\n')
 z=D/'packages'/f'Reliant-Worn-Review-v0.1.0-{tier}.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
  for p in sorted(root.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(root))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for r in records:assert hashlib.sha256(archive.read('mods/'+S.name+'/'+r['file'])).hexdigest()==r['sha256']
 packages.append(dict(tier=tier,path=str(z),sha256=sha(z),bytes=z.stat().st_size));print('PACKAGE',tier,flush=True)
installed=G/'game-data/mods'/S.name
for p in S.iterdir():shutil.copy2(p,installed/p.name)
assert {p.name for p in S.iterdir()}=={p.name for p in installed.iterdir()};assert all(sha(p)==sha(installed/p.name) for p in S.iterdir())
state=json.loads((D.parent/'project_state.json').read_text());state.update(status='surface_revision_5_ready_for_review',user_approved=False,published=False,latest_scene=str(D/'reliant_worn_pbr_v5.blend'),current_maps=str(M),surface_revision=5,packages=packages,updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
state['progress'].update(texture_uv='All 64 window rectangles retained; inserts oriented from native UV-to-world mapping. Native UVs and geometry unchanged from revision 4',pbr_authoring='Reauthored worn steel frames, gaskets, smoked scratched glazing and cabin interior detail; matching colour, height, normal, AO, roughness, metal and spatially varied emission',engine_validation='Official 0.18.0 close checks: bridge both sides, forward windows, 0/25/100 percent illumination, 1K and 2K textures. Preservation, containment, native and normal checks passed',visual_review='Revision 5 window treatment awaits user visual approval')
state['windows_revision_5']={'count':64,'height_resolution':4096,'source_mode':'built-in ImageGen plus registered material assembly','layout_retained':True,'frames_nonemissive':True,'glass_dielectric':True,'lighting_logic_unchanged':True,'native_unchanged':True,'evidence':str(W/'validation.json')}
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
(W/'validation.json').write_text(json.dumps(dict(passed=True,engine='official OpenReliant 0.18.0',source_originals_unchanged=True,window_count=64,frame_containment=contained,native_files_byte_identical_to_v4=True,other_atlases_and_scripts_byte_identical=True,pixels_outside_window_patches_unchanged=True,frames_nonemissive=True,glass_dielectric=True,brightness_probe_0_25_100=levels,native_checks=checks,normal_checks=normals,installed_hashes_match=True,packages=packages,evidence=evidence,user_visual_approval_pending=True),indent=2)+'\n');print('RELIANT_V5_INSTALLED_AND_PACKAGED',flush=True)
