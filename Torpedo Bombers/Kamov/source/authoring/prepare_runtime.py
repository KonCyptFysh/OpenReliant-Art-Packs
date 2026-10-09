import os
from pathlib import Path
import shutil,json,hashlib
D=Path(str(Path(os.environ['KAMOV_WORKSPACE'])));G=Path(str(Path(os.environ['OPENRELIANT_HOME'])));R=D/'work/runtime_validation';T=R/'game-data';T.mkdir(parents=True,exist_ok=True)
# Retail archives/static tables are read-only links. Settings, logs, caches and pilots are isolated.
for p in (G/'game-data').iterdir():
 if p.is_file() and p.suffix.lower() in ['.hog','.ccb','.dat','.bik','.dll','.exe','.icd','.asi','.m3d'] or p.name in ['gunstats.bin','missilestats.bin','pilotstats.bin','shipstats.bin','DEFAULT.TXT'] or p.name in ['interface','inter','music','ms_speech','Forces']:
  if not (T/p.name).exists():(T/p.name).symlink_to(p,target_is_directory=p.is_dir())
(T/'starlancer.ini').write_text('[OpenReliant]\n[Device]\n')
(T/'mods').mkdir(exist_ok=True)
for source in [D/'exports/openreliant_v1/mods/104-kamov-worn-v1',G/'game-data/mods/97-ordnance-worn-v1']:
 target=T/'mods'/source.name
 if not target.exists():target.symlink_to(source,target_is_directory=True)
(R/'README.md').write_text('Isolated bounded animation validation. Retail archives and two mod folders linked read-only; settings, logs and cache live here. Uses official OpenReliant 0.7.0. No global install settings are altered.\n')
print(T)
