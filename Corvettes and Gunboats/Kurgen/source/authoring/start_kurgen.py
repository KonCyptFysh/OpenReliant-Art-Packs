from pathlib import Path
import shutil,subprocess,json,hashlib,datetime
T=Path('${ART_SOURCE_ROOT}/assets/working/textures');D=T/'Kurgen/worn';W=D/'work/reconstruction_v1';old=T/'Scimitar/worn/work/reconstruction_v1';G=Path('${OPENRELIANT_HOME}');F=Path('${ART_SOURCE_ROOT}/assets/extracted/RESOURCE.HOG/files');tool=G/'releases/openreliant-v0.18.0-linux-x86_64/sltool'
assert not D.exists()
for p in ['source','maps','work/reconstruction_v1','review/reconstruction_v1','exports/openreliant_0_8_v1/mods/116-kurgen-worn-v1']:(D/p).mkdir(parents=True)
for name in ['Rus_Kurgan.SHP','Rus_Kurgan_dest.SHP']:shutil.copy2(F/name,D/'source'/name)
for tex in ['KURGEN','DAM_1']:subprocess.run([str(tool),'tcache','extract',str(G/'game-data/tcachehw.dat'),str(F/'palette.tga'),str(D/'source'),tex],check=True)
for name in ['parse_native.py','source_uv_audit.py','build_source.py']:
 s=(old/name).read_text().replace('SCIMITAR','KURGEN').replace('Scimitar','Kurgen').replace('scimitar','kurgen').replace('Kurgen.SHP','Rus_Kurgan.SHP')
 s=s.replace('len(parts)==1','len(parts)==2').replace('len(meshes)==1','len(meshes)==2').replace('==476','==556')
 if name=='build_source.py':
  s=s.replace('o.scale*=.0025','o.scale*=.00065')
  s=s.replace('for mi in [0]:','for mi in [0,1]:').replace("str(D/'source/kurgen.png')","str(D/'source'/['kurgen.png','dam_1.png'][mi])")
  s=s.replace("for p,mi in zip(o.data.polygons,o['native_material_indices']):p.material_index=mi","for p,mi in zip(o.data.polygons,o['native_material_indices']):p.material_index=mi if o['native_part_index']==0 else 1\n if o['native_part_index']==1:o.hide_render=True;o.hide_set(True)")
  s=s.replace('material_index=1\ns=bpy.context.scene','material_index=2\ns=bpy.context.scene')
 (W/name).write_text(s)
subprocess.run(['python3',str(W/'parse_native.py')],check=True)
subprocess.run(['python3',str(W/'source_uv_audit.py')],check=True,stdout=subprocess.DEVNULL)
for command in ['info','check','chunks','components']:
 p=subprocess.run([str(tool),'shp',command,str(D/'source/Rus_Kurgan.SHP')],capture_output=True,text=True,check=True);(W/('native-'+command+'.txt')).write_text(p.stdout+p.stderr)
parts=json.loads((D/'source/native_parts.json').read_text());summary=[dict(name=p['name'],parent=p['parent'],origin=p['origin'],stored_lod0=len(p['lods'][0]['faces']),visible_lod0=sum(not f['hidden'] for f in p['lods'][0]['faces']),tracks=p['tracks'],attachments=len(p['attachments'])) for p in parts];(W/'native_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=dict(ship='Kurgen',catalogue_id='kurgen',native_file='Rus_Kurgan.SHP',ship_type=60,active_variant='worn',status='first_pass_in_progress',user_approved=False,published=False,originals=[dict(path='source/'+p.name,sha256=sha(p)) for p in (D/'source').iterdir() if p.suffix in ('.SHP','.png')],pbr_release_gate=dict(status='satisfied',engine='Official OpenReliant 0.18.0 installed; pack baseline 0.8.1'),progress=dict(texture_uv='original_mesh_and_atlas_audit',pbr_authoring='pending_atlas_restoration',pbr_tuning='pending',engine_validation='pending'),loadout_texture_variants='engine_generated_no_g_or_r_copies',updated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(D.parent/'project_state.json').write_text(json.dumps(state,indent=2)+'\n');shutil.copy2(__file__,W/'start_kurgen.py');print(json.dumps(summary,indent=2))
