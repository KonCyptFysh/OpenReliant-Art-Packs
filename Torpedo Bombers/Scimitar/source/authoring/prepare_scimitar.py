from pathlib import Path
import json,shutil,hashlib,math,subprocess
D=Path('${SCIMITAR_WORKSPACE}');W=D/'work/reconstruction_v1';old=D.parents[1]/'Hades/worn/work/reconstruction_v1'
I=Path('/home/lva-8700/.codex/generated_images/01a0efc3-3a2f-7fe3-b0c1-2dec3263b764')
shutil.copy2(I/'exec-edcab03e-6f07-4a36-a411-17afea62d8f7.png',D/'maps/scimitar_hull_reconstructed_initial.png')
shutil.copy2(I/'exec-e47f960e-7de8-4972-9cc9-963b556b04ec.png',D/'maps/scimitar_hull_reconstructed_v1.png')
prompts=[]
for src in ['/tmp/scimitar-prompt.json','/tmp/scimitar-final-prompt.json']:
 r=json.loads(Path(src).read_text())
 if src.endswith('scimitar-prompt.json'):r['output']='maps/scimitar_hull_reconstructed_initial.png'
 for k in ['input','output']:r[k+'_sha256']=hashlib.sha256((D/r[k]).read_bytes()).hexdigest()
 r['output_dimensions']=[1254,1254];prompts.append(r)
(W/'imagegen_prompts.json').write_text(json.dumps(prompts,indent=2)+'\n')
circle=lambda x,y,r,n=32:[[x+r*math.cos(i*2*math.pi/n),y+r*math.sin(i*2*math.pi/n)] for i in range(n)]
regions={
 'glass':[
 [[50,1104],[60,1093],[70,1093],[78,1103],[78,1226],[68,1236],[60,1236],[50,1226]],
 [[110,1103],[120,1092],[248,1092],[261,1104],[261,1137],[250,1148],[119,1148],[110,1138]],
 [[110,1191],[125,1181],[187,1181],[194,1189],[194,1233],[186,1237],[118,1237],[110,1231]],
 [[222,1187],[229,1181],[252,1181],[261,1188],[261,1226],[250,1236],[228,1236],[222,1230]],
 [[1162,943],[1168,938],[1178,938],[1187,944],[1208,1023],[1207,1032],[1200,1038],[1189,1038],[1162,1010]],
 circle(1133,1031,12)],
 'flat':[[31,75,102,115],[580,54,629,118],[737,121,807,159],[1081,51,1151,86],
 [633,158,705,218],[21,693,112,799],[235,534,276,565],[464,535,489,568],
 [363,984,877,1010],[366,1028,424,1057],[593,1028,652,1057],[815,1028,855,1057],
 [462,1098,612,1121],[457,1214,621,1234],[695,1117,774,1152],[695,1181,773,1224],
 [908,689,924,845],[1017,688,1039,844],[1074,690,1090,843],[1218,690,1238,843],
 [1019,1092,1235,1116],[1016,1215,1235,1238],[1015,1111,1035,1221],[1214,1111,1235,1221]],
 'vents':[[[53,410],[53,493],8],[[117,410],[117,493],8],[[743,65],[878,65],9],[[743,97],[878,97],9],
 [[172,284],[392,284],12],[[642,711],[853,711],12],[[61,886],[243,886],7],[[61,939],[243,939],7],
 [[982,908],[982,1025],8]],
 'radiators':[
 {'polygon':[[416,351],[520,332],[674,300],[782,250],[941,182],[941,365],[879,429],[436,429],[416,411]],'axis':'x','centres':list(range(438,941,21))},
 {'polygon':[[25,0],[181,0],[181,37],[25,37]],'axis':'x','centres':list(range(33,181,23))},
 {'polygon':[[379,453],[669,453],[669,485],[379,485]],'axis':'x','centres':list(range(384,669,19))},
 {'polygon':[[437,670],[594,670],[594,748],[437,748]],'axis':'x','centres':list(range(446,591,11))},
 {'polygon':circle(224,742,50),'axis':'y','centres':list(range(698,791,11))},
 {'polygon':[[922,698],[1017,698],[1017,836],[922,836]],'axis':'y','centres':list(range(706,837,25))},
 {'polygon':[[1089,698],[1217,698],[1217,836],[1089,836]],'axis':'y','centres':list(range(707,837,25))}],
 'circles':[[1144,254,13],[1145,304,13],[933,1168,23]],
 'panels':[
 [[303,0],[303,48]],[[172,0],[172,39]],[[51,222],[51,262]],[[0,379],[151,379]],[[157,350],[157,455]],
 [[213,382],[213,478],[228,493],[305,493],[319,481],[319,381]],[[319,354],[319,379],[371,379]],
 [[46,130],[46,211]],[[88,126],[88,210]],[[415,111],[552,111]],[[553,54],[553,306]],[[431,160],[550,160]],
 [[438,212],[638,212]],[[524,215],[524,297]],[[694,0],[694,156]],[[714,215],[714,271]],
 [[987,0],[987,159]],[[1008,195],[1008,367]],[[1057,192],[1057,272],[1103,272]],[[1176,193],[1176,219]],
 [[1176,345],[1176,430]],[[957,363],[1008,363]],[[886,438],[886,456]],[[777,483],[777,673]],
 [[884,483],[884,679]],[[883,512],[1057,512],[1057,639],[885,639]],[[1057,479],[1057,512]],
 [[1057,557],[1171,557]],[[1056,638],[1170,638]],[[124,527],[124,582]],[[235,531],[235,582]],
 [[491,531],[491,581]],[[576,588],[576,660]],[[236,588],[236,660]],[[166,588],[166,660]],
 [[17,686],[115,686],[121,692],[121,799],[115,806],[16,806],[10,798],[10,695],[17,686]],
 [[68,809],[68,847]],[[200,851],[200,872]],[[275,849],[275,975]],[[317,775],[317,943]],
 [[370,752],[370,969]],[[435,752],[435,804]],[[437,809],[437,914]],[[538,808],[538,869],[713,869]],
 [[719,808],[719,965]],[[804,877],[804,963]],[[884,865],[884,1079]],[[935,884],[935,1041]],
 [[1037,883],[1037,1084]],[[1080,968],[1150,968]],[[1126,862],[1126,908]],
 [[320,1116],[320,1201],[332,1212],[461,1212],[461,1122]],[[648,1108],[648,1166],[689,1166],[689,1230]],
 [[690,1148],[690,1168],[830,1168]],[[751,1168],[751,1230]],[[1041,1117],[1041,1213]],
 [[1082,1144],[1082,1214]],[[1144,1117],[1144,1214]]]
}
(W/'regions.json').write_text(json.dumps(dict(coordinate_size=[1254,1254],regions=regions,policy='Authored structural heights; all six cockpit panes recessed; painted markings flat.'),indent=2)+'\n')
for name in ['build_materials.py','export_native.py','portable_source.py','build_inspection.py']:
 s=(old/name).read_text().replace('HADES','SCIMITAR').replace('Hades','Scimitar').replace('hades','scimitar').replace('USTB_Hds.SHP','Scimitar.SHP').replace('torp_2','scimitar').replace('orhd1','orsc1').replace('114-scimitar','115-scimitar').replace('881','476').replace("'parts':6","'parts':1").replace("'stored_triangles':368","'stored_triangles':476")
 if name=='export_native.py':
  s=s.replace('(965,966,967,968)','(963,964)').replace('mission966','mission964').replace("and '26' in ships","and '48' in ships").replace('recessed green glazing','recessed amber glazing')
 if name=='build_inspection.py':
  s=s.replace('range(4)','range(2)').replace('range(5)','range(3)').replace('26 if i==0 else 74','48 if i==0 else 92').replace('65535 if i==0 else 26','65535 if i==0 else 48').replace("'<HHHHBBHII',5+i","'<HHHHBBHII',3+i").replace('1 if i==0 else 4','1 if i==0 else 2').replace('0 if i<5 else 1','0 if i<3 else 1').replace('range(7)','range(5)')
  s=s.replace(" if mode=='deployed':init+=deploy\n",'').replace(" if mode=='cycle':init+=wait(7)+num(1)+num(1)+num(24)+num(0)+command(1)+bytes([0x22,1])\n",'')
  s=s.replace("init+=deploy+wait(8)+ship(1)+command(0x14)+wait(6)+ship(2)+command(0x14)+wait(6)+ship(3)+command(0x14)+wait(6)+ship(4)+command(0x14)+group(1)+command(0x3a)+stow","init+=wait(8)+ship(1)+command(0x14)+wait(6)+ship(2)+command(0x14)")
  s=s.replace('enumerate([init,cycle])','enumerate([init])').replace("3:(5,b''.join(ships))","3:(3,b''.join(ships))").replace('7:(7,objects)','7:(5,objects)').replace("8:(2,b''.join(parts))","8:(1,b''.join(parts))")
  s=s.replace("[('stowed',968),('deployed',967),('cycle',966),('launch',965)]","[('stowed',964),('launch',963)]").replace('carried_torpedoes=4','carried_torpedoes=2').replace('object.type == "torpedo"','object.type == "russian_torpedo"').replace('Only the four','Only the two')
  # The static Scimitar does not have a deploy animation; remove unused bytecode construction.
  s='\n'.join(line for line in s.split('\n') if not line.startswith((' track=',' deploy=',' cycle=')))
  s=s.replace('init=group(0)',"ret=num(1)+bytes([0x43])\n init=group(0)")
  s=s.replace('name(\'(F)CycleDeployParts\')',"name('(F)Unused')")
  s=s.replace('mode="${1:-cycle}"','mode="${1:-stowed}"').replace('stowed) mission=968','stowed) mission=964').replace('    deployed) mission=967 ;;\n','').replace('    cycle) mission=966 ;;\n','').replace('launch) mission=965','launch) mission=963').replace('[stowed|deployed|cycle|launch]','[stowed|launch]').replace('with four carried torpedoes','with two carried torpedoes')
  s='\n'.join(line for line in s.split('\n') if not line.startswith('if [[ "$mode" == cycle ]]') and not line.startswith('if [[ "$mode" == deployed ]]'))
  s=s.replace('deploy, release the first torpedo after about 9 seconds, then the remaining three at roughly 7-second intervals. The native arms then stow.','release the first torpedo after about 9 seconds and the second roughly 7 seconds later. The native launch mounts are fixed.')
  s=s.replace('openreliant-v0.8.1','openreliant-v0.18.0').replace('OpenReliant 0.8.1','OpenReliant 0.18.0').replace('--ship 26','--ship 48').replace('Built four native missions: stowed, deployed, continuous cycle and timed torpedo release.','Built two native missions: carried torpedoes and timed release.')
  s=s.replace("p.write_bytes(build(mode))", "p.write_bytes(build(mode))\n source=W/f'mission{number}.luau';source.write_text(subprocess.check_output([str(tool),'dte','decompile',str(p)],text=True))\n subprocess.run([str(tool),'dte','build',str(source),str(p)],check=True)")
 (W/name).write_text(s)
subprocess.run(['python3',str(W/'build_inspection.py')],check=True)
p=D/'exports/openreliant_0_8_v1/launch-scimitar-launch-test.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\nscript_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)\nexec "$script_dir/launch-scimitar-test.sh" launch "$@"\n');p.chmod(0o755)
shutil.copy2(__file__,W/'prepare_scimitar.py')
print('Scimitar material masks and two review modes prepared.')
