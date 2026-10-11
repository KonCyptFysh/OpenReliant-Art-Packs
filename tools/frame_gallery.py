#!/usr/bin/env python3
"""Frame fresh engine captures without painting, compositing or altering artwork."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def bounds(image):
 a=np.asarray(image.convert('RGB'));mask=(a[:,:,0]>28)&(a[:,:,1]>20)&(a[:,:,0].astype(float)>a[:,:,2]*0.9)
 # The fixed cool nebula remains below the red threshold. Remove isolated stars;
 # retain disconnected ship parts/attachments with a solid 3 by 3 pixel patch.
 clean=Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(5))
 selected=np.asarray(clean)>0
 y,x=np.where(selected);assert len(x)>10000,'No complete ship was found'
 return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

def frame(raw, box):
 x0,y0,x1,y1=box;cx=(x0+x1)/2;cy=(y0+y1)/2
 # 76% of either frame dimension: roomy enough for dark outlines and light bloom.
 width=math.ceil(max((x1-x0)/.76,(y1-y0)/.76*4/3)/4)*4;height=width*3//4
 width=max(width,1280);height=width*3//4
 left=round(cx-width/2);top=round(cy-height/2)
 left=max(0,min(left,raw.width-width));top=max(round(raw.height*.105),min(top,round(raw.height*.895)-height))
 assert left>=0 and top>=0 and left+width<=raw.width and top+height<=raw.height
 crop=[left,top,left+width,top+height]
 result=raw.crop(crop).resize((1280,960),Image.Resampling.LANCZOS)
 return result,crop

def prepare(args):
 R=args.repository;T=args.workspaces
 c=json.loads((R/'catalog.json').read_text());reports=[];thumbs=[]
 for a in c['assets']:
  work=T/Path(a.get('folder','none')).name/'worn/work/gallery_standard_v1'
  if not work.exists():continue
  e=a['liveries'][0];records=[]
  inputs=[]
  for record in sorted(work.glob('*.json'),key=lambda p:(p.stem!='overview',p.name)):
   r=json.loads(record.read_text())
   if isinstance(r,dict) and 'raw_file' in r:inputs.append(r)
  boxes=[bounds(Image.open(r['raw_file'])) for r in inputs]
  union=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
  for r,box in zip(inputs,boxes):
   assert sha(R/r['runtime_manifest'])==r['runtime_manifest_sha256'], a['id']+' needs a current capture'
   path=Path(r['raw_file']);assert sha(path)==r['raw_sha256'];raw=Image.open(path).convert('RGB')
   picture,crop=frame(raw,union)
   target=R/'docs/assets'/a['id']/('gallery-'+r['mode']+'-v1.webp');target.parent.mkdir(parents=True,exist_ok=True)
   picture.save(target,'WEBP',quality=94,method=6)
   r.update(gallery_file=str(target.relative_to(R/'docs')),gallery_sha256=sha(target),
    gallery_dimensions=[1280,960],detected_ship_bounds=box,crop=crop,
    conversion='Crop and Lanczos downsample, WebP quality 94; no retouching, mirroring or background replacement')
   records.append(r);reports.append(r)
   thumbs.append((a['name']+' / '+r['mode'],picture.copy()))
  (work/'framing.json').write_text(json.dumps(records,indent=2)+'\n')
 if args.publish_catalog:
  expected={a['id'] for a in c['assets'] if a['status']=='available' and a['category'] in ['alliance-fighters','coalition-fighters','torpedo-bombers']}
  assert {r['asset'] for r in reports}==expected
  for a in c['assets']:
   records=[r for r in reports if r['asset']==a['id']]
   if not records:continue
   records.sort(key=lambda r:r['mode']!='overview');e=a['liveries'][0]
   captions={'overview':'Front three-quarter view','deployed':'Deployed — matching camera','fighting':'Fighting position — matching camera'}
   e.update(preview=records[0]['gallery_file'],defaultPreview='image',previewSource='Fresh capture in official OpenReliant 0.8.1',
    previewType='capture',previewArtworkRevision=e['assetRevision'],
    images=[dict(src=r['gallery_file'],caption=a['name']+' — '+captions[r['mode']]) for r in records])
   e['notes']=[n for n in e.get('notes',[]) if not any(x in n.lower() for x in ['photo predates','still is a blender','in-game gallery photo','in-game photo pending'])]
   if 'Gallery captures are from the earlier artwork review' in e.get('validationSummary',''):
    e['validationSummary']='Official OpenReliant 0.8.1 native-file and texture-loader checks passed. Fresh gallery captures show the current repository artwork; broader gameplay and other platforms still need testing.'
  (R/'catalog.json').write_text(json.dumps(c,indent=2,ensure_ascii=False)+'\n')
  (R/'tracking/gallery-standard-captures.json').write_text(json.dumps({'profile':'ship-gallery-v1','ships':len(expected),'photographs':len(reports),'captures':reports},indent=2)+'\n')
 columns=5;w=320;h=264;sheet=Image.new('RGB',(columns*w,math.ceil(len(thumbs)/columns)*h),(16,21,19));draw=ImageDraw.Draw(sheet)
 for i,(name,im) in enumerate(thumbs):
  im.thumbnail((320,240));x=i%columns*w;y=i//columns*h;sheet.paste(im,(x,y));draw.text((x+8,y+242),name,fill=(235,235,224))
 sheet.save(args.contact)
 print(json.dumps({'ships':len({r['asset'] for r in reports}),'photos':len(reports),'contact':str(args.contact)},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True);p.add_argument('--workspaces',type=Path,required=True)
 p.add_argument('--contact',type=Path,required=True);p.add_argument('--publish-catalog',action='store_true');prepare(p.parse_args())
