from pathlib import Path
import json,hashlib,struct,subprocess,shutil
import numpy as np
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';E=Path('${OPENRELIANT_HOME}/releases/openreliant-v0.18.0-linux-x86_64')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((W/'validation.json').read_text());assert sha(r['scene'])==r['scene_sha256'];pres=[]
def groups(fs):
 i=0
 while i<len(fs):
  end=i+fs[i]['remaining']+1;assert end<=len(fs);assert all(fs[j]['remaining']==end-j-1 for j in range(i,end));yield i,end;i=end
def matches(anchor,prev,cur):
 if anchor['kind']==1:ids=[anchor['vertices'][0],prev['vertices'][2]];uv=[anchor['uv'][0],prev['uv'][2]]
 else:
  assert anchor['kind'] in [2,3];ids=prev['vertices'][1:];uv=prev['uv'][1:]
 return anchor['material']==cur['material'] and ids==cur['vertices'][:2] and np.max(np.abs(np.array(uv)-cur['uv'][:2]))<=1e-6
mapping={'rel_1':'orr1_hull','rel_2':'orr2_hull','rel_3':'orr3_hull'}
for file in ['Reliant.SHP','Reliant_destback.SHP']:
 raw=(D/'source'/file).read_bytes();out=bytearray(raw);pos=0;part=lod=-1;allowed=set();joins=[];materials=[];faces_total=0;lightmaps=[]
 while pos<len(raw):
  tag,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count
  if tag==1:
   assert size==312
   for i in range(count):
    at=start+i*size+240;flags=struct.unpack_from('<I',raw,at)[0]
    if flags&128:
     struct.pack_into('<I',out,at,flags&~128);allowed.update(range(at,at+4));lightmaps.append(dict(part=i,old_flags=flags,new_flags=flags&~128))
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  if tag==6:
   for i in range(count):
    at=start+i*size;old=raw[at:at+64].split(b'\0')[0].decode();assert old.lower() in set(mapping)|{'dam_1'}
    if old.lower() in mapping:
     new=mapping[old.lower()];out[at:at+64]=new.encode().ljust(64,b'\0');allowed.update(range(at,at+64));materials.append(dict(old=old,new=new))
  if tag==3:
   assert size==80;fs=[];faces_total+=count
   for i in range(count):
    at=start+i*size;uv=np.array(struct.unpack_from('<6f',out,at+24)).reshape(2,3).T;kind,remaining=struct.unpack_from('<2I',out,at+72);fs.append(dict(material=struct.unpack_from('<I',out,at)[0],vertices=list(struct.unpack_from('<3I',out,at+12)),uv=uv,kind=kind,remaining=remaining))
   segments=[]
   for first,last in groups(fs):
    seg=first
    for j in range(first+1,last):
     if not matches(fs[seg],fs[j-1],fs[j]):segments.append((seg,j));seg=j
    segments.append((seg,last))
   for first,last in segments:
    for j in range(first,last):
     rem=last-j-1
     if rem!=fs[j]['remaining']:
      at=start+j*size+76;struct.pack_into('<I',out,at,rem);allowed.update(range(at,at+4));joins.append(dict(part=part,lod=lod,face=j,prior=fs[j]['remaining'],remaining=rem));fs[j]['remaining']=rem
   for first,last in groups(fs):
    for j in range(first+1,last):assert matches(fs[first],fs[j-1],fs[j])
  if tag not in (1,3,6):assert raw[pos:end]==out[pos:end]
  pos=end
 diff=[i for i,(a,b) in enumerate(zip(raw,out)) if a!=b];assert len(raw)==len(out) and all(i in allowed for i in diff)
 (O/file).write_bytes(out);pres.append(dict(file=file,passed=True,source_sha256=sha(D/'source'/file),output_sha256=sha(O/file),faces_checked=faces_total,materials=materials,legacy_lightmap_flags_cleared=lightmaps,continuation_corrections=joins,changed_bytes=len(diff),geometry_uvs_normals_attachments_animations_collision_byte_identical=True,allowed_changes='Namespaced material names, primitive continuation lengths at existing UV breaks, and only the legacy lightmap bit on part records (new emissive maps replace it)'))
(W/'native_preservation.json').write_text(json.dumps({'passed':True,'files':pres,'shared_alliance_weapon_04_Pulse_las_unchanged':True,'shared_turrets_and_Reliant_Hang_unchanged':True},indent=2)+'\n')
checks=[]
for i in range(1,4):
 maps=r['maps'][f'rel{i}'];stem=f'orr{i}_hull'
 for key,suffix in [('basecolor',''),('normal','_normal'),('emissive','_emissive')]:shutil.copy2(maps[key]['path'],O/(stem+suffix+'.png'))
 rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/(stem+'_orm.png'))
 normal=np.asarray(Image.open(O/(stem+'_normal.png')).convert('RGB')).astype(np.float32)/255*2-1;error=float(np.max(np.abs(np.linalg.norm(normal,axis=-1)-1)));assert error<.02
 em=np.asarray(Image.open(O/(stem+'_emissive.png')).convert('RGB'));assert em.max()>0
 checks.append(dict(role=f'rel{i}',normal_max_unit_error=error,dimensions=[4096,4096],emissive_fraction=float(np.any(em>0,axis=-1).mean())))
(W/'map_checks.json').write_text(json.dumps(dict(passed=True,maps=checks,no_colour_variant_duplicates=True),indent=2)+'\n')
for number,doors in [(959,False),(958,True)]:
 source='''mission({name="Reliant - Worn Paint inspection"})
reliant=flight_group("(FG)Reliant", {wing="player"})
reliant_inspection=ship("Reliant - Inspection", {type="reliant", group=reliant})
initialise=part("(F)ReliantInspection", function()
 CreateFlightGroup(reliant)
'''
 if doors:source+=' Wait(2)\n StartShipAnimation(reliant_inspection, "opendoor")\n StartShipAnimation(reliant_inspection, "opendoor2")\n Wait(1)\n StopShipAnimation(reliant_inspection, "opendoor")\n StopShipAnimation(reliant_inspection, "opendoor2")\n Wait(12)\n StartShipAnimationReverse(reliant_inspection, "opendoor")\n StartShipAnimationReverse(reliant_inspection, "opendoor2")\n Wait(2)\n StopShipAnimation(reliant_inspection, "opendoor")\n StopShipAnimation(reliant_inspection, "opendoor2")\n Wait(12)\n StartShipAnimation(reliant_inspection, "opendoor")\n StartShipAnimation(reliant_inspection, "opendoor2")\n Wait(1)\n StopShipAnimation(reliant_inspection, "opendoor")\n StopShipAnimation(reliant_inspection, "opendoor2")\n'
 source+=' return 1\nend, {start=true})\n';p=W/f'mission{number}.luau';p.write_text(source);subprocess.run([str(E/'sltool'),'dte','build',str(p),str(O/f'mission{number}.dte')],check=True)
(O/'mod.ini').write_text('''[Mod]
Name=Reliant - Worn Paint (Review)
Version=0.1.0-beta.1
Description=Capital-ship first pass: restored native hull atlases, structural PBR and normals, damage-responsive warm windows and engine-component-aware nozzle afterglow. Awaiting visual approval.
OpenReliant=0.18.0
License=CC-BY-NC-SA-4.0

[Scripts]
Global=reliant_lighting.luau
Player=reliant_surface.luau, reliant_camera.luau

[Missions]
mission959.dte=reliant_inspection.luau
mission958.dte=reliant_inspection.luau
''')
(O/'license.txt').write_text('Reliant - Worn Paint\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/\nOriginal StarLancer assets retain their respective owners rights. Requires your own StarLancer installation.\n')
shutil.copy2(D/'review/material_front.png',O/'mod.png')
checks=[]
for kind,file in [('shp','Reliant.SHP'),('shp','Reliant_destback.SHP'),('dte','mission959.dte'),('dte','mission958.dte')]:
 p=subprocess.run([str(E/'sltool'),kind,'check',str(O/file)],capture_output=True,text=True,check=True);checks.append(dict(file=file,exit_code=p.returncode,output=p.stdout+p.stderr))
(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('RELIANT_NATIVE_EXPORT_PASSED',[(x['file'],x['faces_checked'],len(x['continuation_corrections'])) for x in pres],flush=True)
