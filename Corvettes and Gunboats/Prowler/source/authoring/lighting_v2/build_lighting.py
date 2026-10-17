from pathlib import Path
import json,struct,shutil,hashlib,numpy as np
D=Path('${PROWLER_WORKSPACE}');W=D/'work/lighting_v2';O=D/'exports/openreliant_0_18_v2/mods/117-prowler-worn-v1';K=D.parents[1]/'Kurgen/worn/exports/openreliant_0_18_v8/mods/116-kurgen-worn-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
parts=json.loads((D/'source/native_parts.json').read_text())
# Fingerprints of native nozzle planes disambiguate local coordinates of separate parts.
# Thermal masks contain only recessed faces. No geometry, material, UV or normal changes.
groups=[]
for pi,fast,heat,center in [(1,[8,9]+list(range(28,44)),[8,9,30,31,35,36,37,38,41,42],[6.418,-.968,-780]),(3,[8,9]+list(range(28,44)),[8,9,28,29,32,36,37,38,39,40],[-10.572,2.617,-791.5]),(2,list(range(150,198)),list(range(150,158))+list(range(178,198)),[-2.6,289.3,-1640])]:
 lod=parts[pi]['lods'][0];v=np.array(lod['vertices']);allpts=[];planes=[]
 for fi in fast:
  f=lod['faces'][fi];xyz=v[f['vertices']];allpts.extend(xyz);n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);n/=np.linalg.norm(n)
  if n@np.array(f['normal'])<0:n=-n
  p=np.r_[n,n@xyz[0]]
  if not any(np.linalg.norm(p-q['plane'])<.03 for q in planes):planes.append(dict(plane=p,heat=fi in heat))
 pts=np.array(allpts);groups.append(dict(part=pi,planes=planes,lo=pts.min(0)-.5,hi=pts.max(0)+.5,center=np.array(center)))

def mask(pts,n,g,thermal=False):
 inside=np.all((pts>=g['lo'])&(pts<=g['hi']),axis=1);out=np.zeros(len(pts),bool)
 for p in g['planes']:
  if thermal and not p['heat']:continue
  q=p['plane'];out|=(n@q[:3]>.99995)&(np.abs(pts@q[:3]-q[3])<.35)
 return out&inside
rows=[]
for pi,p in enumerate(parts):
 for li,l in enumerate(p['lods']):
  v=np.array(l['vertices']);fast=[];heat=[]
  for f in l['faces']:
   if f['hidden']:continue
   xyz=v[f['vertices']];n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);n/=max(np.linalg.norm(n),1e-8)
   if n@np.array(f['normal'])<0:n=-n
   pts=np.array([xyz[0]*(1-u-w)+xyz[1]*u+xyz[2]*w for u in np.linspace(0,1,21) for w in np.linspace(0,1-u,21)])
   for gi,g in enumerate(groups):
    a=mask(pts,n,g);b=mask(pts,n,g,True)
    if a.any():
     assert pi==g['part'],('outside nozzle part',pi,li,f['id'],gi)
     fast.append([f['id'],gi])
    if b.any():heat.append([f['id'],gi])
  rows.append(dict(part=pi,lod=li,fast_faces=fast,heat_faces=heat))
for g in groups:
 row=next(x for x in rows if x['part']==g['part'] and x['lod']==0)
 assert len(row['heat_faces'])==(28 if g['part']==2 else 10),row
(W/'nozzle_surface_audit.json').write_text(json.dumps(dict(passed=True,method='Native plane normals and plane distances, with nozzle bounds; sampled all native triangles across all LODs',other_parts_selected=0,rows=rows),indent=2)+'\n')

def vec(a):return 'vec'+str(len(a))+'('+','.join(f'{x:.7f}' for x in a)+')'
base=(K/'kurgen_systems.glsl').read_text();compose=base[base.index('vec3 ku18_compose'):base.index('vec3 ku18_engine_spill')].replace('ku18_','pr18_')
spill=base[base.index('vec3 ku18_engine_spill'):base.index('float ku18_nozzle')].replace('ku18_','pr18_').replace('Surface pixel, float drive','Surface pixel, float drive, vec3 lightPosition, float reach').replace('vec3(-28.5745697, 62.7972527, -2572.3293457)','lightPosition').replace('2000.0','reach').replace('vec3(1.0, 0.0, 0.0)','vec3(1.0, 0.075, 0.012)').replace('* drive;','* drive * 1.8;')
shader='''// SPDX-License-Identifier: MPL-2.0
// Material/light composition adapted from OpenReliant 0.18.0 device.glsl.
// See LICENSE-OpenReliant.txt. Local surface spill; does not cast onto other objects.
// Native mesh parts use separate shader frames. Exact plane/normal masks prevent
// engine coordinates selecting similar locations on the hull or support arms.
'''+compose+spill
for i,g in enumerate(groups):
 shader+=f'const vec4 planes{i}[{len(g["planes"])}] = vec4[]('+','.join(vec(p['plane']) for p in g['planes'])+');\n'
 shader+=f'const float hot{i}[{len(g["planes"])}] = float[]('+','.join('1.0' if p['heat'] else '0.0' for p in g['planes'])+');\n'
 shader+=f'''vec2 nozzle{i}(vec3 at, vec3 normal) {{
 if (any(lessThan(at,{vec(g['lo'])})) || any(greaterThan(at,{vec(g['hi'])}))) return vec2(0.0);
 vec2 weight=vec2(0.0);
 for (int j=0;j<{len(g['planes'])};j++) {{
  vec4 plane=planes{i}[j];
  if (dot(normal,plane.xyz) > 0.99995 && abs(dot(at,plane.xyz)-plane.w) < 0.35) weight=max(weight,vec2(1.0,hot{i}[j]));
 }}
 return weight;
}}
'''
shader+='''void surface(inout Surface s, vec4 parameters, float time) {
 s.glow *= clamp(parameters.x,0.0,1.0);
 vec3 geometric=cross(dFdx(s.local),dFdy(s.local));
 geometric/=max(length(geometric),0.000001);
 if (dot(geometric,objectDirection(facing))<0.0) geometric=-geometric;
 float drive=clamp(parameters.y,0.0,1.0),heat=clamp(parameters.z,0.0,1.0);
 float thermal=0.0;
'''
for i,g in enumerate(groups):
 shader+=f' vec2 n{i}=nozzle{i}(s.local,geometric);\n if(n{i}.x>0.0) s.glow += pr18_engine_spill(s,drive,{vec(g["center"])},{680.0 if i<2 else 580.0});\n thermal=max(thermal,n{i}.y);\n'
shader+=''' float detail=0.45+0.55*clamp(dot(s.color,vec3(0.2126,0.7152,0.0722))*2.0,0.0,1.0);
 s.glow+=thermal*detail*(0.16*drive+0.46*heat)*mix(vec3(0.65,0.035,0.005),vec3(1.0,0.20,0.025),heat);
 s.glow*=clamp(parameters.w,0.0,1.0);
}
'''
(O/'prowler_systems.glsl').write_text(shader)
for name in ['lighting','response','surface','inspection']:
 s=(K/f'kurgen_{name}.luau').read_text().replace('kurgen','prowler').replace('Kurgen','Prowler').replace('KURGEN','PROWLER').replace('kurgan','prowler')
 if name=='lighting':s=s.replace('    return {a.left / full, a.right / full, a.fore / full, a.aft / full}','    -- The Prowler also has a separately counted hull component. Its real damage\n    -- must dim cabins even when the four armour fields have not changed.\n    local hull = 1\n    for _, part in ship:parts() do\n        if part.class == "hull" and part.component ~= nil and part.full_armor and part.full_armor > 0 then\n            hull = math.min(hull, (part.armor or 0) / part.full_armor)\n        end\n    end\n    return {math.min(hull,a.left/full), math.min(hull,a.right/full),\n        math.min(hull,a.fore/full), math.min(hull,a.aft/full)}')
 if name=='surface':s=s.replace('mission.number == 962','mission.number == 961').replace('bloom = 0.65','bloom = 0.40')
 if name=='inspection':s=s.replace('mission 962','mission 961')
 (O/f'prowler_{name}.luau').write_text(s)
shutil.copy2(K/'LICENSE-OpenReliant.txt',O/'LICENSE-OpenReliant.txt')
# Disable only the intact hull's old steady red wash. Preserve wreck lamp and plumes.
old=(D/'exports/openreliant_0_18_v1/mods/117-prowler-worn-v1/US_Prowler.SHP').read_bytes();new=bytearray(old);pos=0;part=-1;change=[]
while pos<len(old):
 tag,size,count=struct.unpack_from('<3H',old,pos);start=pos+6
 if tag==2:part+=1
 if tag==9 and part==2:
  for i in range(count):
   a=start+i*size
   if struct.unpack_from('<I',old,a)[0]==4:
    assert struct.unpack_from('<2f',old,a+116)==(400.,8.);assert struct.unpack_from('<3i',old,a+84)==(0,0,0)
    struct.pack_into('<f',new,a+120,0.);change.append(dict(part=part,attachment=i,offset=a+120,before=8,after=0,position=list(struct.unpack_from('<3f',old,a+4))))
 pos=start+size*count
assert len(change)==1 and all(a==b or change[0]['offset']<=i<change[0]['offset']+4 for i,(a,b) in enumerate(zip(old,new)))
(O/'US_Prowler.SHP').write_bytes(new)
(W/'native_preservation.json').write_text(json.dumps(dict(passed=True,changes=change,previous_sha256=sha(old),revised_sha256=sha(new),all_other_bytes_identical=True,original_exhaust_attachments_turrets_damage_lamp_preserved=True),indent=2)+'\n')
(O/'mod.ini').write_text('''[Mod]
Name=Prowler - Worn Paint (Review)
Version=0.1.0-beta.1
Description=Prowler revision 1.1: muted green glazing, worn outlined AL-47 stencil, and nozzle-centred throttle and heat lighting. Awaiting review.
OpenReliant=0.18.0
License=CC-BY-NC-SA-4.0

[Scripts]
Global=prowler_lighting.luau
Player=prowler_surface.luau

[Missions]
mission961.dte=prowler_inspection.luau
''')
for p in O.iterdir():
 if p.suffix in ['.glsl','.luau']:shutil.copy2(p,W/p.name)
print('PROWLER_NOZZLES_AUDITED',[(g['part'],len(g['planes'])) for g in groups],len(rows),'part/LODs')
