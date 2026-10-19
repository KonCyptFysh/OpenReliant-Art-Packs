from pathlib import Path
from PIL import Image
import numpy as np,shutil
D=Path('${RELIANT_WORKSPACE}');M=D/'maps/machinery_v9';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'
for suffix in ['', '_normal','_orm']:shutil.copy2(M/f'orr2_hull{suffix}.png',S/f'orr2_hull{suffix}.png')
p=S/'mod.ini';p.write_text(p.read_text().replace('0.1.0-beta.8','0.1.0-beta.9'))
for tier,n in [('2k',2048),('1k',1024)]:
    T=D/f'exports/review_v1_{tier}/mods'/S.name
    for suffix in ['', '_normal','_orm']:
        name=f'orr2_hull{suffix}.png';im=Image.open(M/name).convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
        if suffix=='_normal':
            a=np.asarray(im).astype('float32')/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1e-8);im=Image.fromarray(np.uint8(np.clip(a*.5+.5,0,1)*255+.5))
        im.save(T/name)
    shutil.copy2(S/'mod.ini',T/'mod.ini')
print('1K 2K 4K EXPORTS PREPARED; NATIVE MESHES AND SCRIPTS RETAINED',flush=True)
