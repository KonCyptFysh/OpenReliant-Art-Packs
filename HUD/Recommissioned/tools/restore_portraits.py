#!/usr/bin/env python3
"""Restore uncovered portrait sequences with the existing RealBasicVSR x4 recipe.

Reads the sltool audit exports; writes a separate staging collection. Existing
HUD frames and runtime files are never modified by this command.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, time
import numpy as np
from PIL import Image
import torch
from portrait_temporal_inference import load_realbasicvsr, evaluate

MODEL_SHA = '52f77c2c835aaa3fe675b3959b2f85010a6c6f63f77f7e279394646e55a4e376'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save_json(p, data):
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)

def restore(args):
    assert sha(args.checkpoint)==MODEL_SHA, 'Use the checkpoint that made the existing HD collection'
    inventory={x['filename']:x for x in json.loads((args.audit/'inventory.json').read_text())}
    coverage=json.loads((args.audit/'coverage-review.json').read_text())
    queue=sorted(coverage['additional_distinct_sequences'], key=lambda n:(inventory[n]['native']['frames'],n.casefold()))
    args.output.mkdir(parents=True,exist_ok=True)
    state={'status':'running','model':'RealBasicVSR GAN x4','checkpoint_sha256':MODEL_SHA,
           'content_size':[480,400],'fps':15,'frame_interpolation':False,'completed':[],
           'active':None,'total_sequences':len(queue),'total_frames':sum(inventory[n]['native']['frames'] for n in queue)}
    device=torch.device(args.device)
    if device.type=='cuda':
        assert torch.cuda.is_available()
        state['device']=torch.cuda.get_device_name(device)
    torch.set_num_threads(8)
    model=load_realbasicvsr(args.checkpoint,device)
    for name in queue:
        item=inventory[name];clip=args.output/Path(name).stem;record=clip/'manifest.json'
        state['active']=name;save_json(args.output/'status.json',state)
        if record.exists():
            existing=json.loads(record.read_text())
            assert existing['source_fm8_sha256']==item['source_sha256']
            for f in existing['frames']:assert sha(clip/f['path'])==f['sha256']
            state['completed'].append(name)
            continue
        clip.mkdir(exist_ok=True);out=clip/'frames';out.mkdir(exist_ok=True)
        started=time.monotonic();print('Restoring',name,len(item['frame_paths']),'frames',flush=True)
        source=np.stack([np.asarray(Image.open(args.audit/p).convert('RGB'),dtype=np.uint8) for p in item['frame_paths']])
        assert source.shape==(item['native']['frames'],100,120,3)
        tensor=torch.from_numpy(source.astype(np.float32)/255.0).permute(0,3,1,2).unsqueeze(0).to(device)
        with torch.inference_mode():
            result=model(tensor).clamp_(0.0,1.0)
        restored=result.squeeze(0).permute(0,2,3,1).mul(255.0).round().byte().cpu().numpy()
        assert restored.shape==(len(source),400,480,3)
        del tensor,result
        if device.type=='cuda':torch.cuda.empty_cache()
        files=[]
        for i,pixels in enumerate(restored,1):
            p=out/f'frame_{i:04d}.png';Image.fromarray(pixels).save(p,optimize=True)
            files.append({'path':p.relative_to(clip).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','15','-i',str(out/'frame_%04d.png'),
                        '-c:v','libx264','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',str(clip/'preview.mp4')],check=True)
        data={'status':'complete','filename':name,'source_fm8_sha256':item['source_sha256'],
              'source_decoded_rgba_sha256':item['decoded_rgba_sequence_sha256'],
              'source_frame_count':len(source),'output_frame_count':len(restored),'source_dimensions':[120,100],
              'output_dimensions':[480,400],'fps':15,'frame_interpolation':False,'model':state['model'],
              'model_checkpoint_sha256':MODEL_SHA,'torch_version':torch.__version__,'device':state.get('device',str(device)),
              'temporal_metrics':evaluate(source,restored),'frames':files,
              'elapsed_seconds':round(time.monotonic()-started,2),
              'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        save_json(record,data);state['completed'].append(name);save_json(args.output/'status.json',state)
        print('Completed',name,data['elapsed_seconds'],'seconds',flush=True)
    state.update(status='complete',active=None);save_json(args.output/'status.json',state)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--device',default='cuda')
    restore(p.parse_args())
