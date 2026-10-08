import os
from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
from collections import deque
D=Path(os.environ['PHOENIX_WORKSPACE']);W=D/'work/audit_v5';R=D/'review/audit_v5'
W.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
rgb=np.array(Image.open(D/'maps/phoenix_worn_basecolor_generated_v1.png').convert('RGB')).astype(int)
boxes=[('roof_front',(545,591,706,633)),('roof_mid_front',(724,583,911,641)),('roof_mid_aft',(918,585,1061,644)),('roof_aft',(1070,570,1248,654)),('side_front',(564,682,732,751)),('side_middle',(732,656,913,723)),('side_aft',(918,647,1062,695))]
def hull(points):
 p=sorted(set(points));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);lo=[];hi=[]
 for q in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>=2 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return lo[:-1]+hi[:-1]
result=[];im=Image.fromarray(rgb.astype('uint8'));draw=ImageDraw.Draw(im)
for name,box in boxes:
 x0,y0,x1,y1=box;a=rgb[y0:y1,x0:x1];r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];mask=(g-r>=3)&(b-r>=1)&(g>=17)&(g<=130)&(r<=80)
 seen=np.zeros(mask.shape,bool);components=[]
 for y,x in zip(*np.where(mask)):
  if seen[y,x]:continue
  q=deque([(int(y),int(x))]);seen[y,x]=1;pts=[]
  while q:
   j,i=q.popleft();pts.append((i+x0,j+y0))
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     yy,xx=j+dy,i+dx
     if 0<=yy<mask.shape[0] and 0<=xx<mask.shape[1] and mask[yy,xx] and not seen[yy,xx]:seen[yy,xx]=1;q.append((yy,xx))
  components.append(pts)
 pts=max(components,key=len)
 # Exclude narrow vertical paint/reflection streaks which project beyond the
 # actual straight upper inside edge of the two central roof frames.
 if name=='roof_mid_front':pts=[(x,y) for x,y in pts if y>=594-(x-738)*3/159-.35]
 if name=='roof_mid_aft':pts=[(x,y) for x,y in pts if y>=594-(x-931)*2/116-.35]
 outline=hull(pts);result.append({'name':name,'original_colour_region_pixels':len(pts),'glass_outline':outline,'box':box})
 draw.line(outline+[outline[0]],fill=(255,50,180),width=1)
(W/'original_glass_outlines.json').write_text(json.dumps(result,indent=2)+'\n');im.crop((530,570,1254,755)).resize((1448,370)).save(R/'original_outline_diagnostic.png')
print('TRACED',len(result),'original pane outlines')
