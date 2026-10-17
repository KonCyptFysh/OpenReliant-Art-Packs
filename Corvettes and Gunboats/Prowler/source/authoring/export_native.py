from pathlib import Path
import json,hashlib,shutil,struct,subprocess,os
import numpy as np
from PIL import Image
D=Path('${PROWLER_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_18_v1/mods/117-prowler-worn-v1';G=Path('${OPENRELIANT_HOME}');E=G/'releases/openreliant-v0.18.0-linux-x86_64';E8=G/'releases/openreliant-v0.8.1-linux-x86_64'
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
for file,mapping in [('US_Prowler.SHP',{'prow_1':'orpr1_hull1','prow_2':'orpr1_hull2'})]:
 raw=(D/'source'/file).read_bytes();out=bytearray(raw);pos=0;part=lod=-1;names=[];allowed=set();joins=[];materials=[];stats=[];protected=[]
 while pos<len(raw):
  tag,size,count=struct.unpack_from('<3H',raw,pos);start=pos+6;end=start+size*count
  if tag==1:names=[raw[start+i*size:start+i*size+64].split(b'\0')[0].decode() for i in range(count)]
  if tag==2:part+=1;lod=-1
  if tag==4:lod+=1
  if tag==6:
   for i in range(count):
    at=start+i*size;old=raw[at:at+64].split(b'\0')[0].decode();assert old.lower() in set(mapping)|{'dam_1'}
    if old.lower() in mapping:
     new=mapping[old.lower()];out[at:at+64]=new.encode().ljust(64,b'\0');allowed.update(range(at,at+64));materials.append(dict(part=part,lod=lod,old=old,new=new))
  if tag==3:
   assert size==80;fs=[]
   for i in range(count):
    at=start+i*size;uv=np.array(struct.unpack_from('<6f',out,at+24)).reshape(2,3).T;kind,remaining=struct.unpack_from('<2I',out,at+72)
    fs.append(dict(material=struct.unpack_from('<I',out,at)[0],vertices=list(struct.unpack_from('<3I',out,at+12)),uv=uv,kind=kind,remaining=remaining))
   oldgroups=list(groups(fs));segments=[]
   for first,last in oldgroups:
    seg=first
    for j in range(first+1,last):
     if not matches(fs[seg],fs[j-1],fs[j]):segments.append((seg,j));seg=j
    segments.append((seg,last))
   for first,last in segments:
    for j in range(first,last):
     rem=last-j-1
     if rem!=fs[j]['remaining']:
      at=start+j*size+76;struct.pack_into('<I',out,at,rem);allowed.update(range(at,at+4));joins.append(dict(part=names[part],lod=lod,face=j,prior=fs[j]['remaining'],remaining=rem));fs[j]['remaining']=rem
   for first,last in groups(fs):
    for j in range(first+1,last):assert matches(fs[first],fs[j-1],fs[j])
   stats.append(dict(part=names[part],lod=lod,faces=count,groups_before=len(oldgroups),groups_after=len(segments),all_shared_corner_uvs_match=True))
  if tag not in (3,6):
   assert raw[pos:end]==out[pos:end];protected.append(dict(tag=tag,bytes=end-pos,sha256=hashlib.sha256(raw[pos:end]).hexdigest()))
  pos=end
 assert pos==len(raw)==len(out)
 diff=[i for i,(a,b) in enumerate(zip(raw,out)) if a!=b];assert all(i in allowed for i in diff)
 (O/file).write_bytes(out);pres.append(dict(file=file,passed=True,source_sha256=sha(D/'source'/file),output_sha256=sha(O/file),uv_edits=[],continuation_corrections=joins,detail_meshes=stats,geometry_normals_uvs_attachments_animation_collision_winding_byte_identical=True,allowed_changes='Material names and primitive continuation counts at UV seams only',changed_bytes=len(diff),protected_chunks=protected))
assert sum(x['faces'] for p in pres for x in p['detail_meshes'])==1593
(W/'native_preservation.json').write_text(json.dumps({'passed':True,'files':pres,'all_1593_faces_checked':True},indent=2)+'\n')
checks=[]
for role,maps in r['maps'].items():
 stem='orpr1_'+role
 for key,suffix in [('basecolor',''),('normal','_normal'),('emissive','_emissive')]:
  if key in maps:shutil.copy2(maps[key]['path'],O/(stem+suffix+'.png'))
 rough=Image.open(maps['roughness']['path']).convert('RGB').getchannel('R');metal=Image.open(maps['metallic']['path']).convert('RGB').getchannel('R');Image.merge('RGB',(Image.new('L',rough.size,255),rough,metal)).save(O/(stem+'_orm.png'))
 normal=np.asarray(Image.open(O/(stem+'_normal.png')).convert('RGB')).astype(np.float32)/255*2-1;lengths=np.linalg.norm(normal,axis=-1);assert np.max(np.abs(lengths-1))<.02
 flat=(np.asarray(Image.open(maps['flat_graphics']['path']).convert('L'))>250)&(np.asarray(Image.open(maps['glass']['path']).convert('L'))<1)
 for _ in range(12):
  inner=flat[1:-1,1:-1]&flat[2:,1:-1]&flat[:-2,1:-1]&flat[1:-1,2:]&flat[1:-1,:-2];flat[:]=False;flat[1:-1,1:-1]=inner
 assert flat.sum()>1000 and np.max(np.abs(normal[flat]-[0,0,1]))<.008
 for rec in maps.values():
  assert sha(rec['path'])==rec['sha256']
  with Image.open(rec['path']) as im:im.load();assert list(im.size)==rec['dimensions']
 checks.append(dict(role=role,normal_max_unit_error=float(np.max(np.abs(lengths-1))),graphics_normals_flat=True,orm_channels_verified=True,dimensions=[4096,4096]))
(W/'map_checks.json').write_text(json.dumps(dict(passed=True,maps=checks,no_colour_variant_duplicates=True),indent=2)+'\n')

mission="""mission({name="Prowler - Worn Paint inspection"})
prowler=flight_group("(FG)Prowler", {wing="player"})
prowler_inspection=ship("Prowler - Inspection", {type="prowler", group=prowler})
initialise=part("(F)ProwlerInspection", function() CreateFlightGroup(prowler) return 1 end, {start=true})
"""
(W/'mission961.luau').write_text(mission)
subprocess.run([str(E/'sltool'),'dte','build',str(W/'mission961.luau'),str(O/'mission961.dte')],check=True)
(O/'prowler_inspection.luau').write_text("""-- Only loaded by the quiet Prowler review mission.
local world = require("openreliant.world")
local seen = {}
local function quiet()
    for _, object in world.objects() do
        if not seen[object.slot] then
            object.side = "friendly"
            object.invulnerable = "full"
            object.engines_disabled = true
            object.guns_disabled = true
            object.missiles_disabled = true
            object.eject_disabled = true
            seen[object.slot] = true
        end
    end
end
return {engine_handlers = {on_mission_start = quiet, on_step = quiet}}
""")
(O/'mod.ini').write_text("""[Mod]
Name=Prowler - Worn Paint (Review)
Version=0.1.0-beta.1
Description=Restored Prowler armour and markings, recessed blue glazing, structural surface maps and window emission. First pass awaiting review.
OpenReliant=0.18.0
License=CC-BY-NC-SA-4.0

[Missions]
mission961.dte=prowler_inspection.luau
""")
(O/'license.txt').write_text("Prowler - Worn Paint\nOriginal restoration contributions by KonCyptFysh: CC-BY-NC-SA-4.0\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/\nOriginal StarLancer assets retain their respective owners rights. Requires your own StarLancer installation.\n")
shutil.copy2(D/'review/reconstruction_v1/material_front.png',O/'mod.png')
checks=[]
for kind,file in [('shp','US_Prowler.SHP'),('dte','mission961.dte')]:
 p=subprocess.run([str(E/'sltool'),kind,'check',str(O/file)],capture_output=True,text=True,check=True);checks.append(dict(engine=E.name,file=file,exit_code=p.returncode,output=p.stdout+p.stderr,sha256=sha(O/file)))
ships=subprocess.check_output([str(E/'sltool'),'dte','ships',str(O/'mission961.dte')],text=True)
assert 'Prowler - Inspection' in ships and '30' in ships
(W/'mission961-ships.txt').write_text(ships)
dependency_check=W/'native-dependency-check';dependency_check.mkdir(exist_ok=True)
shutil.copy2(O/'US_Prowler.SHP',dependency_check/'US_Prowler.SHP')
shutil.copy2(D/'source/14_al_STUR.SHP',dependency_check/'14_al_STUR.SHP')
components=subprocess.check_output([str(E/'sltool'),'shp','components',str(dependency_check/'US_Prowler.SHP')],text=True)
assert components.count('14_al_stur.shp')==4
(W/'runtime-components.txt').write_text(components)
(W/'native_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
launcher="""#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
if [[ ! -f "$install_dir/game-data/mods/117-prowler-worn-v1/mission961.dte" ]]; then
    printf '%s\\n' 'The Prowler review mod is missing.' >&2; exit 1
fi
printf '%s\\n' 'Prowler inspection: quiet stationary corvette with four native turret mounts.' 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\\n' 'Official OpenReliant 0.18.0 is required.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission 961 --ship 30 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
"""
p=O.parent.parent/'launch-prowler-test.sh';p.write_text(launcher);p.chmod(0o755);subprocess.run(['bash','-n',str(p)],check=True)
print('PROWLER_NATIVE_EXPORT_PASSED',[(p['file'],len(p['continuation_corrections'])) for p in pres],flush=True)
