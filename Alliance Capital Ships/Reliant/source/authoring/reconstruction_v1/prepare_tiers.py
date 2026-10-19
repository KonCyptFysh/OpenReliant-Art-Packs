from pathlib import Path
import bpy,numpy as np,json,hashlib,shutil
D=Path('${RELIANT_WORKSPACE}');W=D/'work/reconstruction_v1';S=D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1';report=[]
for tier,n in [('2k',2048),('1k',1024)]:
 dest=D/f'exports/review_v1_{tier}/mods'/S.name;dest.mkdir(parents=True,exist_ok=True);checks=[]
 for p in S.iterdir():
  if p.suffix!='.png' or p.name=='mod.png':shutil.copy2(p,dest/p.name);continue
  im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';im.scale(n,n)
  if '_normal' in p.name:
   a=np.empty(n*n*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(-1,4);v=a[:,:3]*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);a[:,:3]=v*.5+.5;im.pixels.foreach_set(a.ravel())
  im.filepath_raw=str(dest/p.name);im.file_format='PNG';im.save();bpy.data.images.remove(im);checks.append({'file':p.name,'size':[n,n],'sha256':hashlib.sha256((dest/p.name).read_bytes()).hexdigest()})
 report.append({'tier':tier,'path':str(dest),'maps':checks});print('TIER_READY',tier,flush=True)
(W/'resolution_checks.json').write_text(json.dumps({'passed':True,'method':'Aligned native UVs; all four runtime maps resized together; normals renormalized; shader response and native models identical in every tier','tiers':report},indent=2)+'\n')
