from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
D=Path('${RELIANT_WORKSPACE}');M=D/'maps/refinement_v2';W=D/'work/refinement_v2';N=2048
r=json.loads((W/'material_regions.json').read_text());fins=next(q for q in r['materials'][2]['ribs'] if q['box']==[224,202,245,227])['centres']
y,x=np.mgrid[:N,:N].astype('float32');X=(x+.5)*256/N;Y=(y+.5)*256/N
# The final radiator bank was absent from the first-pass semantic list.
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
m=smooth(0,.4,np.minimum.reduce([X-224,245-X,Y-230,254-Y]));bar=np.zeros_like(m)
for c in fins:bar=np.maximum(bar,1-smooth(.16,.85,abs(X-c)))
h=np.load(M/'orr3_hull_height.npy');h=h*(1-m)+(-3.4+4.1*bar)*m;np.save(M/'orr3_hull_height.npy',h)
dy,dx=np.gradient(h,256/N);nx=-dx*.85;ny=dy*.85;q=np.maximum(1,np.hypot(nx,ny)/2.65);n=np.stack([nx/q,ny/q,np.ones_like(h)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
im=Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255+.5)).resize((4096,4096),Image.Resampling.LANCZOS);n=np.asarray(im).astype('float32')/127.5-1;n/=np.linalg.norm(n,axis=-1,keepdims=True);Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255+.5)).save(M/'orr3_hull_normal.png')
Image.fromarray(np.uint8(np.clip((h+8)/16,0,1)*255+.5)).resize((4096,4096),Image.Resampling.LANCZOS).save(M/'orr3_hull_height.png')
# Same cavity occlusion as the upper two banks.
orm=np.asarray(Image.open(M/'orr3_hull_orm.png').resize((N,N))).astype('float32')/255;orm[:,:,0]=orm[:,:,0]*(1-m)+(1-.28*(1-bar))*m
Image.fromarray(np.uint8(np.clip(orm,0,1)*255+.5)).resize((4096,4096),Image.Resampling.LANCZOS).save(M/'orr3_hull_orm.png')
r['third_radiator_bank']={'box':[224,230,245,254],'centres':fins};r['analytic_bridge_bevels']=True;(W/'material_regions.json').write_text(json.dumps(r,indent=2)+'\n')
for suffix in ['_normal','_orm']:shutil.copy2(M/('orr3_hull'+suffix+'.png'),D/'exports/openreliant_0_18_v1/mods/119-reliant-worn-v1'/('orr3_hull'+suffix+'.png'))
print('Third radiator bank completed')
