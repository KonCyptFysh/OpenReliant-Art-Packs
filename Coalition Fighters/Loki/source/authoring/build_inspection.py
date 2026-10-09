import os
from pathlib import Path
import json,struct,subprocess,shutil,hashlib
D=Path(str(Path(os.environ['LOKI_WORKSPACE'])));W=D/'work/reconstruction_v1';O=D/'exports/openreliant_v1/mods/105-loki-worn-v1';O.mkdir(parents=True,exist_ok=True)
tool=Path(str(Path(os.environ['OPENRELIANT_HOME']) / 'releases/openreliant-v0.7.0-linux-x86_64/sltool'))
def build(mode):
 strings=bytearray()
 def name(s):
  off=len(strings);strings.extend(s.encode()+b'\0');return off
 partnames=[name('(F)LokiInspection'),name('(F)CycleLegs')]
 shipnames=[name('Loki - Inspection')]
 groupnames=[name('(FG)Loki')]
 ships=[]
 for i in range(1):
  s=bytearray(76);struct.pack_into('<IHH',s,0,i,shipnames[i],0);s[20:24]=bytes([0 if i==0 else 1,255,0,0]);struct.pack_into('<H',s,24,65 if i==0 else 92)
  struct.pack_into('<HBB',s,40,65535 if i==0 else 45,255,255 if i==0 else i-1)
  struct.pack_into('<IHH',s,48,0xffffffff,65535,65535);s[60:72]=bytes.fromhex('ff ff 00 00 ff ff ff ff 00 00 00 00');ships.append(bytes(s))
 groups=b''.join(struct.pack('<HHHHBBHII',1+i,0,groupnames[i],0,0 if i==0 else 255,1 if i==0 else 4,0,0 if i==0 else 1,0xff19ffff) for i in range(1))
 objects=b''.join(struct.pack('<BBHI',0 if i<1 else 1,0,65535,0) for i in range(2))
 num=lambda n:bytes([0x32,n]);command=lambda n:bytes([0x21,n]);ship=lambda n:bytes([0x2c,n]);group=lambda n:bytes([0x2d,n]);wait=lambda n:num(n)+command(5)
 track_name=b'fighting position\0';track=bytes([0x2b,len(track_name)+1])+track_name
 deploy=ship(0)+track+command(0x11);stow=ship(0)+track+command(0x3d);ret=num(1)+bytes([0x43])
 init=group(0)+command(3)
 if mode=='fighting':init+=deploy
 if mode=='cycle':init+=wait(7)+num(1)+num(1)+num(24)+num(0)+command(1)+bytes([0x22,1])
 init+=ret
 cycle=deploy+wait(11)+stow+wait(11)+ret
 script=bytearray();parts=[]
 for i,code in enumerate([init,cycle]):
  offset=len(script);length=(len(code)+2+3)&~3;block=struct.pack('<H',length)+code;block+=bytes(length-len(block));script.extend(block)
  p=bytearray(28);struct.pack_into('<H',p,0,partnames[i]);struct.pack_into('<H',p,10,offset//2);p[12]=int(i==0);struct.pack_into('<H',p,16,length//2);parts.append(bytes(p))
 title=('Loki inspection - '+mode).encode();title=struct.pack('<4sHH',b'ORMN',1,len(title))+title+b'\0'
 sections={0:(len(strings),strings),3:(1,b''.join(ships)),4:(1,groups),6:(len(script)//2,script),7:(2,objects),8:(2,b''.join(parts)),10:(len(script),bytes(len(script))),21:(len(title),title)}
 result=bytearray(216)
 for i in range(27):
  if i in sections:
   count,payload=sections[i];result.extend(bytes(-len(result)%4));offset=len(result);result.extend(payload)
  else:count,offset=0,65535
  struct.pack_into('<HBBI',result,i*8,count,0,15,offset)
 return result
checks=[]
for mode,number in [('folded',983),('fighting',982),('cycle',981)]:
 p=O/f'mission{number}.dte';p.write_bytes(build(mode))
 out=subprocess.check_output([str(tool),'dte','check',str(p)],text=True);script=subprocess.check_output([str(tool),'dte','script',str(p)],text=True);ships=subprocess.check_output([str(tool),'dte','ships',str(p)],text=True)
 assert 'not an opcode' not in script and ('StartShipAnimation' in script);(W/f'mission{number}-script.txt').write_text(script);(W/f'mission{number}-ships.txt').write_text(ships);checks.append(dict(mode=mode,mission=number,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),check=out,retail_data_copied=False,carried_torpedoes=0))
(W/'inspection-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(O/'loki_inspection.luau').write_text('''-- Only the Loki inspection missions load this diagnostic script.
local world = require("openreliant.world")
local function configure(object)
    object.side = "friendly"
    object.invulnerable = "full"
    object.guns_disabled = true
    object.engines_disabled = true
    object.missiles_disabled = true
    object.eject_disabled = true
end
return {engine_handlers = {
on_mission_start = function()
    for _, object in world.objects() do configure(object) end
end,
on_step = function()
    for _, object in world.objects() do configure(object) end
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
    folded) mission=983 ;;
    fighting) mission=982 ;;
    cycle) mission=981 ;;
    *) printf '%s\\n' 'Usage: launch-loki-test.sh [folded|fighting|cycle] [engine options]' >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
if [[ ! -f "$install_dir/game-data/mods/105-loki-worn-v1/mission$mission.dte" ]]; then
    printf '%s\\n' 'The Loki review mod is missing.' >&2; exit 1
fi
printf '%s\\n' "Loki inspection: $mode, native articulated leg and foot poses." 'Press 7 for orbit; arrow keys rotate; Shift+Up/Down zoom; 0 saves a screenshot.'
if [[ "$mode" == cycle ]]; then printf '%s\\n' 'Starts folded, then repeatedly moves to fighting position and folds back. Each movement takes four seconds with pauses between.'; fi
if [[ "$mode" == fighting ]]; then printf '%s\\n' 'Allow four seconds for the native animation; the fighting pose then holds.'; fi
unset XDG_ACTIVATION_TOKEN
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-x11}"
engine="$install_dir/releases/openreliant-v0.7.0-linux-x86_64/openreliant"
if [[ ! -x "$engine" ]]; then printf '%s\\n' 'Official OpenReliant 0.7.0 is required for this review launcher.' >&2; exit 1; fi
exec "$engine" "$install_dir/game-data" --mission "$mission" --ship 65 --view 1 --no-sound --size 1920x1080 --fps 60 "$@"
'''
p=D/'exports/launch-loki-test.sh';p.write_text(launcher);p.chmod(0o755);subprocess.run(['bash','-n',str(p)],check=True)

print('Built three single-Loki missions: folded, fighting position, cycle. All pass native validation.')
