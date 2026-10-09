import os
from pathlib import Path
import json,struct,subprocess,shutil,hashlib
D=Path(str(Path(os.environ['KAMOV_WORKSPACE'])));W=D/'work/reconstruction_v1';O=D/'exports/openreliant_v1/mods/104-kamov-worn-v1';O.mkdir(parents=True,exist_ok=True)
tool=Path(str(Path(os.environ['OPENRELIANT_HOME']) / 'releases/openreliant-v0.7.0-linux-x86_64/sltool'))
def build(mode):
 strings=bytearray()
 def name(s):
  off=len(strings);strings.extend(s.encode()+b'\0');return off
 partnames=[name('(F)KamovInspection'),name('(F)CycleBays')]
 shipnames=[name('Kamov - Inspection')]+[name('Carried torpedo '+str(i+1)) for i in range(4)]
 groupnames=[name('(FG)Kamov'),name('(FG)Torpedoes')]
 ships=[]
 for i in range(5):
  s=bytearray(76);struct.pack_into('<IHH',s,0,i,shipnames[i],0);s[20:24]=bytes([0 if i==0 else 1,255,0,0]);struct.pack_into('<H',s,24,45 if i==0 else 92)
  struct.pack_into('<HBB',s,40,65535 if i==0 else 45,255,255 if i==0 else i-1)
  struct.pack_into('<IHH',s,48,0xffffffff,65535,65535);s[60:72]=bytes.fromhex('ff ff 00 00 ff ff ff ff 00 00 00 00');ships.append(bytes(s))
 groups=b''.join(struct.pack('<HHHHBBHII',5+i,0,groupnames[i],0,0 if i==0 else 255,1 if i==0 else 4,0,0 if i==0 else 1,0xff19ffff) for i in range(2))
 objects=b''.join(struct.pack('<BBHI',0 if i<5 else 1,0,65535,0) for i in range(7))
 num=lambda n:bytes([0x32,n]);command=lambda n:bytes([0x21,n]);ship=lambda n:bytes([0x2c,n]);group=lambda n:bytes([0x2d,n]);wait=lambda n:num(n)+command(5)
 track=bytes([0x2b,8])+b'deploy\0'
 deploy=ship(0)+track+command(0x11);stow=ship(0)+track+command(0x3d);ret=num(1)+bytes([0x43])
 init=group(0)+command(3)+group(1)+command(3)
 if mode=='deployed':init+=deploy
 if mode=='cycle':init+=wait(7)+num(1)+num(1)+num(24)+num(0)+command(1)+bytes([0x22,1])
 if mode=='launch':init+=group(1)+command(0x3a)+stow
 init+=ret
 cycle=deploy+wait(11)+stow+wait(11)+ret
 script=bytearray();parts=[]
 for i,code in enumerate([init,cycle]):
  offset=len(script);length=(len(code)+2+3)&~3;block=struct.pack('<H',length)+code;block+=bytes(length-len(block));script.extend(block)
  p=bytearray(28);struct.pack_into('<H',p,0,partnames[i]);struct.pack_into('<H',p,10,offset//2);p[12]=int(i==0);struct.pack_into('<H',p,16,length//2);parts.append(bytes(p))
 title=('Kamov inspection - '+mode).encode();title=struct.pack('<4sHH',b'ORMN',1,len(title))+title+b'\0'
 sections={0:(len(strings),strings),3:(5,b''.join(ships)),4:(2,groups),6:(len(script)//2,script),7:(7,objects),8:(2,b''.join(parts)),10:(len(script),bytes(len(script))),21:(len(title),title)}
 result=bytearray(216)
 for i in range(27):
  if i in sections:
   count,payload=sections[i];result.extend(bytes(-len(result)%4));offset=len(result);result.extend(payload)
  else:count,offset=0,65535
  struct.pack_into('<HBBI',result,i*8,count,0,15,offset)
 return result
checks=[]
for mode,number in [('stowed',987),('deployed',986),('cycle',985),('launch',984)]:
 p=O/f'mission{number}.dte';p.write_bytes(build(mode))
 out=subprocess.check_output([str(tool),'dte','check',str(p)],text=True);script=subprocess.check_output([str(tool),'dte','script',str(p)],text=True);ships=subprocess.check_output([str(tool),'dte','ships',str(p)],text=True)
 (W/f'mission{number}-script.txt').write_text(script);(W/f'mission{number}-ships.txt').write_text(ships);checks.append(dict(mode=mode,mission=number,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),check=out,retail_data_copied=False,carried_torpedoes=4))
(W/'inspection-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(O/'kamov_inspection.luau').write_text('''-- Only the four Kamov inspection missions load this diagnostic script.
local world = require("openreliant.world")
local util = require("openreliant.util")
local hooks = require("openreliant.hooks")
local steps = 0
local allow_launch = false
local seen = {}
local function configure(object)
    if seen[object.slot] then return end
    seen[object.slot] = true
    object.side = "friendly"
    object.invulnerable = "full"
    object.guns_disabled = true
    if object.is_player then
        object.engines_disabled = true
        object.missiles_disabled = not allow_launch
        object.eject_disabled = true
    end
end
hooks.after("object_damage", function(e)
    print("KAMOV_DAMAGE", steps, e.object.slot, e.kind, e.value)
end)
hooks.after("vm_command", function(e)
    if e.command == "start_ship_animation" or e.command == "start_ship_animation_reverse" then
        print("KAMOV_ANIMATION", steps, e.command)
    end
end)
return {engine_handlers = {
on_mission_start = function(mission)
    allow_launch = mission.number == 984
    for _, object in world.objects() do configure(object) end
    if world.player then world.player.missiles_disabled = not allow_launch end
end,
on_mission_end = function(outcome) print("KAMOV_MISSION_END", steps, outcome.ending) end,
on_step = function()
    steps += 1
    for _, object in world.objects() do configure(object) end
    if steps % 25 ~= 0 or not world.player then return end
    for _, object in world.objects() do
        if object.type == "russian_torpedo" then
            local p = util.to_local(world.player.position, world.player.orientation, object.position)
            print("KAMOV_TORPEDO", steps, object.slot, object.order, p.x, p.y, p.z)
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
mode="${1:-cycle}"
case "$mode" in
    stowed) mission=987 ;;
    deployed) mission=986 ;;
    cycle) mission=985 ;;
    launch) mission=984 ;;
    *) printf '%s\\n' 'Usage: launch-kamov-test.sh [stowed|deployed|cycle|launch] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/104-kamov-worn-v1/mission$mission.dte" ]]; then
    printf '%s\\n' 'The Kamov review mod is missing.' >&2; exit 1
fi
printf '%s\\n' "Kamov inspection: $mode, with four carried torpedoes." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == cycle ]]; then printf '%s\\n' 'Starts stowed for 8 seconds, then repeats: 4 seconds opening, 8 open, 4 closing, 8 closed.'; fi
if [[ "$mode" == deployed ]]; then printf '%s\\n' 'Allow 4 seconds for the native deployment, then the bays remain open.'; fi
if [[ "$mode" == launch ]]; then printf '%s\\n' 'Use your Launch Missile control to release each torpedo. After all four launch, the bays stow.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.7.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\\n' 'Official OpenReliant 0.7.0 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 45 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
'''
p=D/'exports/launch-kamov-test.sh';p.write_text(launcher);p.chmod(0o755);subprocess.run(['bash','-n',str(p)],check=True)
shutil.copy2(__file__,W/'build_inspection.py')
print('Built four native missions: stowed, deployed, continuous cycle and player launch. All pass sltool validation.')
