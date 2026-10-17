from pathlib import Path
import shutil,subprocess,json,hashlib,datetime
T=Path('${ART_SOURCE_ROOT}/assets/working/textures');D=T/'Prowler/worn';W=D/'work/reconstruction_v1';K=T/'Kurgen/worn/work/reconstruction_v1';G=Path('${OPENRELIANT_HOME}');F=Path('${ART_SOURCE_ROOT}/assets/extracted/RESOURCE.HOG/files');E=G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'
assert not D.exists()
for p in ['source','maps','work/reconstruction_v1','review/reconstruction_v1','exports/openreliant_0_18_v1/mods/117-prowler-worn-v1']:(D/p).mkdir(parents=True)
for name in ['US_Prowler.SHP','14_al_STUR.SHP']:shutil.copy2(F/name,D/'source'/name)
for tex in ['PROW_1','PROW_2','DAM_1','Missiles']:subprocess.run([str(E),'tcache','extract',str(G/'game-data/tcachehw.dat'),str(F/'palette.tga'),str(D/'source'),tex],check=True)
for name in ['parse_native.py','parse_turret.py','source_uv_audit.py']:
 s=(K/name).read_text().replace('Kurgen','Prowler').replace('Rus_Kurgan.SHP','US_Prowler.SHP').replace('10_Rus_STUR.SHP','14_al_STUR.SHP')
 if name=='parse_native.py':s=s.replace('len(parts)==2','len(parts)==6')
 (W/name).write_text(s);subprocess.run(['python3',str(W/name)],check=True,stdout=subprocess.DEVNULL)
for cmd in ['info','check','chunks','components']:
 p=subprocess.run([str(E),'shp',cmd,str(D/'source/US_Prowler.SHP')],capture_output=True,text=True,check=True);(W/('native-'+cmd+'.txt')).write_text(p.stdout+p.stderr)
s=(K/'build_source.py').read_text().replace('KURGEN','PROWLER').replace('Kurgen','Prowler').replace('kurgen','prowler').replace('Rus_Kurgan.SHP','US_Prowler.SHP')
s=s.replace('for mi in [0,1]:','for mi in [0,1,2]:').replace("['prowler.png','dam_1.png'][mi]","['prow_1.png','prow_2.png','dam_1.png'][mi]")
s=s.replace("mi if o['native_part_index']==0 else 1","mi if o['native_part_index']!=5 else 2").replace("if o['native_part_index']==1:","if o['native_part_index']==5:").replace('material_index=2\ns=bpy.context.scene','material_index=3\ns=bpy.context.scene')
s=s.replace('len(meshes)==2','len(meshes)==6').replace('==556','==661')
(W/'build_source.py').write_text(s)
parts=json.loads((D/'source/native_parts.json').read_text());summary=[dict(name=p['name'],origin=p['origin'],tracks=p['tracks'],lod0_faces=len(p['lods'][0]['faces'])) for p in parts];(W/'native_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=dict(ship='Prowler',catalogue_id='prowler',native_file='US_Prowler.SHP',ship_type=30,active_variant='worn',status='first_pass_in_progress',user_approved=False,published=False,originals=[dict(path=str(p.relative_to(D)),sha256=sha(p)) for p in (D/'source').iterdir() if p.suffix in ('.SHP','.png')],pbr_release_gate=dict(status='satisfied',engine='Official OpenReliant 0.18.0 installed'),progress=dict(texture_uv='native_audit_complete_reconstruction_in_progress',pbr_authoring='pending',pbr_tuning='pending',engine_validation='native_source_checks_passed'),loadout_texture_variants='canonical_unprefixed_PNG_only',updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n');shutil.copy2(__file__,W/'start_prowler.py');print(json.dumps(summary,indent=2))
