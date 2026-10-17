from pathlib import Path
import json,hashlib,shutil,subprocess,numpy as np
from PIL import Image,ImageFilter
D=Path('${KURGEN_WORKSPACE}');W=D/'work/window_scope_v3';O=D/'exports/openreliant_0_8_v3/mods/116-kurgen-worn-v1';G=Path('${OPENRELIANT_HOME}')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
r=read(W/'validation.json');assert sha(r['scene'])==r['scene_sha256'];pres=read(W/'native_preservation.json');assert pres['passed']
mapchecks=[];probes=[]
for role,stem,maps,dim in [('hull','orku1_hull',r['maps'],(4096,4096)),('bridge','orku3_bridge',r['bridge_maps'],(512,512)),('bridge_lod','orku3_bridge_lod',r['bridge_lod_maps'],(256,1024))]:
    for key,suffix in [('basecolor',''),('normal','_normal'),('emissive','_emissive')]:shutil.copy2(maps[key]['path'],O/(stem+suffix+'.png'))
    rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/(stem+'_orm.png'))
    for key,q in maps.items():
        assert sha(q['path'])==q['sha256']
        with Image.open(q['path']) as im:im.load();assert im.size==dim
    n=rgb(O/(stem+'_normal.png')).astype(np.float32)/255*2-1;err=float(np.max(np.abs(np.linalg.norm(n,axis=-1)-1)));assert err<.015
    orm=rgb(O/(stem+'_orm.png'));assert np.all(orm[:,:,0]==255) and np.array_equal(orm[:,:,1],np.asarray(rough)) and np.array_equal(orm[:,:,2],np.asarray(metal))
    em=rgb(O/(stem+'_emissive.png'));assert np.any(em) and np.count_nonzero(np.any(em,axis=-1))<dim[0]*dim[1]*.25
    q=subprocess.run(['/tmp/kurgen-emissive-probe',str(O),stem],capture_output=True,text=True,check=True);assert 'EMISSIVE PASS' in q.stdout+q.stderr;probes.append(q.stdout+q.stderr)
    mapchecks.append(dict(role=role,dimensions=list(dim),normal_max_unit_error=err,orm_verified=True))
base=rgb(O/'orku1_hull.png');original=rgb(D/'maps/kurgen_hull_basecolor_v1.png');ap=np.asarray(Image.open(r['maps']['window_aperture']['path']).convert('L').filter(ImageFilter.MaxFilter(5)))>0
changed=np.any(base!=original,axis=-1);assert not np.any(changed&~ap)
em=rgb(O/'orku1_hull_emissive.png');assert not np.any(em[~ap])
# Explicit regression checks: nose vents, front/rear shared strip and under-turret hardware.
rects={'nose_top_vents':[170,9,245,49],'nose_side_vents':[63,77,185,101],'rear_reused_strip':[38,102,46,123],'under_rear_turret':[64,173,92,182]}
for name,(a,b,c,d) in rects.items():
    sl=np.s_[b*16:d*16,a*16:c*16];assert np.array_equal(base[sl],original[sl]),name;assert not np.any(em[sl]),name
flat=np.asarray(Image.open(r['maps']['flat_graphics']['path']).convert('L').filter(ImageFilter.MinFilter(25)))>250
n=rgb(O/'orku1_hull_normal.png').astype(np.float32)/255*2-1;assert np.max(np.abs(n[flat]-[0,0,1]))<.008
assert np.count_nonzero(rgb(r['maps']['vent_ribs']['path'])[:,:,0])>1000
for name in ['10_Rus_STUR.SHP','orku1_turret.png','orku1_turret_normal.png','orku1_turret_orm.png','mission962.dte','kurgen_inspection.luau']:
    assert sha(O/name)==sha(D/'exports/openreliant_0_8_v2/mods/116-kurgen-worn-v1'/name)
assert not any(p.name.startswith(('g-','r-')) for p in O.iterdir())
native=[]
for version in ['0.8.1','0.18.0']:
    for kind,name in [('shp','Rus_Kurgan.SHP'),('shp','10_Rus_STUR.SHP'),('dte','mission962.dte')]:
        q=subprocess.run([str(G/f'releases/openreliant-v{version}-linux-x86_64/sltool'),kind,'check',str(O/name)],capture_output=True,text=True,check=True);native.append(dict(version=version,file=name,exit_code=q.returncode,output=q.stdout+q.stderr))
dump(W/'native_checks.json',native);(W/'emissive-loader-probe.log').write_text('\n'.join(probes))
dump(W/'map_checks.json',dict(passed=True,materials=mapchecks,changed_main_albedo_percent=float(changed.mean()*100),main_albedo_outside_authorized_side_windows_identical_to_first_pass=True,emission_outside_authorized_regions_zero=True,restored_vent_regions=rects,vent_ribs_authored=True,flat_paint_normals_preserved=True,bridge_front_faces_only=True,geometry_normals_attachments_animations_preserved=True,emissive_loader=dict(engine_source='official 0.8.1',probe_sha256=sha('/tmp/kurgen-emissive-probe'),output=probes),no_generated_colour_variant_files=True,runtime_visual_review='pending_user'))
ini=O/'mod.ini';lines=ini.read_text().splitlines();lines=['Description=Kurgen revision 1.2: windows restricted to the marked bridge sections; original vents restored with structural relief. Awaiting review.' if x.startswith('Description=') else x for x in lines];ini.write_text('\n'.join(lines)+'\n')
shutil.copy2(D/'review/window_scope_v3/material_front.png',O/'mod.png')
(O.parent.parent/'README.md').write_text('# Kurgen correction 1.2\n\nWindows restricted to the user-marked bridge sections. Unmarked amber slots restored to original vent artwork with stronger mechanical relief. The front bridge pair has a dedicated 512-square material to prevent emission on the rear faces that reused its UVs. Native geometry and attachments retained. Runtime review pending.\n')
print(json.dumps(read(W/'map_checks.json'),indent=2))
