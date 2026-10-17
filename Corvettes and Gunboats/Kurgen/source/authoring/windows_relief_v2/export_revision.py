from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
import numpy as np
from PIL import Image,ImageFilter
D=Path('${KURGEN_WORKSPACE}');W=D/'work/windows_relief_v2';M=D/'maps/windows_relief_v2'
OLD=D/'exports/openreliant_0_8_v1';E=D/'exports/openreliant_0_8_v2';O=E/'mods/116-kurgen-worn-v1';G=Path('${OPENRELIANT_HOME}')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
r=read(W/'validation.json');assert sha(r['scene'])==r['scene_sha256']
if not E.exists():shutil.copytree(OLD,E)
for key,suffix in [('basecolor',''),('normal','_normal'),('emissive','_emissive')]:shutil.copy2(r['maps'][key]['path'],O/('orku1_hull'+suffix+'.png'))
rough=Image.open(r['maps']['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(r['maps']['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/'orku1_hull_orm.png')
changed=np.any(rgb(O/'orku1_hull.png')!=rgb(OLD/'mods/116-kurgen-worn-v1/orku1_hull.png'),axis=-1)
ap=np.asarray(Image.open(r['maps']['window_aperture']['path']).convert('L').filter(ImageFilter.MaxFilter(5)))>0
assert not np.any(changed&~ap)
em=rgb(O/'orku1_hull_emissive.png');lit=np.any(em>0,axis=-1);assert 0<lit.mean()<.08 and not np.any(lit&~ap)
glass=np.asarray(Image.open(r['maps']['window_glass']['path']).convert('L'))
assert np.max(em[glass==0])<=2
n=rgb(O/'orku1_hull_normal.png').astype(np.float32)/255*2-1;length=np.linalg.norm(n,axis=-1);assert np.max(np.abs(length-1))<.015
n0=rgb(OLD/'mods/116-kurgen-worn-v1/orku1_hull_normal.png').astype(np.float32)/255*2-1
xy=np.linalg.norm(n[:,:,:2],axis=-1);xy0=np.linalg.norm(n0[:,:,:2],axis=-1)
struct=(xy0>.025)&~ap
ratio=float(np.median(xy[struct]/xy0[struct]));assert ratio>2.1
flat=np.asarray(Image.open(r['maps']['flat_graphics']['path']).convert('L').filter(ImageFilter.MinFilter(25)))>250
assert np.max(np.abs(n[flat]-[0,0,1]))<.008
assert np.all(rgb(O/'orku1_hull_orm.png')[:,:,0]==255)
assert np.array_equal(rgb(O/'orku1_hull_orm.png')[:,:,1],np.asarray(rough))
assert np.array_equal(rgb(O/'orku1_hull_orm.png')[:,:,2],np.asarray(metal))
preserved=[]
for name in ['Rus_Kurgan.SHP','10_Rus_STUR.SHP','orku1_turret.png','orku1_turret_normal.png','orku1_turret_orm.png','mission962.dte','kurgen_inspection.luau']:
    assert sha(O/name)==sha(OLD/'mods/116-kurgen-worn-v1'/name);preserved.append(dict(file=name,sha256=sha(O/name)))
for key,q in r['maps'].items():
    assert sha(q['path'])==q['sha256']
    with Image.open(q['path']) as im:im.load();assert im.size==(4096,4096)
assert not any(p.name.startswith(('g-','r-')) for p in O.iterdir())
checks=[]
for version in ['0.8.1','0.18.0']:
    tool=G/f'releases/openreliant-v{version}-linux-x86_64/sltool'
    for kind,name in [('shp','Rus_Kurgan.SHP'),('shp','10_Rus_STUR.SHP'),('dte','mission962.dte')]:
        q=subprocess.run([str(tool),kind,'check',str(O/name)],capture_output=True,text=True,check=True);checks.append(dict(engine=version,file=name,exit_code=q.returncode,output=q.stdout+q.stderr))
dump(W/'native_checks.json',checks)
q=subprocess.run(['/tmp/kurgen-emissive-probe',str(O),'orku1_hull'],capture_output=True,text=True,check=True);assert 'EMISSIVE PASS' in q.stderr+q.stdout;(W/'emissive-loader-probe.log').write_text(q.stdout+q.stderr)
dump(W/'map_checks.json',dict(passed=True,changed_albedo_percent=float(changed.mean()*100),albedo_unchanged_outside_windows=True,emission_percent=float(lit.mean()*100),hull_and_frame_emission_black=True,structural_normal_median_xy_ratio=ratio,normal_max_unit_error=float(np.max(np.abs(length-1))),painted_graphics_normals_flat=True,orm_verified=True,all_maps_size=[4096,4096],geometry_and_turret_preserved=preserved,emissive_loader=dict(engine_source='official 0.8.1',probe_sha256=sha('/tmp/kurgen-emissive-probe'),output=q.stdout+q.stderr),runtime_visual_review='pending_user'))
ini=O/'mod.ini';s=ini.read_text();s=s.replace('Description=Restored Kurgen hull and shared Coalition small turret, with structural surface maps. Awaiting visual review.','Description=Kurgen worn hull with inset illuminated windows and stronger panel and machinery relief; shared small turret retained. Revision 1.1 awaiting visual review.');ini.write_text(s)
shutil.copy2(D/'review/windows_relief_v2/material_front.png',O/'mod.png')
(E/'README.md').write_text('# Kurgen material revision 1.1\n\nWarm window emissives, inset framed panes, deeper structural normals. Native models, original first-pass artwork outside windows, shared turret and inspection mission retained. Baseline 0.8.1, review 0.18.0. Runtime visual review pending.\n')
print(json.dumps(read(W/'map_checks.json'),indent=2))
