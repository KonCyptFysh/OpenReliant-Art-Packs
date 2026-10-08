import os
import json,hashlib,numpy as np
from pathlib import Path
from PIL import Image
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v5';r=json.loads((W/'validation.json').read_text());base=json.loads((D/'work/reconstruction_v1/validation.json').read_text())
def pix(p):return np.asarray(Image.open(p).convert('RGB'))
edit=pix(r['audit_changes']['edit_mask']['path'])[:,:,0];glass=pix(r['maps']['glass']['path'])[:,:,0];checks=[]
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=pix(base['maps'][key]['path']);b=pix(r['maps'][key]['path']);delta=np.max(np.abs(b.astype(int)-a.astype(int)),axis=-1);allowed=glass if key=='basecolor' else edit
 count=int(np.count_nonzero((delta>1)&(allowed==0)));assert count==0,(key,count)
 checks.append({'map':key,'changed_pixels_outside_original_panes' if key=='basecolor' else 'changed_pixels_outside_glazing_footprint':count})
core=glass==255;optics={}
for key in ['basecolor','roughness','metallic']:
 a=pix(r['maps'][key]['path']);optics[key]={'glass_core_min':a[core].min(0).tolist(),'glass_core_max':a[core].max(0).tolist()}
assert optics['metallic']['glass_core_max']==[0,0,0]
assert all(v<=1 for v in np.subtract(optics['basecolor']['glass_core_max'],optics['basecolor']['glass_core_min']))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();models=[]
for name in ['USPF_Phx.SHP','t_USPF_Phx.SHP','Phoenix_gun.SHP']:
 a=D/'exports/openreliant_v2/mods/98-phoenix-worn-v1'/name;b=D/'exports/openreliant_v5/mods/98-phoenix-worn-v1'/name;assert sha(a)==sha(b),name
 models.append({'file':name,'exact_match_to_v2_original_window_uvs_and_repaired_belly':True,'sha256':sha(b)})
(W/'map_locality.json').write_text(json.dumps({'checks':checks,'optics':optics,'original_frames_and_surrounding_colours_preserved':True,'native_models':models},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'original_frames_preserved':True,'native_models_equal_v2':len(models),'optics':optics},indent=2))
