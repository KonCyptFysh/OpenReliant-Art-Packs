from pathlib import Path
import json,shutil
D=Path('${RELIANT_WORKSPACE}');W=D/'work/refinement_v2';M=D/'maps/refinement_v2';M.mkdir(exist_ok=True)
for a,b in [(W/'art/rel1_basecolor.png',M/'orr1_hull.png'),(W/'art/rel2_basecolor.png',M/'orr2_hull.png'),(D/'maps/reliant_rel3_basecolor_v1.png',M/'orr3_hull.png'),(W/'art/all_trt_reconstructed.png',M/'orr_cgun_source.png')]:shutil.copy2(a,b)
O=D.parent.parent/'Ordnance/worn/maps'
for a,b in [('ordnance_basecolor_2k_v1.png','orr_sgun_source.png'),('ordnance_height_2k_v1.png','orr_sgun_height_source.png'),('ordnance_flat_graphics_2k_v1.png','orr_sgun_flat_source.png')]:shutil.copy2(O/a,M/b)
print(M)
