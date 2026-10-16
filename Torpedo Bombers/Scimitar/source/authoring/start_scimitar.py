from pathlib import Path
import shutil,json,hashlib,datetime,subprocess,os
T=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures');D=T/'Scimitar/worn';W=D/'work/reconstruction_v1'
assert not D.exists(),'Inspect any existing Scimitar workspace first'
for p in ['source','maps','work/reconstruction_v1','review/reconstruction_v1','exports/openreliant_0_8_v1/mods/115-scimitar-worn-v1']:(D/p).mkdir(parents=True)
G=Path('${OPENRELIANT_HOME}');tool=G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'
F=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/extracted/RESOURCE.HOG/files')
shutil.copy2(F/'Scimitar.SHP',D/'source/Scimitar.SHP')
subprocess.run([str(tool),'tcache','extract',str(G/'game-data/tcachehw.dat'),str(F/'palette.tga'),str(D/'source'),'SCIMITAR'],check=True)
for name in ['parse_native.py','build_source.py','source_uv_audit.py']:
 s=(T/'Hades/worn/work/reconstruction_v1'/name).read_text().replace('HADES','SCIMITAR').replace('Hades','Scimitar').replace('hades','scimitar').replace('USTB_Hds.SHP','Scimitar.SHP').replace('torp_2.png','SCIMITAR.png')
 s=s.replace('len(parts)==6','len(parts)==1').replace('len(meshes)==6','len(meshes)==1').replace('==368','==476')
 (W/name).write_text(s)
subprocess.run(['python3',str(W/'parse_native.py')],check=True)
subprocess.run(['python3',str(W/'source_uv_audit.py')],check=True,stdout=subprocess.DEVNULL)
for command in ['info','check','chunks','components']:
 p=subprocess.run([str(tool),'shp',command,str(D/'source/Scimitar.SHP')],capture_output=True,text=True,check=True);(W/('native-'+command+'.txt')).write_text(p.stdout+p.stderr)
parts=json.loads((D/'source/native_parts.json').read_text())
summary=[dict(name=p['name'],parent=p['parent'],origin=p['origin'],stored_lod0=len(p['lods'][0]['faces']),visible_lod0=sum(not f['hidden'] for f in p['lods'][0]['faces']),tracks=p['tracks'],attachments=p['attachments']) for p in parts]
(W/'native_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=dict(ship='Scimitar',catalogue_id='scimitar',native_file='Scimitar.SHP',ship_type=48,active_variant='worn',status='first_pass_in_progress',user_approved=False,published=False,originals=[dict(path='source/'+p.name,sha256=sha(p)) for p in (D/'source').iterdir() if p.suffix in ('.SHP','.png')],pbr_release_gate=dict(status='satisfied',engine='Official OpenReliant 0.18.0 installed; existing pack baseline 0.8.1'),progress=dict(texture_uv='original_mesh_and_atlas_audit',pbr_authoring='pending_atlas_restoration',pbr_tuning='pending',engine_validation='pending'),loadout_texture_variants='engine_generated_no_g_or_r_copies',updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n')
shutil.copy2(__file__,W/'start_scimitar.py')
print(json.dumps(summary,indent=2))
