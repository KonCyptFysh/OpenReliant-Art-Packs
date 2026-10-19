from pathlib import Path
from PIL import Image
import numpy as np,shutil
D=Path('${RELIANT_WORKSPACE}');S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';M=D/'maps/windows_v5'
for suffix in ['','_emissive','_normal','_orm']:shutil.copy2(M/f'orr2_hull{suffix}.png',S/f'orr2_hull{suffix}.png')
p=S/'mod.ini';p.write_text(p.read_text().replace('0.1.0-beta.4','0.1.0-beta.5'))
for tier,n in [('2k',2048),('1k',1024)]:
 T=D/f'exports/review_v1_{tier}/mods'/S.name
 for suffix in ['','_emissive','_normal','_orm']:
  name=f'orr2_hull{suffix}.png';im=Image.open(M/name).convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
  if suffix=='_normal':
   a=np.asarray(im).astype('float32')/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-8);im=Image.fromarray(np.uint8(np.clip(a*.5+.5,0,1)*255+.5))
  im.save(T/name)
 shutil.copy2(S/'mod.ini',T/'mod.ini');print('TIER',tier,flush=True)
p=D/'README.md';s=p.read_text().replace('# Reliant — Worn Paint, surface revision 4','# Reliant — Worn Paint, surface revision 5').replace('Status: local surface revision 4','Status: local surface revision 5');at=s.index('## Surface revision 4');s=s[:at]+'''## Surface revision 5 — reauthored window materials

All 64 existing windows retain their rectangular layout. Each now has a worn steel
mounting bezel, dark gasket and recessed smoked glazing. Subtle glass abrasion,
edge dirt and softly lit cabin detail replace the uniform gold fill. Window inserts
are oriented using their native UV-to-mesh mapping, including the inverted forward
banks. Interiors are texture detail behind opaque glazing; no new interior mesh was added.

Colour, emission, normal, structural height, cavity, roughness and metallic maps
share the same frame/glass coordinates. The glass is nonmetallic and smoother than
the surrounding steel; seals are rough. Frames emit no light. Uneven warm interior
illumination keeps its detail when the existing health dimming, flicker and surges run.
The structural height master for REL_2 is now 4096 pixels; its normal map already
includes that relief, so it should not be combined with a second full-strength bump pass.

Current scene: `reliant_worn_pbr_v5.blend`. Current maps: `maps/windows_v5/`.
Editable assembly and exact window regions: `work/windows_v5/`.

Artwork was created with the built-in ImageGen tool. The retained
[source artwork](work/windows_v5/window-art-source.png) and
[complete prompt](work/windows_v5/imagegen-prompt.txt) are part of the source package.
Generated glass/frame art is fitted through fixed rectangular material masks;
all pixels outside the window patches remain identical to revision 4.
Revision 4 is preserved in `history/stages/pre_windows_v5/`.

Official 0.18.0 checks cover lit/unlit glazing, changed lighting angles and both bridge
sides. 1K, 2K and 4K review packs contain the matching window material set.
This remains a local review awaiting the user's visual approval.

'''+s[at:];s=s.replace('`reliant_worn_pbr_v4.blend` is the current editable hull scene','`reliant_worn_pbr_v5.blend` is the current editable hull scene');p.write_text(s)
