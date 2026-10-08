import os
import json,hashlib,numpy as np
from pathlib import Path
from PIL import Image
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v7';r=json.loads((W/'validation.json').read_text());old=json.loads((D/'work/audit_v6/validation.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pix(p):return np.asarray(Image.open(p).convert('RGB'))
edit=pix(r['audit_changes']['relief_edit_mask']['path'])[:,:,0];opening=pix(r['audit_changes']['relief_opening_mask']['path'])[:,:,0];checks=[]
for key in ['normal','roughness','metallic','height','structure','fins']:
 a=pix(old['maps'][key]['path']);b=pix(r['maps'][key]['path']);delta=np.max(np.abs(a.astype(int)-b.astype(int)),axis=2);outside=int(np.count_nonzero((delta>1)&(edit==0)));assert outside==0,(key,outside);checks.append({'map':key,'changed_pixels_outside_intake_vent_edit_region':outside})
for key in ['basecolor','glass','seal','flat_graphics','panels','paint']:assert sha(old['maps'][key]['path'])==sha(r['maps'][key]['path'])
normal=pix(r['maps']['normal']['path']);cleared=(edit==255)&(opening==0);q=normal[cleared].astype(int);assert np.max(np.abs(q-np.array([128,128,255])))<=1
fins=pix(r['maps']['fins']['path'])[:,:,0];assert np.max(fins[cleared])==0
oldn=pix(old['maps']['normal']['path']);bad=np.max(np.abs(oldn[cleared].astype(int)-[128,128,255]),axis=1)>4;old_pixels=int(np.count_nonzero(bad))
# Existing glazing faces remain in the main family with unchanged coordinates.
glazing=range(74,92)
for fi in glazing:assert r['models']['Phoenix_Cockpit']['faces'][fi]==old['models']['Phoenix_Cockpit']['faces'][fi]
joins=json.loads((W/'belly_shared_edges.json').read_text());assert joins and max(j['max_uv_gap_pixels'] for j in joins)<1e-5
for key,m in r['repair_maps'].items():
 assert sha(m['path'])==m['sha256'];im=Image.open(m['path']);assert im.size==(4096,4096);im.verify()
result={'main_map_locality':checks,'main_basecolor_and_glazing_masks_byte_identical':True,'glazing_face_uvs_and_materials_unchanged':True,'incorrect_relief_pixels_cleared_outside_actual_openings':old_pixels,'new_relief_normals_outside_openings_flat':True,'fin_relief_contained_by_openings':True,'belly_continuous_shared_edges':len(joins),'max_belly_shared_edge_uv_gap_pixels':max(j['max_uv_gap_pixels'] for j in joins),'surface_bake_faces':len(r['audit_changes']['surface_faces']),'repair_maps_verified':len(r['repair_maps'])}
(W/'map_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
