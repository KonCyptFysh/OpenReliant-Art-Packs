#!/usr/bin/env python3
"""Validate the art-pack catalogue and copy it into the static website."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build(root=ROOT):
    data=json.loads((root/'catalog.json').read_text());categories={c['id'] for c in data['categories']};ids=set()
    for asset in data['assets']:
        assert asset['id'] not in ids,asset['id'];ids.add(asset['id']);assert asset['category'] in categories
        assert asset['status'] in {'coming-soon','available'}
        if asset['status']=='available':
            assert asset.get('download','').startswith('https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/download/')
            assert asset.get('release') and asset.get('checksum') and asset.get('downloadBytes',0)>0
            assert '/releases/download/'+asset['tag']+'/' in asset['download'],'Download must use its final published tag'
            assert (root/asset['folder']/'asset-manifest.json').is_file()
        else:assert not asset.get('download'),'Unreleased assets must not expose a download link'
        media=[asset[name] for name in ('preview','model') if asset.get(name)]
        if asset.get('images'):
            assert isinstance(asset['images'],list)
            assert asset['preview']==asset['images'][0]['src'],'Cover must be the first gallery photo'
            for photo in asset['images']:
                assert isinstance(photo.get('caption'),str) and photo['caption'].strip()
                media.append(photo['src'])
            assert len({photo['src'] for photo in asset['images']})==len(asset['images']),'Duplicate gallery photo'
        for source in media:
            rel=Path(source);assert not rel.is_absolute() and '..' not in rel.parts
            p=root/'docs'/rel;assert p.is_file(),p
            assert not p.read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1'),p
    (root/'docs/catalog.json').write_text(json.dumps(data,indent=2)+'\n')
    print(f'Catalogue validated: {len(categories)} categories, {len(ids)} assets, {sum(a["status"]=="available" for a in data["assets"])} available.')

if __name__=='__main__':build()
