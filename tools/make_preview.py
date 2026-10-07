#!/usr/bin/env python3
"""Build a small viewing-only GLB from a native SHP and its runtime PBR maps.

Uses official sltool geometry export and Pillow for reduced preview textures.
Does not edit runtime assets or editable artwork. The output is not a game mod.
"""
import argparse,hashlib,io,json,struct,subprocess,tempfile
from pathlib import Path
from PIL import Image

def build(model,mod_folder,output,sltool,maximum=1024):
    with tempfile.TemporaryDirectory() as work:
        target=Path(work)/'preview.gltf'
        subprocess.run([str(sltool),'shp','gltf',str(model),str(target),'--lod','0'],check=True,capture_output=True)
        doc=json.loads(target.read_text());payload=bytearray((target.parent/doc['buffers'][0]['uri']).read_bytes())
        files={p.name.lower():p for p in mod_folder.iterdir() if p.is_file()}
        originals=list(doc['images']);doc['images']=[];doc['textures']=[];record=[]
        def texture(path,kind):
            with Image.open(path) as im:
                rgba=im.convert('RGBA');has_alpha=rgba.getextrema()[3][0]<255
                pic=rgba if kind=='base' and has_alpha else im.convert('RGB')
                pic.thumbnail((maximum,maximum),Image.Resampling.LANCZOS)
                data=io.BytesIO()
                if kind=='base' and not has_alpha:pic.save(data,format='JPEG',quality=90,subsampling=0);mime='image/jpeg'
                else:pic.save(data,format='PNG',optimize=True);mime='image/png'
                size=list(pic.size)
            while len(payload)%4:payload.append(0)
            view=len(doc['bufferViews']);blob=data.getvalue();doc['bufferViews'].append({'buffer':0,'byteOffset':len(payload),'byteLength':len(blob)});payload.extend(blob)
            image=len(doc['images']);doc['images'].append({'bufferView':view,'mimeType':mime})
            index=len(doc['textures']);doc['textures'].append({'source':image})
            record.append({'runtime_file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'kind':kind,'preview_dimensions':size})
            return index
        for material in doc['materials']:
            name=material['name'];base=files.get((name+'.png').lower())
            if base is None:raise ValueError('No matching runtime texture for preview material '+name)
            material['pbrMetallicRoughness']={'baseColorTexture':{'index':texture(base,'base')},'metallicFactor':0,'roughnessFactor':0.8}
            normal=files.get((name+'_normal.png').lower());orm=files.get((name+'_orm.png').lower())
            if normal:material['normalTexture']={'index':texture(normal,'normal')}
            if orm:
                index=texture(orm,'orm');material['pbrMetallicRoughness'].update(metallicRoughnessTexture={'index':index},metallicFactor=1,roughnessFactor=1);material['occlusionTexture']={'index':index}
        while len(payload)%4:payload.append(0)
        doc['buffers']=[{'byteLength':len(payload)}];doc['asset']['generator']='OpenReliant sltool 0.7.0 geometry; OpenReliant Art Packs viewing-only textures'
        encoded=json.dumps(doc,separators=(',',':')).encode()
        encoded+=b' '*((-len(encoded))%4)
        glb=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(payload))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(payload),0x004e4942)+payload
        output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(glb)
        return {'model':model.name,'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'preview_sha256':hashlib.sha256(glb).hexdigest(),'preview_bytes':len(glb),'highest_detail_geometry':True,'textures':record,'limitations':'Viewing copy with reduced texture resolution and browser lighting; in-game screenshots show actual engine appearance.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('model',type=Path);p.add_argument('mod_folder',type=Path);p.add_argument('output',type=Path);p.add_argument('--sltool',type=Path,required=True);p.add_argument('--maximum',type=int,default=1024);a=p.parse_args();print(json.dumps(build(a.model,a.mod_folder,a.output,a.sltool,a.maximum),indent=2))
