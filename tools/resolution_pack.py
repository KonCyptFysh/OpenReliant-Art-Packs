#!/usr/bin/env python3
"""Build reproducible resolution variants from a validated, immutable released master.

Requires Python 3, Pillow, NumPy and ImageMagick (for 16-bit PNG maps). Runtime textures are capped by longest edge;
mod.png is a launcher illustration, not a material. No source art is modified.
"""
import argparse, configparser, hashlib, json, shutil, sys, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
import package_mod

RECIPE = 'texture-resolution-v2'
TIERS = {'1k':1024, '2k':2048, '4k':4096}
ROLES = ('normal', 'orm', 'emissive', 'occlusion', 'roughness', 'metallic')

def read(p): return json.loads(p.read_text())
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def role_of(path):
    for role in ROLES:
        if path.stem.endswith('_'+role): return role
    return 'colour'

def is_texture(p): return p.suffix.lower()=='.png' and p.name.lower()!='mod.png'

def dimensions(size, limit):
    w,h=size
    while max(w,h)>limit: w,h=max(1,w//2),max(1,h//2)
    return w,h

def mean_blocks(a, factor):
    h,w=a.shape[:2]
    if h%factor or w%factor: raise ValueError('Expected power-of-two material dimensions')
    return a.reshape(h//factor,factor,w//factor,factor,-1).mean(axis=(1,3))

def decode_srgb(x): return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def encode_srgb(x): return np.where(x<=.0031308,x*12.92,1.055*np.maximum(x,0)**(1/2.4)-.055)

def resize_texture(source, destination, limit):
    with Image.open(source) as im:
        size=im.size; target=dimensions(size,limit)
        if target==size:
            shutil.copy2(source,destination)
            return dict(role=role_of(source),source_size=list(size),size=list(size),resized=False)
        # Pillow decodes 16-bit RGB PNG to 8 bits; use ImageMagick for those masters.
        if im.mode not in ('RGB','RGBA'): raise ValueError(f'Unsupported master mode {source}: {im.mode}')
        with source.open('rb') as f: header=f.read(29)
        bits=header[24]
        if bits not in (8,16): raise ValueError(f'Unsupported PNG bit depth: {source}')
        if size[0]%target[0] or size[1]%target[1] or size[0]//target[0]!=size[1]//target[1]:
            raise ValueError('Non-uniform material scale: '+str(source))
        if bits==16:
            channels=4 if header[25]==6 else 3
            raw=subprocess.check_output(['magick',str(source),'-depth','16','-endian','MSB',('RGBA' if channels==4 else 'RGB')+':-'])
            a=np.frombuffer(raw,dtype='>u2').reshape(size[1],size[0],channels).astype(np.float32)/65535
            del raw
        else: a=np.asarray(im,dtype=np.float32)/255
        factor=size[0]//target[0]; role=role_of(source)
        if role=='normal':
            n=a[:,:,:3]*2-1
            n/=np.maximum(np.linalg.norm(n,axis=2,keepdims=True),1e-10)
            n=mean_blocks(n,factor)
            length=np.linalg.norm(n,axis=2,keepdims=True)
            n=np.where(length>1e-8,n/np.maximum(length,1e-8),np.array([0,0,1],dtype=np.float32))
            out=(n+1)/2 # OpenReliant ignores source normal alpha.
        elif role in ('colour','emissive'):
            rgb=decode_srgb(a[:,:,:3])
            if a.shape[2]==4:
                alpha=mean_blocks(a[:,:,3:4],factor)
                colour=mean_blocks(rgb*a[:,:,3:4],factor)/np.maximum(alpha,1e-10)
                colour=np.where(alpha>0,colour,mean_blocks(rgb,factor))
                out=np.concatenate([encode_srgb(colour),alpha],axis=2)
            else: out=encode_srgb(mean_blocks(rgb,factor))
        else: out=mean_blocks(a,factor)
        if bits==16:
            raw=np.rint(np.clip(out,0,1)*65535).astype('>u2').tobytes()
            subprocess.run(['magick','-size',f'{target[0]}x{target[1]}','-depth','16','-endian','MSB',
                ('RGBA' if out.shape[2]==4 else 'RGB')+':-','-define','png:bit-depth=16','-define','png:exclude-chunks=date,time',str(destination)],input=raw,check=True)
        else: Image.fromarray(np.rint(np.clip(out,0,1)*255).astype('uint8')).save(destination,compress_level=6)
        return dict(role=role,source_size=list(size),size=list(target),resized=True)

def audit_maps(folder, limit):
    files={p.name:p for p in folder.iterdir() if is_texture(p)}
    for name,p in files.items():
        with Image.open(p) as im:
            im.load(); size=im.size
        if max(size)>limit: raise ValueError('Texture exceeds tier: '+name)
        role=role_of(p)
        if role!='colour':
            base=files.get(p.stem[:-(len(role)+1)]+'.png')
            if base is None: raise ValueError('Orphan map: '+name)
            with Image.open(base) as im:
                if im.size!=size: raise ValueError('Material map dimensions differ: '+name)
    return len(files)

def build_variant(root, tier, source_commit):
    root=root.resolve(); limit=TIERS[tier]
    config,assets=package_mod.validate(root)
    if root.parent.name=='HUD': raise ValueError('HUD is excluded')
    generated=root/'dist'/'resolutions'/tier
    generated.mkdir(parents=True,exist_ok=True)
    version=config['version']+'.res2'
    records=[]; images=[]; copied=[]
    for source in assets:
        rel=source.relative_to(root); dest=generated/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        info=None
        if is_texture(source): info=resize_texture(source,dest,limit)
        elif source.name=='mod.ini':
            # Preserve formatting, every script hook and all dependency declarations.
            text=source.read_text(encoding='utf-8-sig')
            import re
            text,n=re.subn(r'(?m)^Version=.*$', 'Version='+version,text,count=1)
            if n!=1: raise ValueError('Expected one mod version')
            text=re.sub(r'(?m)^Name=(.*)$',lambda m:'Name='+m[1]+' ('+tier.upper()+')',text,count=1)
            dest.write_text(text)
        else:
            shutil.copy2(source,dest);copied.append(rel.as_posix())
        record=dict(path=rel.as_posix(),bytes=dest.stat().st_size,sha256=package_mod.digest(dest))
        records.append(record)
        if info: images.append(dict(path=rel.as_posix(),source_sha256=package_mod.digest(source),sha256=record['sha256'],**info))
    for folder in config['mod_folders']: audit_maps(generated/'mods'/folder,limit)
    write(generated/'asset-manifest.json',records)
    manifest_hash=package_mod.digest(generated/'asset-manifest.json')
    proof=dict(recipe=RECIPE,tier=tier,max_texture_edge=limit,source_commit=source_commit,
        source_version=config['version'],asset_revision=config['asset_revision'],
        source_manifest_sha256=package_mod.digest(root/'asset-manifest.json'),
        asset_manifest_sha256=manifest_hash,images=images,unchanged_files=copied,
        resampling=dict(colour='sRGB decoded to linear light; alpha-weighted box average; sRGB encoded',
            emissive='Same linear-light averaging as colour; no automatic brightness boost',
            normal='Average unit vectors then renormalize; flat fallback for cancelling vectors',
            orm='Linear channel averages; no colour conversion'),
        limitations=['Normal variance below the target pixel size is not retained in PNG normal alpha, which the engine ignores.',
            'Master gallery images are shared by all tiers; small details become softer at lower resolution.'])
    write(generated/'resolution-provenance.json',proof)
    original=read(root/'validation.json')
    write(generated/'validation.json',dict(status='passed',asset_manifest_sha256=manifest_hash,
        engine_build=original['engine_build'],tested_platforms=original['tested_platforms'],
        checks=['Released master manifest verified','All PNG files decoded; dimensions and companion maps checked',
                'Non-image runtime files preserved except mod name/version; no geometry, UV, animation or lighting-script changes'],
        scope='Automated packaging checks. Master engine evidence is inherited for unchanged files; representative tier rendering is recorded separately in the repository.',
        source_validation_sha256=package_mod.digest(root/'validation.json')))
    docs=[]
    for name in ('CREDITS.md','LICENSING.md','KNOWN_ISSUES.md'):
        if (root/name).is_file(): shutil.copy2(root/name,generated/name);docs.append(name)
    for name in ('README.md','validation.json'):
        shutil.copy2(root/name,generated/('MASTER-'+name))
        docs.append('MASTER-'+name)
    (generated/'README.md').write_text(f'''# {root.name} — {tier.upper()} textures\n\nComplete drop-in mod, derived from approved artwork revision {config['asset_revision']} / master package {config['version']}. Requires OpenReliant {config['minimum_openreliant']} or newer.\n\nTextures are at most {limit} pixels on their longest edge. Smaller textures and the launcher illustration retain their original size. Models, UVs, animations and scripted emissive behaviour are unchanged.\n\n## Installation\n\nChoose ONE resolution for this asset. Replace its existing mod folder with the folder inside this ZIP's `mods/` directory; do not merge folders or install tiers side by side. All tiers share the same native folder and dependencies. Different assets may use different resolutions. Keep your pilot saves.\n\nThe included MASTER documents describe the reviewed source pack; their hashes and dimensions are historical master evidence. This variant's exact files are listed in asset-manifest.json and resolution-provenance.json. Automated resizing does not add missing emissives.\n\n## Emissives\n\nAuthor base colour, normal, ORM and emissive maps once at master resolution with matching dimensions and UV placement. Generate each tier together. Scripted flicker, heat and throttle timing use the same code at every tier. Emissive images are averaged in linear light to retain average intensity; very fine lights can become softer or blend together at 1K. Review those details when adding new lighting.\n''')
    new=dict(config,version=version,package_name=config['package_name']+'-'+tier,
        asset_manifest_sha256=manifest_hash,source_master_version=config['version'],resolution=tier,
        include_documents=['README.md','asset-manifest.json','validation.json','resolution-provenance.json','release.json']+docs)
    write(generated/'release.json',new)
    archive=package_mod.build(generated)
    return dict(tier=tier,version=version,zip=str(archive),sha256=package_mod.digest(archive),bytes=archive.stat().st_size,
                manifest=manifest_hash,provenance=proof)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--tier',choices=TIERS,required=True);p.add_argument('--source-commit',required=True)
    args=p.parse_args();result=build_variant(args.root,args.tier,args.source_commit)
    print(json.dumps({k:v for k,v in result.items() if k!='provenance'},indent=2))
