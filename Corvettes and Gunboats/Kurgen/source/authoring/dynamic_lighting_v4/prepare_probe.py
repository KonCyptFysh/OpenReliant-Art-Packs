from pathlib import Path
import json,struct,shutil,hashlib
S=Path('/tmp/kurgen-poc-stage')
D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Kurgen/worn')
G=Path('/home/lva-8700/Games/OpenReliant/game-data')
P=Path('/tmp/kurgen-lighting-probe');P.mkdir(exist_ok=True)
O=P/'mods/116-kurgen-worn-v1';O.parent.mkdir(exist_ok=True)
if not O.exists():shutil.copytree(D/'exports/openreliant_0_8_v3/mods/116-kurgen-worn-v1',O)
for p in G.iterdir():
    if p.name in ['mods','starlancer.ini','cache','saves','screenshots','openreliant.log']:continue
    q=P/p.name
    if not q.exists():q.symlink_to(p,target_is_directory=p.is_dir())
if not (P/'starlancer.ini').exists():shutil.copy2(G/'starlancer.ini',P/'starlancer.ini')
for p in S.iterdir():
    if p.suffix in ('.luau','.glsl') and not p.name.startswith('test_'):shutil.copy2(p,O/p.name)
src=D/'exports/openreliant_0_8_v3/mods/116-kurgen-worn-v1/Rus_Kurgan.SHP'
before=src.read_bytes();data=bytearray(before);cursor=0;part=-1;changes=[]
while cursor<len(data):
    tag,size,count=struct.unpack_from('<3H',data,cursor);start=cursor+6
    if tag==2:part+=1
    if tag==9 and part==0:
        for i in range(count):
            at=start+i*size
            if i!=5:continue
            assert struct.unpack_from('<I',data,at)[0]==4
            assert struct.unpack_from('<3i',data,at+84)==(0,0,0)
            assert struct.unpack_from('<2f',data,at+116)==(2000.,1.)
            assert struct.unpack_from('<3f',data,at+4)[2]<-2500
            changes.append({'part':part,'attachment':i,'brightness_offset':at+120,
                'position':list(struct.unpack_from('<3f',data,at+4)), 'range':2000,
                'before':1,'after':0})
            struct.pack_into('<f',data,at+120,0.)
    cursor=start+size*count
assert len(changes)==1 and len(before)==len(data)
allow=set(range(changes[0]['brightness_offset'],changes[0]['brightness_offset']+4))
assert all(a==b or i in allow for i,(a,b) in enumerate(zip(before,data)))
(O/'Rus_Kurgan.SHP').write_bytes(data)
sha=lambda b:hashlib.sha256(b).hexdigest()
(S/'native_preservation.json').write_text(json.dumps({'passed':True,'changes':changes,'before_sha256':sha(before),'after_sha256':sha(data),
    'all_other_bytes_identical':True,'geometry_uv_materials_animations_collision_turrets_beacons_preserved':True},indent=2)+'\n')
(O/'mod.ini').write_text('''[Mod]
Name=Kurgen - Worn Paint (Lighting PoC)
Version=0.1.0-beta.1
Description=Kurgen revision 1.3: damage-responsive cabin lights, throttle-responsive stern glow, retained nozzle heat. Review build.
OpenReliant=0.18.0
License=CC-BY-NC-SA-4.0

[Scripts]
Global=kurgen_lighting.luau
Player=kurgen_surface.luau

[Missions]
mission962.dte=kurgen_inspection.luau
''')
print(O)
