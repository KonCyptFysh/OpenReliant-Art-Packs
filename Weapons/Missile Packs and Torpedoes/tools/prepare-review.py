#!/usr/bin/env python3
"""Create an isolated local review environment using the installed, deployed art.
Usage: python prepare-review.py /path/to/OpenReliant
Game archives are linked for reading. Settings are copied once; saves and caches stay local.
"""
from pathlib import Path
import shutil,sys
asset=Path(__file__).resolve().parents[1]
install=Path(sys.argv[1]).expanduser().resolve() if len(sys.argv)>1 else Path.home()/'Games/OpenReliant'
data=install/'game-data';review=install/'reviews/ordnance-v1';rd=review/'game-data';mods=rd/'mods';mods.mkdir(parents=True,exist_ok=True)
assert (data/'resource.hog').is_file(),'Choose the installed OpenReliant folder'
for p in data.iterdir():
 if p.is_file() and p.suffix.lower() in ['.hog','.dat','.ccb','.bin','.dll','.bik','.txt']:
  q=rd/p.name
  if not q.exists():q.symlink_to(p)
for name in ['music','ms_speech','inter','interface','Forces']:
 p=data/name;q=rd/name
 if p.is_dir() and not q.exists():q.symlink_to(p,target_is_directory=True)
for p in data.glob('*.ini'):
 q=rd/p.name
 if not q.exists():shutil.copy2(p,q)
# Load only the deployed ordnance art and test-only ship definitions.
main=data/'mods/97-ordnance-worn-v1';assert main.is_dir(),'Deploy the artwork mod first'
link=mods/main.name
if not link.exists():link.symlink_to(main,target_is_directory=True)
assert link.resolve()==main.resolve(),'Unexpected ordnance review link'
helper=mods/'ordnance-inspection';helper.mkdir(exist_ok=True)
for p in (asset/'testing/ordnance-inspection').iterdir():shutil.copy2(p,helper/p.name)
shutil.copy2(asset/'tools/launch-ordnance-test.sh',install/'launch-ordnance-test.sh');(install/'launch-ordnance-test.sh').chmod(0o755)
print('Review ready:',install/'launch-ordnance-test.sh')
