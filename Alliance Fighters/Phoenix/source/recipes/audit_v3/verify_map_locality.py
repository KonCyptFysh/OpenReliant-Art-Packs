import os
from pathlib import Path
import json,numpy as np
from PIL import Image
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v3'
old=json.loads((D/'work/audit_v2/validation.json').read_text());new=json.loads((W/'validation.json').read_text())
def pixels(p):return np.asarray(Image.open(p).convert('RGB'))
edit=pixels(new['audit_changes']['edit_mask']['path'])[:,:,0];outside=edit==0;result=[]
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=pixels(old['maps'][key]['path']);b=pixels(new['maps'][key]['path']);diff=np.max(np.abs(a.astype(int)-b.astype(int)),axis=-1)
 assert not np.any((diff>1)&outside),(key,'outside edit footprint')
 result.append({'map':key,'changed_pixels_outside_window_edit_mask_over_one_level':int(np.count_nonzero((diff>1)&outside))})
S=4096;scale=S/1254;x0,y0,x1,y1=[int(round(v*scale)) for v in new['audit_changes']['edit_bounds_atlas']];yy,xx=np.mgrid[y0:y1,x0:x1]
tri=np.array(new['audit_changes']['triangle_atlas_pixels']);inv=np.linalg.inv(np.vstack([tri.T,np.ones(3)]));bary=np.stack([(xx+.5)/scale,(yy+.5)/scale,np.ones_like(xx)],-1)@inv.T
g=pixels(new['maps']['glass']['path'])[y0:y1,x0:x1,0]>128;seal=pixels(new['maps']['seal']['path'])[y0:y1,x0:x1,0]>128
assert np.all(bary[g|seal]>=0), 'Glass or seal spills outside triangular mesh boundary'
glass={}
for key in ['basecolor','roughness','metallic','normal']:
 a=pixels(new['maps'][key]['path'])[y0:y1,x0:x1];core=pixels(new['maps']['glass']['path'])[y0:y1,x0:x1,0]==255
 glass[key]={'core_min':a[core].min(0).tolist(),'core_max':a[core].max(0).tolist()}
assert glass['metallic']['core_max']==[0,0,0]
(W/'map_locality.json').write_text(json.dumps({'locality':result,'glass_and_seal_inside_triangle':True,'glass_material':glass},indent=2)+'\n')
print(json.dumps({'maps_verified':len(result),'glass_and_seal_inside_triangle':True,'glass_material':glass},indent=2))
