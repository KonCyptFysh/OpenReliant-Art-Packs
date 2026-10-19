from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,shutil
D=Path('${RELIANT_WORKSPACE}');W=D/'work/frame_relief_v6';M=D/'maps/frame_relief_v6';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
for suffix in ['_normal','_orm']:shutil.copy2(M/f'orr2_hull{suffix}.png',S/f'orr2_hull{suffix}.png')
p=S/'mod.ini';p.write_text(p.read_text().replace('0.1.0-beta.5','0.1.0-beta.6'))
for tier,n in [('2k',2048),('1k',1024)]:
 T=D/f'exports/review_v1_{tier}/mods'/S.name
 for suffix in ['_normal','_orm']:
  name=f'orr2_hull{suffix}.png';im=Image.open(M/name).convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
  if suffix=='_normal':
   a=np.asarray(im).astype('float32')/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-8);im=Image.fromarray(np.uint8(np.clip(a*.5+.5,0,1)*255+.5))
  im.save(T/name)
 shutil.copy2(S/'mod.ini',T/'mod.ini')
p=D/'README.md';s=p.read_text().replace('# Reliant — Worn Paint, surface revision 5','# Reliant — Worn Paint, surface revision 6').replace('Status: local surface revision 5','Status: local surface revision 6')
at=s.index('## Surface revision 5');s=s[:at]+'''## Surface revision 6 — structural frame bevel correction

The previous pocket normals followed the bright frame ridge with a fixed, steep
ramp. This produced a separate dark strip beside the painted bevel, especially at
diagonal corners. The glass treatment from revision 5 is retained.

All 160 edges of the 20 REL_2 structural pockets now use measured painted
transition positions and widths. Reduced pocket depth removes the near-vertical
false wall. The normal, supporting height and cavity occlusion share these new
transitions. Window bezel/glass normals, all colour/emission/roughness/metallic
channels, native geometry, UVs and lighting scripts are unchanged.

Current editable scene: `reliant_worn_pbr_v6.blend`.
Current maps: `maps/frame_relief_v6/`.
Measurements, source, before/after detail and validation: `work/frame_relief_v6/`.
Revision 5 is preserved in `history/stages/pre_frame_relief_v6/`.

Official OpenReliant 0.18.0 checks cover matched-camera before/after views, both
bridge sides with rotated lighting, the forward window banks and machinery frame.
1K, 2K and 4K packs are refreshed. Local visual review remains pending.

'''+s[at:];s=s.replace('`reliant_worn_pbr_v5.blend` is the current editable hull scene','`reliant_worn_pbr_v6.blend` is the current editable hull scene');p.write_text(s)
# Comparison crops have identical 2x scale in both axes; no image warping.
out=Image.new('RGB',(840,768),(24,24,24));dr=ImageDraw.Draw(out)
for i,v in enumerate(['v5','v6']):
 im=Image.open(W/f'{v}-bridge-cell.png').crop((800,245,1220,425)).resize((840,360),Image.Resampling.LANCZOS);out.paste(im,(0,24+i*384));dr.text((8,6+i*384),'Before' if i==0 else 'Corrected bevel',fill='white')
out.save(W/'frame-before-after.png');print('V6_EXPORTS_PREPARED',flush=True)
