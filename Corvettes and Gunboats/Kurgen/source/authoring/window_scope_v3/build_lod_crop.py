from pathlib import Path
import bpy,json,hashlib,numpy as np
D=Path('${KURGEN_WORKSPACE}');W=D/'work/window_scope_v3';M=D/'maps/window_scope_v3';crop=[96,128,112,192];width=256;height=1024
parts=json.loads((D/'source/native_parts.json').read_text());l=parts[0]['lods'][1];f=l['faces'][66];uv=np.array(f['uv']);uv[:,1]=1-uv[:,1];uv*=256;xyz=np.array(l['vertices'])[f['vertices']]+parts[0]['origin']
yy,xx=np.mgrid[:height,:width];xy=np.stack(((xx+.5)/16+crop[0],(yy+.5)/16+crop[1]),axis=-1);ab=(xy-uv[0])@np.linalg.inv((uv[1:]-uv[0]).T).T;z=xyz[0,2]+ab@(xyz[1:,2]-xyz[0,2])
# Coarse triangles originally stretch the bridge's side atlas onto the rear platform.
# Retain new glass only within the physical span of the original marked bridge.
t=np.clip((z+2325)/25,0,1);keep=t*t*(3-2*t)
def load(p):
 im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name='Non-Color';a=np.empty(4096*4096*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(4096,4096,4)[::-1,:,:3][crop[1]*16:crop[3]*16,crop[0]*16:crop[2]*16].copy();bpy.data.images.remove(im);return a
maps={}
for key in ['basecolor','normal','roughness','metallic','emissive']:
 new=load(M/('kurgen_hull_'+key+'_v3.png'))
 if key=='emissive':old=np.zeros_like(new)
 else:old=load(D/'maps'/('kurgen_hull_'+key+'_v1.png'))
 if key=='normal':
  v=old*2-1;v[:,:,:2]*=2.8;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);old=v*.5+.5
 a=new*keep[:,:,None]+old*(1-keep[:,:,None])
 if key=='normal':
  v=a*2-1;v/=np.maximum(np.linalg.norm(v,axis=-1,keepdims=True),1e-8);a=v*.5+.5
 im=bpy.data.images.new('bridge distant '+key,width,height,alpha=False);im.colorspace_settings.name='Non-Color';q=np.ones((height,width,4),np.float32);q[:,:,:3]=a;im.pixels.foreach_set(np.ascontiguousarray(q[::-1]).ravel());p=M/('kurgen_bridge_lod_'+key+'_v3.png');im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);maps[key]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),dimensions=[width,height])
v=json.loads((W/'validation.json').read_text());v['bridge_lod_maps']=maps;v['bridge_lod_selection']=dict(atlas_crop=crop,selected_faces_by_lod=[[],[66,202],[33,113],[],[],[]],purpose='Restrict lower-detail side windows to the highlighted bridge span; restore original unlit hardware beyond it');(W/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('LOD_WINDOW_CROP_SAVED')
