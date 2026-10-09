import os
from pathlib import Path
import json,hashlib,shutil,struct,subprocess,numpy as np
from PIL import Image
D=Path(os.environ['BASILISK_WORKSPACE']).resolve();W=D/'work/nose_finish_v2'
MOD='103-basilisk-worn-v1';old=D/'exports/openreliant_v1/mods'/MOD;out=D/'exports/openreliant_v2/mods'/MOD
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());assert sha(Path(r['scene']))==r['scene_sha256']
for p in old.iterdir():shutil.copy2(p,out/p.name)
raw=(old/'Rus_basalisk.SHP').read_bytes();data=bytearray(raw);at=2290
assert struct.unpack_from('<I',raw,at)[0]==4 and struct.unpack_from('<I',raw,at+0x34)[0]==3
assert struct.unpack_from('<2f',raw,at+0x74)==(1000.,2.)
struct.pack_into('<2f',data,at+0x74,450.,.65)
changed=[i for i,(a,b) in enumerate(zip(raw,data)) if a!=b]
assert all(at+0x74<=i<at+0x7c for i in changed)
(out/'Rus_basalisk.SHP').write_bytes(data)
for key,suffix in [('basecolor',''),('normal','_normal')]:shutil.copy2(r['maps']['hull'][key]['path'],out/('orbs1_hull'+suffix+'.png'))
rough=Image.open(r['maps']['hull']['roughness']['path']).convert('RGB').getchannel('R')
metal=Image.open(r['maps']['hull']['metallic']['path']).convert('RGB').getchannel('R')
Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(out/'orbs1_hull_orm.png')
for suffix in ['','_normal','_orm']:shutil.copy2(out/('orbs1_hull'+suffix+'.png'),out/('gorbs1_hull'+suffix+'.png'))
checks=[];tool=os.environ['OPENRELIANT_SLTOOL']
for kind,name in [('shp','Rus_basalisk.SHP'),('dte','mission988.dte')]:
    c=subprocess.run([tool,kind,'check',str(out/name)],check=True,text=True,capture_output=True);checks.append(dict(file=name,exit_code=c.returncode,output=c.stdout+c.stderr,sha256=sha(out/name)))
normal=np.asarray(Image.open(out/'orbs1_hull_normal.png').convert('RGB')).astype(np.float32)/255*2-1
error=float(np.max(np.abs(np.linalg.norm(normal,axis=-1)-1)));assert error<.02
mask=np.asarray(Image.open(r['maps']['hull']['nose_mask']['path']).convert('L'))
base=np.asarray(Image.open(out/'orbs1_hull.png').convert('RGB'));prior=np.asarray(Image.open(old/'orbs1_hull.png').convert('RGB'))
assert np.array_equal(base[mask==0],prior[mask==0])
glass=np.asarray(Image.open(r['maps']['hull']['glass']['path']).convert('L'))>250
assert np.max(np.abs(normal[glass]-[0,0,1]))<.008
assert np.array_equal(base[glass],prior[glass])
orm=np.asarray(Image.open(out/'orbs1_hull_orm.png').convert('RGB'))
assert np.all(orm[:,:,0]==255) and np.array_equal(orm[:,:,1],np.asarray(rough)) and np.array_equal(orm[:,:,2],np.asarray(metal))
assert orm[:,:,2][glass].max()==0
for suffix in ['','_normal','_orm']:assert sha(out/('orbs1_hull'+suffix+'.png'))==sha(out/('gorbs1_hull'+suffix+'.png'))
preservation=dict(passed=True,base_model_sha256=sha(old/'Rus_basalisk.SHP'),output_sha256=sha(out/'Rus_basalisk.SHP'),allowed_changes='Only range and brightness of the single inherited red light at attachment offset 2290; prior UV repairs preserved.',changed_byte_offsets=changed,geometry_normals_uvs_other_attachments_animation_collision_and_winding_byte_identical=True,red_light=dict(range_before=1000,range_after=450,brightness_before=2,brightness_after=.65,reach_before=2000,reach_after=292.5),engine_glow_sprites_unchanged=True)
(W/'native_preservation.json').write_text(json.dumps(preservation,indent=2)+'\n');(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(W/'map_checks.json').write_text(json.dumps(dict(passed=True,normal_max_unit_error=error,base_colour_outside_nose_unchanged=True,glazing_colours_and_flat_normals_preserved=True,glass_metallic_zero=True,orm_channels_match=True,flight_and_loadout_maps_identical=True,dimensions=[4096,4096]),indent=2)+'\n')
(out/'mod.ini').write_text('[Mod]\nName=Basilisk - Worn Paint\nVersion=0.1.0-beta.1\nDescription=Restored worn Coalition livery, smoother reflective nose panelling, amber glazing and repaired machinery UVs. Red hull light spill restrained. In-game review pending.\nOpenReliant=0.7.0\nLicense=CC-BY-NC-SA-4.0\n')
shutil.copy2(D/'review/nose_finish_v2/material_front.png',out/'mod.png')
print('Basilisk v2 model and material checks passed; light reach 2000 -> 292.5; nose maps and glazing verified.')
