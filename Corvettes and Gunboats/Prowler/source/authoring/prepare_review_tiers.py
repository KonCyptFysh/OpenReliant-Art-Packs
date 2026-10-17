from pathlib import Path
import sys,json,shutil,subprocess,hashlib
R=Path('${ART_PACK_REPOSITORY}');sys.path.insert(0,str(R/'tools'));import resolution_pack as rp
D=Path('${PROWLER_WORKSPACE}');W=D/'work/reconstruction_v1';O=D/'exports/openreliant_0_18_v1/mods/117-prowler-worn-v1';records=[]
for tier,limit in [('4k',4096),('2k',2048),('1k',1024)]:
 dest=O if tier=='4k' else D/'exports'/('review_'+tier)/'mods'/O.name
 dest.mkdir(parents=True,exist_ok=True)
 if tier!='4k':
  for p in O.iterdir():
   if rp.is_texture(p):rp.resize_texture(p,dest/p.name,limit)
   else:shutil.copy2(p,dest/p.name)
  p=dest/'mod.ini';p.write_text(p.read_text().replace('(Review)',f'({tier.upper()} Review)'))
 assert rp.audit_maps(dest,limit)==7
 checks=[]
 for stem in ['orpr1_hull1','orpr1_hull2']:
  em=(dest/(stem+'_emissive.png')).exists();probe=Path('/tmp/kurgen-emissive-probe') if em else R/'.local/texture-variant-cleanup/texture-probe'
  q=subprocess.run([str(probe),str(dest),stem],capture_output=True,text=True,timeout=240);log=W/f'loader-{tier}-{stem}.log';log.write_text(q.stdout+q.stderr);assert q.returncode==0,(tier,stem,q.stdout,q.stderr)
  checks.append(dict(material=stem,emissive=em,probe_sha256=rp.package_mod.digest(probe),log_sha256=rp.package_mod.digest(log)))
 records.append(dict(tier=tier,status='passed',runtime=str(dest),files=[dict(name=p.name,sha256=rp.package_mod.digest(p),bytes=p.stat().st_size) for p in sorted(dest.iterdir()) if p.is_file()],loader_checks=checks))
 print('PROWLER_TIER_PASSED',tier,flush=True)
(W/'resolution_checks.json').write_text(json.dumps(dict(status='passed',recipe=rp.RECIPE,tiers=records,scope='Local review exports; not published packages. Official loader probes for base/normal/ORM/loadout recolours and emissives; not an in-game visual test.'),indent=2)+'\n')
