from pathlib import Path
import json,subprocess,os,sys,shutil,numpy as np
D=Path('${RELIANT_WORKSPACE}');W=D/'work/machinery_v9';P=Path('/tmp/reliant-refinement-probe/mods/119-reliant-worn-v1');E=Path('${OPENRELIANT_HOME}/releases/openreliant-v0.18.0-linux-x86_64/openreliant')
views=json.loads((D/'work/alignment_v4/camera-views.json').read_text());views['forward-windows']={'target':[5271,150,-1400],'position':[8300,-100,-1000]}
views['machinery-opposite']={'target':[-5165.95,17.741,-12795.851],'position':[-12965.95,-103.189,-12545.851]}
which=sys.argv[1];revision=sys.argv[2] if len(sys.argv)>2 else 'v9';yaw=float(sys.argv[3]) if len(sys.argv)>3 else 0
light=float(sys.argv[4]) if len(sys.argv)>4 else -1
tier=sys.argv[5] if len(sys.argv)>5 else '4k'
source=D/('maps/opaque_glass_v8' if revision=='v8' else 'maps/machinery_v9')
if tier!='4k': source=D/f'exports/review_v1_{tier}/mods/119-reliant-worn-v1'
for suffix in ['', '_emissive', '_normal', '_orm']:shutil.copy2(source/f'orr2_hull{suffix}.png',P/f'orr2_hull{suffix}.png')
natives=D/'work/uv_projection_v7/native'
for name in ['Reliant.SHP','Reliant_destback.SHP']:shutil.copy2(natives/name,P/name)
views['forward-panel']={'target':[5271,220,-2336.96],'position':[10071,220,-2336.96]}
views['port-panel']={'target':[-5120,143,-2336.96],'position':[-9920,143,-2336.96]}
views['bridge-distant']={k:list(v) for k,v in views['bridge-cell'].items()}
v=views['bridge-distant'];v['position']=(np.array(v['target'])+2.5*(np.array(v['position'])-v['target'])).tolist()
v=views[which];vec=lambda a:','.join(str(x) for x in a)
s='''local self=require("openreliant.self")
local camera=require("openreliant.camera")
local util=require("openreliant.util")
local core=require("openreliant.core")
local n=0
local view=camera.register_view("reliant_probe",{letterbox=false,frame=function(ship,dt)
 local target=vector.create(TARGET)
 local pos=vector.create(POSITION)
 target=util.to_world(ship.position,ship.orientation,target)
 pos=util.to_world(ship.position,ship.orientation,pos)
 return {position=pos,orientation=util.look_at(target-pos)}
end})
return {engine_handlers={on_frame=function(dt) n+=1;ROTATE OVERRIDE if n==15 then camera.set_view(view,self) end end}}
'''.replace('TARGET',vec(v['target'])).replace('POSITION',vec(v['position'])).replace('ROTATE',f'if n==10 then core.send_global_event("reliant_rotate",{{yaw={yaw},seconds=.1}}) end;' if yaw else '')
s=s.replace('OVERRIDE',f'if n>20 then self:set_surface("119-reliant-worn-v1:reliant_systems",{{{light},0,0,0}}) end;' if light>=0 else '')
(P/'camera_probe.luau').write_text(s)
name=f'{revision}-{which}'+('-rotated' if yaw else '')+(f'-light{light:g}' if light>=0 else '')+(f'-{tier}' if tier!='4k' else '');out=W/(name+'.png');log=W/(name+'.log');env=os.environ.copy();env.pop('XDG_ACTIVATION_TOKEN',None);env['SDL_VIDEODRIVER']='x11'
with log.open('w') as f:ret=subprocess.run([str(E),str(P.parent.parent),'--mods',P.name,'--mission','959','--ship','12','--view','1','--no-sound','--size','1400x1000','--no-update-check','--screenshot',str(out),'--screenshot-ticks','100'],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=55)
assert ret.returncode==0;assert out.exists();s=log.read_text();assert not any(x in s.lower() for x in ['warning(scripts)','warning(library)','error(']);print(out,flush=True)
