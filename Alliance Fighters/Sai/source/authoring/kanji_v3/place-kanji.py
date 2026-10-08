from pathlib import Path
import subprocess, json, hashlib, shutil
from PIL import Image
import numpy as np

D=Path('/home/lva-8700/Documents/ABANDONEWARE_JESUS/assets/working/textures/Sai/worn')
W=D/'work/kanji_v3'; M=D/'maps/kanji_v3'; Q=D/'review/kanji_v3'; H=D/'history/stages/pre_kanji_v3'
for p in [W,M,Q,H]: p.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): subprocess.run(['magick','-limit','thread','4',*[str(q) for q in a]],check=True)
state=json.loads((D.parent/'project_state.json').read_text())
assert state['latest_pass']=='decals_v2'
for p in [D.parent/'project_state.json',D/'manifest.json',D/'README.md']:
 if p.exists() and not (H/p.name).exists(): shutil.copy2(p,H/p.name)
maps=json.loads(json.dumps(state['maps']))
base=Path(maps['sam1']['basecolor']['path']); assert sha(base)==maps['sam1']['basecolor']['sha256']
# Original footprints measured on the pre-remap 4096px artwork. Fit the ink
# uniformly, retain the original centre and never reflect a kanji image.
specs=[dict(name='nose',text='侍飛将',file='sai_侍飛将_red_vertical.png',box=[1725,2918,2175,4070]),dict(name='tail',text='神風',file='sai_神風_black_horizontal.png',box=[228,510,1245,1060])]
placements=[]; layer=W/'sai_kanji_placement_layer.png'
run('-size','8192x4096','xc:none','-colorspace','sRGB','-type','TrueColorAlpha','PNG32:'+str(layer))
for spec in specs:
 src=D/'decals/kanji_v1'/spec['file']; a=np.array(Image.open(src))[:,:,3]; yy,xx=np.where(a>8)
 x0,y0,x1,y1=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
 box=[48+q*4000/4096 for q in spec['box']]; tw,th=box[2]-box[0],box[3]-box[1]
 scale=min(tw/(x1-x0),th/(y1-y0)); width=round((x1-x0)*scale);height=round((y1-y0)*scale)
 fitted=W/(spec['name']+'_scaled.png')
 run(src,'-crop',f'{x1-x0}x{y1-y0}+{x0}+{y0}','+repage','-filter','Lanczos','-resize',f'{width}x{height}!',fitted)
 x=round((box[0]+box[2]-width)/2);y=round((box[1]+box[3]-height)/2)
 for side,px in [('left',x),('right',8192-x-width)]:
  run(layer,'-colorspace','sRGB',fitted,'-geometry',f'+{px}+{y}','-compose','Over','-composite','PNG32:'+str(layer))
  placements.append(dict(text=spec['text'],region=spec['name'],side=side,position_px=[px,y],size_px=[width,height],source=str(src),source_sha256=sha(src),source_ink_crop=[x0,y0,x1,y1],uniform_scale=scale,rotation_degrees=0,mirrored=False,original_4k_footprint=spec['box']))
# Leave physical panel gaps visible through the lettering. These trace the
# existing atlas gaps; the mirrored hull gets a mirrored gap mask, not text.
seams=W/'panel_gap_protection.svg'
seams.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="8192" height="4096"><rect width="8192" height="4096" fill="white"/><defs><g id="gaps" fill="none" stroke="black" stroke-linecap="round"><path stroke-width="16" d="M517 439 L517 1800 M0 670 L517 670 M1612 3518 L1833 3747 L2218 3747 M1833 3747 L1833 4096 M1500 3885 L1833 3885"/></g></defs><use href="#gaps"/><use href="#gaps" transform="translate(8192 0) scale(-1 1)"/></svg>''')
run(seams,W/'panel_gap_protection.png')
run(layer,'-alpha','extract',W/'alpha_raw.png')
run(W/'alpha_raw.png',W/'panel_gap_protection.png','-compose','Multiply','-composite',W/'alpha_final.png')
run(layer,W/'alpha_final.png','-alpha','off','-compose','CopyOpacity','-composite',M/'sai_kanji_decals_lr_v3.png')
result=M/'sai_sam1_basecolor_lr_v3.png'
run(base,M/'sai_kanji_decals_lr_v3.png','-compose','Over','-composite','-alpha','off','-depth','8',result)
old=np.array(Image.open(base).convert('RGB'));new=np.array(Image.open(result).convert('RGB'));alpha=np.array(Image.open(M/'sai_kanji_decals_lr_v3.png').getchannel('A'))
changed=np.any(new!=old,axis=-1);assert not np.any(changed&(alpha==0));assert np.any(changed[:,:4096]) and np.any(changed[:,4096:])
maps['sam1']['basecolor']={'path':str(result),'dimensions':[8192,4096],'sha256':sha(result)}
report={'status':'placement prepared for mesh review','maps':maps,'prior_scene':state['latest_scene'],'prior_scene_sha256':sha(state['latest_scene']),'placements':placements,'source_decals_unchanged':True,'all_pixels_outside_decal_alpha_identical':True,'changed_basecolor_pixels':int(changed.sum()),'other_texture_maps_unchanged':True,'method':'Uniformly scaled approved PNG decals, independent normal-reading placement in both atlas halves, original panel gaps protected.','runtime_visual_review':'pending_user_review'}
(W/'placement.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name,box in [('nose_left',[1620,2810,2245,4048]),('nose_right',[5947,2810,6572,4048]),('tail_left',[180,430,1370,1170]),('tail_right',[6822,430,8012,1170])]:
 x0,y0,x1,y1=box;run(result,'-crop',f'{x1-x0}x{y1-y0}+{x0}+{y0}','+repage',Q/(name+'_atlas.png'))
shutil.copy2(__file__,W/'place-kanji.py')
print(json.dumps({k:v for k,v in report.items() if k!='maps'},ensure_ascii=False,indent=2))
