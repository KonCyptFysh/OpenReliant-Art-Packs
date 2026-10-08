import os
import json,hashlib,numpy as np
from pathlib import Path
from PIL import Image
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v6';r=json.loads((W/'validation.json').read_text());old=json.loads((D/'work/audit_v5/validation.json').read_text());base=json.loads((D/'work/reconstruction_v1/validation.json').read_text())
def pix(p):return np.asarray(Image.open(p).convert('RGB'))
edit=pix(r['audit_changes']['edit_mask']['path'])[:,:,0];glass=pix(r['maps']['glass']['path'])[:,:,0];oldglass=pix(old['maps']['glass']['path'])[:,:,0];checks=[]
for key in ['basecolor','roughness','metallic','normal','glass','seal','height','structure','panels','paint']:
 a=pix(old['maps'][key]['path']);b=pix(r['maps'][key]['path']);delta=np.max(np.abs(b.astype(int)-a.astype(int)),axis=-1);allowed=np.maximum(glass,oldglass) if key=='basecolor' else edit
 count=int(np.count_nonzero((delta>1)&(allowed==0)));assert count==0,(key,count)
 checks.append({'map':key,'changed_pixels_outside_glazing_edit_footprint':count})
a=pix(base['maps']['basecolor']['path']);b=pix(r['maps']['basecolor']['path']);assert not np.any((np.max(np.abs(a.astype(int)-b.astype(int)),axis=-1)>1)&(glass==0))
core=glass==255;optics={}
for key in ['basecolor','roughness','metallic','normal']:
 a=pix(r['maps'][key]['path']);optics[key]={'glass_core_min':a[core].min(0).tolist(),'glass_core_max':a[core].max(0).tolist()}
assert optics['metallic']['glass_core_max']==[0,0,0]
assert all(v<=1 for v in np.subtract(optics['basecolor']['glass_core_max'],optics['basecolor']['glass_core_min']))
assert np.max(np.abs(np.array(optics['normal']['glass_core_min'])-[128,128,255]))<=1
assert np.max(np.abs(np.array(optics['normal']['glass_core_max'])-[128,128,255]))<=1
normal=pix(r['maps']['normal']['path']).astype(np.float32)/127.5-1;normal/=np.linalg.norm(normal,axis=2,keepdims=True);angle=np.rad2deg(np.arccos(np.clip(normal[:,:,2],-1,1)));edge=(glass>0)&(glass<255)
normal_checks={'max_glass_core_normal_degrees':float(angle[core].max()),'max_glass_boundary_normal_degrees':float(angle[edge].max()),'previous_max_glass_boundary_normal_degrees':r['audit_changes']['reflection_diagnosis']['previous_edge_normal_max_degrees']};assert normal_checks['max_glass_boundary_normal_degrees']<.5
# Inspect independently selected dark-glass points omitted by v5.
coverage=[]
for name,x,y in [('middle_forward_upper',750,690),('middle_upper_edge',772,684),('roof_forward_corner',731,601),('forward_side_upper',690,696)]:
 i,j=int(y*4096/1254),int(x*4096/1254);v=int(glass[i,j]);previous=int(oldglass[i,j]);assert v>=250,(name,v);coverage.append({'sample':name,'atlas_xy':[x,y],'previous_coverage':previous,'coverage':v})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();models=[]
for name in ['USPF_Phx.SHP','t_USPF_Phx.SHP','Phoenix_gun.SHP']:
 a=D/'exports/openreliant_v5/mods/98-phoenix-worn-v1'/name;b=D/'exports/openreliant_v6/mods/98-phoenix-worn-v1'/name;assert sha(a)==sha(b),name
 models.append({'file':name,'exact_match_to_v5_geometry_normals_uvs_and_repaired_belly':True,'sha256':sha(b)})
result={'checks':checks,'optics':optics,'normal_checks':normal_checks,'coverage_samples':coverage,'original_frames_and_surrounding_colours_preserved':True,'native_models':models}
(W/'map_locality.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'original_frames_preserved':True,'native_models_equal_v5':len(models),'normal_checks':normal_checks,'coverage_samples':coverage},indent=2))
