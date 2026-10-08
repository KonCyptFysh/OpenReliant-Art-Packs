from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
def binary_erosion(a,iterations):return np.array(Image.fromarray(a.astype(np.uint8)*255).filter(ImageFilter.MinFilter(2*iterations+1)))>0
D=Path(__file__).resolve().parents[2];M=D/'maps';W=D/'recipes/reconstruction_v1';O=D/'exports/openreliant_v1/mods/99-crusader-worn-v1'
def arr(name):return np.array(Image.open(M/f'crusader_worn_{name}_4k_v1.png').convert('RGB'))
normal=arr('normal').astype(np.float32)/255*2-1;glass=binary_erosion(arr('glass')[:,:,0]>250,iterations=8);flat=binary_erosion(arr('flat_graphics')[:,:,0]>250,iterations=8);metal=arr('metallic')[:,:,0];rough=arr('roughness')[:,:,0];nerr=float(np.abs(normal[glass|flat,:2]).max());assert nerr<.005,nerr;assert metal[glass].max()==0;assert np.abs(rough[glass].astype(float)/255-.14).max()<.005
orm=np.array(Image.open(O/'orcr1_hull_orm.png'));assert (orm[:,:,0]==255).all() and np.array_equal(orm[:,:,1],rough) and np.array_equal(orm[:,:,2],metal)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for suffix in ['','_normal','_orm']:assert sha(O/f'orcr1_hull{suffix}.png')==sha(O/f'gorcr1_hull{suffix}.png')
maps=[]
for p in M.glob('*.png'):
 with Image.open(p) as im:
  size=im.size;im.verify()
 if '_4k_' in p.name:assert size==(4096,4096)
 maps.append(dict(file=p.name,dimensions=size,sha256=sha(p)))
report=dict(passed=True,maps=maps,glass_flat_normal_max_xy=nerr,glass_metallic_max=int(metal[glass].max()),glass_roughness_median=float(np.median(rough[glass])/255),flat_insignia_and_label_normals=True,orm_channel_packing_verified=True,matching_loadout_maps=True,normal_type='OpenGL tangent space, structural height only')
(W/'map_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('Crusader maps checked: flat glass and insignia, ORM channels and matching loadout copies.')
