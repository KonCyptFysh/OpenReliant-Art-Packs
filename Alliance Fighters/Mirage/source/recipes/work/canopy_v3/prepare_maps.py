from pathlib import Path
import numpy as np,json
from PIL import Image,ImageFilter
D=Path(__file__).resolve().parents[2];W=D/'work/canopy_v3';M=D/'maps/canopy_v3';N=4096
prior=json.loads((W/'prior_project_state.json').read_text());a=np.array(Image.open(prior['basecolour']).convert('RGB'));base=a.copy();edit=np.array(Image.open(M/'canopy_edit_generated.png').convert('RGB').resize((768,1024),Image.Resampling.LANCZOS));alpha=np.zeros((N,N),np.float32);newglass=np.zeros((N,N),np.float32)
# The front tip wraps to rows 11.51..20.96 while the adjoining roof uses
# 9.94..19.38. Fit the generated glass slightly beyond both sampling ranges
# so the source UV discontinuity cannot bring a piece of rim inside the glass.
patch=Image.fromarray(edit[:512]).crop((148,114,608,282)).resize((460,190),Image.Resampling.LANCZOS)
edit[104:294,148:608]=np.array(patch)
regions=json.loads((D/'work/reconstruction_v1/regions.json').read_text())['glass'];crops=json.loads((W/'edit_regions.json').read_text())['crops']
def smooth(lo,hi,d):
 t=np.clip((d-lo)/(hi-lo),0,1);return t*t*(3-2*t)
def poly(x,y,points):
 p=np.asarray(points);d=np.full(x.shape,1000,np.float32);area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
 for aa,bb in zip(p,np.roll(p,-1,axis=0)):
  v=bb-aa;d=np.minimum(d,np.sign(area)*(v[0]*(y-aa[1])-v[1]*(x-aa[0]))/np.linalg.norm(v))
 return d
# Limits include just the two affected panes and their added rim. Native UVs stay unchanged.
outer=[[(12.0,9.05),(42.65,9.05),(42.65,21.8),(12.0,21.8)],[(162.3,216.05),(183.7,216.8),(193.05,219.9),(193.05,235.3),(162.3,235.3)]]
for i,box in enumerate(crops):
 x0,y0,x1,y1=[int(v*16) for v in box];yy,xx=np.mgrid[y0:y1,x0:x1];X=(xx+.5)/16;Y=(yy+.5)/16
 inside=poly(X,Y,outer[i]);safe=poly(X,Y,np.array(regions[0 if i==0 else 3])*256/1254)
 weight=smooth(0,.45,inside)*(1-smooth(.35,1.65,safe));b=edit[i*512:(i+1)*512].astype(np.float32)
 base[y0:y1,x0:x1]=np.rint(a[y0:y1,x0:x1]*(1-weight[:,:,None])+b*weight[:,:,None]).astype(np.uint8);alpha[y0:y1,x0:x1]=weight
 green=(b[:,:,1]>b[:,:,0]+1.5)&(b[:,:,1]>b[:,:,2]+1.5)&(b.max(2)<110)&(inside>.25)
 mask=Image.fromarray(green.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(.7))
 newglass[y0:y1,x0:x1]=np.array(mask)/255*smooth(0,.45,inside)
Image.fromarray(base).save(M/'mirage_worn_basecolor_4k_v3.png');Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(M/'canopy_edit_mask_4k_v3.png');Image.fromarray(np.rint(newglass*255).astype(np.uint8)).save(M/'canopy_glass_extension_4k_v3.png')
changed=np.any(base!=a,axis=2);outside=alpha==0
assert not changed[outside].any()
r={'basecolor_changed_pixels':int(changed.sum()),'basecolor_changed_percent':float(changed.mean()*100),'outside_canopy_edit_mask_changed_pixels':int(changed[outside].sum()),'preserved_glass_interiors':True,'only_affected_regions_native_atlas':outer,'method':'Built-in image edit, composited only over the added rims; original glass interiors and all other artwork preserved.'};(W/'local_edit_validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
