#!/usr/bin/env python3
"""Repackage already-verified materials without recompressing or changing them."""
from pathlib import Path
import hashlib, shutil, subprocess, zipfile
import package_mod

def repack(source, root):
    config, assets = package_mod.validate(root)
    destination = root/'dist'/(config['package_name']+'-'+config['version']+'.zip')
    destination.parent.mkdir(parents=True,exist_ok=True)
    expected={p.relative_to(root).as_posix():p for p in assets}
    changed={}; removed=[]
    with zipfile.ZipFile(source) as old:
        if len(old.namelist())!=len(set(old.namelist())):raise ValueError('Duplicate source ZIP entry')
        for entry in old.infolist():
            p=expected.get(entry.filename)
            if p is None:removed.append(entry.filename)
            elif hashlib.sha256(old.read(entry)).hexdigest()!=package_mod.digest(p):
                removed.append(entry.filename);changed[entry.filename]=p
        for name,p in expected.items():
            if name not in old.namelist():changed[name]=p
    temporary=destination.with_suffix('.partial.zip')
    shutil.copy2(source,temporary)
    if removed:
        subprocess.run(['zip','-q','-d',str(temporary),*removed],check=True)
    with zipfile.ZipFile(temporary,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
        for name,p in sorted(changed.items()):
            info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            out.writestr(info,p.read_bytes())
    with zipfile.ZipFile(temporary) as out:
        if set(out.namelist())!=set(expected):raise ValueError('Unexpected packaged file')
        for name,p in expected.items():
            if hashlib.sha256(out.read(name)).hexdigest()!=package_mod.digest(p):raise ValueError('Packaged file mismatch: '+name)
    temporary.replace(destination)
    destination.with_suffix('.zip.sha256').write_text(package_mod.digest(destination)+'  '+destination.name+'\n')
    return destination
