from pathlib import Path
import numpy as np,json,shutil,struct
D=Path('${RELIANT_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';O.mkdir(parents=True,exist_ok=True)
P=Path('${OPENRELIANT_HOME}/game-data/mods/117-prowler-worn-v1')
parts=json.loads((D/'source/native_parts.json').read_text())
nozzles=[dict(name='central',center=[-127.84,-45.23],back=178,front=-800,radius=1400),dict(name='port',center=[-4061.51,-45.23],back=1920,front=1090,radius=1400),dict(name='starboard',center=[3822.75,-45.23],back=1920,front=1090,radius=1400)]
def tri(lod,f):
 v=np.array([lod['vertices'][j] for j in f['vertices']],float);n=np.cross(v[1]-v[0],v[2]-v[0]);n/=max(np.linalg.norm(n),1e-10)
 if np.dot(n,f['normal'])<0:n=-n
 return v,n
for q in nozzles:
 q['planes']=[];q['faces']=[];verts=[]
 for li,l in enumerate(parts[19]['lods']):
  for f in l['faces']:
   v,n=tri(l,f);c=v.mean(0);radial=c[:2]-q['center'];dot=np.dot(radial,n[:2]);rad=np.linalg.norm(radial)
   disk=abs(c[2]-q['back'])<3 and n[2]<-.995
   petal=q['front']<c[2]<q['back'] and -.7<n[2]<-.1 and dot< -100
   if (disk or petal) and rad<q['radius'] and not f['hidden']:
    plane=np.r_[n,np.dot(n,v[0])]
    if not any(np.linalg.norm(plane[:3]-p[:3])<1e-5 and abs(plane[3]-p[3])<.25 for p in q['planes']):q['planes'].append(plane)
    q['faces'].append([19,li,f['id']]);verts.extend(v)
 v=np.array(verts);q['lo']=v.min(0)-.5;q['hi']=v.max(0)+.5
 print(q['name'],'planes',len(q['planes']),'faces',len(q['faces']))
 # Validate all native part-local coordinate frames, including damaged and reduced detail models.
 false=[];hits=[]
 for p in parts:
  for li,l in enumerate(p['lods']):
   for f in l['faces']:
    if f['hidden']:continue
    v,n=tri(l,f)
    for c in [v.mean(0),*(v.mean(0)*.25+v*.75)]:
     hit=np.all(c>=q['lo']) and np.all(c<=q['hi']) and any(np.dot(n,pl[:3])>.99995 and abs(np.dot(c,pl[:3])-pl[3])<.35 for pl in q['planes'])
     if hit:
      key=[p['index'],li,f['id']]
      if key not in hits:hits.append(key)
      if key not in q['faces'] and key not in false:false.append(key)
 assert not false,(q['name'],false)
 assert all(f in hits for f in q['faces'])
 q['audit_hits']=hits
helpers=(P/'prowler_systems.glsl').read_text().split('const vec4 planes0')[0].replace('pr18_','rl18_')
shader=helpers
fmt=lambda a:','.join(f'{x:.7f}' for x in a)
for i,q in enumerate(nozzles):
 planes=q['planes'];shader+=f"\nconst vec4 planes{i}[{len(planes)}] = vec4[]("+','.join('vec4('+fmt(p)+')' for p in planes)+');\n'
 shader+=f'''float nozzle{i}(vec3 at, vec3 normal) {{
 if (any(lessThan(at,vec3({fmt(q['lo'])}))) || any(greaterThan(at,vec3({fmt(q['hi'])})))) return 0.0;
 for(int j=0;j<{len(planes)};j++) {{vec4 p=planes{i}[j];if(dot(normal,p.xyz)>.99995 && abs(dot(at,p.xyz)-p.w)<.35) return 1.0;}}
 return 0.0;
}}
'''
shader+='''void surface(inout Surface s, vec4 parameters, float time) {
 s.glow *= clamp(parameters.x,0.0,1.0);
 vec3 geometric=cross(dFdx(s.local),dFdy(s.local));
 geometric/=max(length(geometric),0.000001);
 if(dot(geometric,objectDirection(s.toEye))<0.0) geometric=-geometric;
 float drive=clamp(parameters.y,0.0,1.0),heat=clamp(parameters.z,0.0,1.0),thermal=0.0;
'''
for i,q in enumerate(nozzles):
 center=q['center']+[q['front']-250];reach=3300 if i==0 else 2800
 shader+=f' float n{i}=nozzle{i}(s.local,geometric);\n if(n{i}>0.0) s.glow+=rl18_engine_spill(s,drive,vec3({fmt(center)}),{reach}.0);\n thermal=max(thermal,n{i});\n'
shader+=''' float detail=.45+.55*clamp(dot(s.color,vec3(.2126,.7152,.0722))*2.0,0.0,1.0);
 s.glow+=thermal*detail*(.16*drive+.46*heat)*mix(vec3(.65,.035,.005),vec3(1.0,.20,.025),heat);
 s.glow*=clamp(parameters.w,0.0,1.0);
}
'''
(O/'reliant_systems.glsl').write_text(shader)
(W/'nozzle-audit.json').write_text(json.dumps({'passed':True,'scope':'all 24 native part coordinate frames and all LODs, face centroid plus three inset corners; no exterior vents selected','nozzles':nozzles},default=lambda o:o.tolist(),indent=2)+'\n')
for name in ['response','surface','inspection','lighting']:
 s=(P/f'prowler_{name}.luau').read_text().replace('prowler','reliant').replace('Prowler','Reliant').replace('PROWLER','RELIANT').replace('961','959')
 if name=='lighting':
  s=s.replace('local dead = ship.exploding or ship.ejected','''local engine_health = 1
        local engine_destroyed = false
        for _, part in ship:parts() do
            if part.class == "engine" and part.component ~= nil then
                engine_destroyed = engine_destroyed or part.destroyed
                if part.full_armor and part.full_armor > 0 then
                    engine_health = math.min(engine_health, math.clamp((part.armor or 0) / part.full_armor, 0, 1))
                end
            end
        end
        local engine_off = ship.engines_disabled or engine_destroyed or engine_health <= 0
        local dead = ship.exploding or ship.ejected''')
  s=s.replace('ship.throttle, ship.engines_disabled,','ship.throttle * engine_health, engine_off,').replace('engine_off = ship.engines_disabled,','engine_off = engine_off, engine_health = engine_health, engine_destroyed = engine_destroyed,')
 if name=='surface':
  s=s.replace('mission.number == 959','mission.number == 959 or mission.number == 958')
  s=s.replace('or key == "f9"','or key == "f9" or key == "f10" or key == "f12"')
  s=s.replace('F9 engines",','F9 engines   F10 critical   F12 destroy engine",').replace('Spill %.0f%%','Drive %.0f%%')
 if name=='inspection':
  s=s.replace('elseif data.key == "f6" or','''elseif data.key == "f12" then
            ships(function(ship)
                for _, part in ship:parts() do
                    if part.class == "engine" and part.component ~= nil and not part.destroyed then ship:destroy_component(part.component) end
                end
            end)
        elseif data.key == "f6" or''')
  s=s.replace('or data.key == "f8" then','or data.key == "f8" or data.key == "f10" then')
  s=s.replace('if data.key == "f8" then','''if data.key == "f10" then
                    ship.armor = {left=full*.25,right=full*.25,fore=full*.25,aft=full*.25}
                elseif data.key == "f8" then''')
 if name=='inspection':
  s=s.replace('local homes = {}','local homes = {}\nlocal home_facing = {}').replace('homes[key] = ship.position','homes[key] = ship.position\n            home_facing[key] = ship.orientation').replace('ship.position = homes[key]','ship.position = homes[key]\n        ship.orientation = home_facing[key]')
 (O/f'reliant_{name}.luau').write_text(s)
shutil.copy2(P/'LICENSE-OpenReliant.txt',O/'LICENSE-OpenReliant.txt')
# Pure response regression checks, including no fake impact on spawn, threshold, thermal decay and full-range faults.
s=(D.parent.parent/'Prowler/worn/work/nozzle_surge_v3/test_response.luau').read_text().replace('prowler_response','reliant_response')
(W/'test_response.luau').write_text(s);shutil.copy2(O/'reliant_response.luau',W/'reliant_response.luau')
print('RELIANT_LIGHTING_BUILT')
