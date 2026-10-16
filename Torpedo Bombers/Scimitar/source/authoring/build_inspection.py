from pathlib import Path
import json,struct,subprocess,shutil,hashlib
D=Path('${SCIMITAR_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_8_v1/mods/115-scimitar-worn-v1';O.mkdir(parents=True,exist_ok=True)
tool=Path('${OPENRELIANT_HOME}/releases/openreliant-v0.18.0-linux-x86_64/sltool')
def build(mode):
 strings=bytearray()
 def name(s):
  off=len(strings);strings.extend(s.encode()+b'\0');return off
 partnames=[name('(F)ScimitarInspection'),name('(F)Unused')]
 shipnames=[name('Scimitar - Inspection')]+[name('Carried torpedo '+str(i+1)) for i in range(2)]
 groupnames=[name('(FG)Scimitar'),name('(FG)Torpedoes')]
 ships=[]
 for i in range(3):
  s=bytearray(76);struct.pack_into('<IHH',s,0,i,shipnames[i],0);s[20:24]=bytes([0 if i==0 else 1,255,0,0]);struct.pack_into('<H',s,24,48 if i==0 else 92)
  struct.pack_into('<HBB',s,40,65535 if i==0 else 48,255,255 if i==0 else i-1)
  struct.pack_into('<IHH',s,48,0xffffffff,65535,65535);s[60:72]=bytes.fromhex('ff ff 00 00 ff ff ff ff 00 00 00 00');ships.append(bytes(s))
 groups=b''.join(struct.pack('<HHHHBBHII',3+i,0,groupnames[i],0,0 if i==0 else 255,1 if i==0 else 2,0,0 if i==0 else 1,0xff19ffff) for i in range(2))
 objects=b''.join(struct.pack('<BBHI',0 if i<3 else 1,0,65535,0) for i in range(5))
 num=lambda n:bytes([0x32,n]);command=lambda n:bytes([0x21,n]);ship=lambda n:bytes([0x2c,n]);group=lambda n:bytes([0x2d,n]);wait=lambda n:num(n)+command(5)
 ret=num(1)+bytes([0x43])
 init=group(0)+command(3)+group(1)+command(3)
 if mode=='launch':init+=wait(8)+ship(1)+command(0x14)+wait(6)+ship(2)+command(0x14)
 init+=ret
 script=bytearray();parts=[]
 for i,code in enumerate([init]):
  offset=len(script);length=(len(code)+2+3)&~3;block=struct.pack('<H',length)+code;block+=bytes(length-len(block));script.extend(block)
  p=bytearray(28);struct.pack_into('<H',p,0,partnames[i]);struct.pack_into('<H',p,10,offset//2);p[12]=int(i==0);struct.pack_into('<H',p,16,length//2);parts.append(bytes(p))
 title=('Scimitar inspection - '+mode).encode();title=struct.pack('<4sHH',b'ORMN',1,len(title))+title+b'\0'
 sections={0:(len(strings),strings),3:(3,b''.join(ships)),4:(2,groups),6:(len(script)//2,script),7:(5,objects),8:(1,b''.join(parts)),10:(len(script),bytes(len(script))),21:(len(title),title)}
 result=bytearray(216)
 for i in range(27):
  if i in sections:
   count,payload=sections[i];result.extend(bytes(-len(result)%4));offset=len(result);result.extend(payload)
  else:count,offset=0,65535
  struct.pack_into('<HBBI',result,i*8,count,0,15,offset)
 return result
checks=[]
for mode,number in [('stowed',964),('launch',963)]:
 p=O/f'mission{number}.dte';p.write_bytes(build(mode))
 source=W/f'mission{number}.luau';source.write_text(subprocess.check_output([str(tool),'dte','decompile',str(p)],text=True))
 subprocess.run([str(tool),'dte','build',str(source),str(p)],check=True)
 out=subprocess.check_output([str(tool),'dte','check',str(p)],text=True);script=subprocess.check_output([str(tool),'dte','script',str(p)],text=True);ships=subprocess.check_output([str(tool),'dte','ships',str(p)],text=True)
 (W/f'mission{number}-script.txt').write_text(script);(W/f'mission{number}-ships.txt').write_text(ships);checks.append(dict(mode=mode,mission=number,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),check=out,retail_data_copied=False,carried_torpedoes=2))
(W/'inspection-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(O/'scimitar_inspection.luau').write_text('''-- Only the two Scimitar inspection missions load this diagnostic script.
local world = require("openreliant.world")
local util = require("openreliant.util")
local hooks = require("openreliant.hooks")
local steps = 0
local seen = {}
local function configure(object)
    if seen[object.slot] then return end
    seen[object.slot] = true
    object.side = "friendly"
    object.invulnerable = "full"
    object.guns_disabled = true
    if object.is_player then
        object.engines_disabled = true
        object.missiles_disabled = true
        object.eject_disabled = true
    end
end
hooks.after("object_damage", function(e)
    print("SCIMITAR_DAMAGE", steps, e.object.slot, e.kind, e.value)
end)
hooks.after("vm_command", function(e)
    if e.command == "start_ship_animation" or e.command == "start_ship_animation_reverse" then
        print("SCIMITAR_ANIMATION", steps, e.command)
    end
end)
return {engine_handlers = {
on_mission_start = function(mission)
    for _, object in world.objects() do configure(object) end
    if world.player then world.player.missiles_disabled = true end
end,
on_mission_end = function(outcome) print("SCIMITAR_MISSION_END", steps, outcome.ending) end,
on_step = function()
    steps += 1
    for _, object in world.objects() do configure(object) end
    if steps % 25 ~= 0 or not world.player then return end
    for _, object in world.objects() do
        if object.type == "russian_torpedo" then
            local p = util.to_local(world.player.position, world.player.orientation, object.position)
            print("SCIMITAR_TORPEDO", steps, object.slot, object.order, p.x, p.y, p.z)
        end
    end
end}}
''')
launcher='''#!/usr/bin/env bash
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -x "$script_dir/launch-openreliant.sh" ]]; then
    install_dir="$script_dir"
else
    install_dir="${OPENRELIANT_HOME:-$HOME/Games/OpenReliant}"
fi
mode="${1:-stowed}"
case "$mode" in
    stowed) mission=964 ;;
    launch) mission=963 ;;
    *) printf '%s\\n' 'Usage: launch-scimitar-test.sh [stowed|launch] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/115-scimitar-worn-v1/mission$mission.dte" ]]; then
    printf '%s\\n' 'The Scimitar review mod is missing.' >&2; exit 1
fi
printf '%s\\n' "Scimitar inspection: $mode, with two carried torpedoes." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == launch ]]; then printf '%s\\n' 'Timed review: release the first torpedo after about 9 seconds and the second roughly 7 seconds later. The native launch mounts are fixed.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.18.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\\n' 'Official OpenReliant 0.18.0 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 48 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
'''
p=D/'exports/openreliant_0_8_v1/launch-scimitar-test.sh';p.write_text(launcher);p.chmod(0o755);subprocess.run(['bash','-n',str(p)],check=True)
if Path(__file__).resolve() != (W/'build_inspection.py').resolve():shutil.copy2(__file__,W/'build_inspection.py')
print('Built two native missions: carried torpedoes and timed release. All pass sltool validation.')
