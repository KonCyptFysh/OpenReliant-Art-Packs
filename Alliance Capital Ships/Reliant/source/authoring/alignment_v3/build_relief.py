"""Revision 3: current-artwork-aligned geometric relief, in 1024-pixel atlas coordinates.
Base/emission remain byte-identical. Analytic bevels; no guessed periodic rib grids,
no texture-brightness-to-height conversion or height on paint chips. All paths retained.
"""
from pathlib import Path
import numpy as np,json,shutil
from PIL import Image,ImageDraw
D=Path('${RELIANT_WORKSPACE}');W=D/'work/alignment_v3';OLD=D/'maps/refinement_v2';M=D/'maps/alignment_v3';M.mkdir(exist_ok=True);N=2048;K=N/1024
for p in OLD.iterdir():
 if not (M/p.name).exists():shutil.copy2(p,M/p.name)
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
class Relief:
 def __init__(self,i):
  self.i=i;self.stem=f'orr{i}_hull' if isinstance(i,int) else i;self.h=np.zeros((N,N),np.float32);self.records=[];self.base=Image.open(OLD/f'{self.stem}.png').convert('RGB').resize((1024,1024));self.overlay=self.base.copy();self.draw=ImageDraw.Draw(self.overlay)
 def apply(self,bounds,fn):
  x0,y0,x1,y1=bounds;x0=max(0,int(np.floor(x0*K)));y0=max(0,int(np.floor(y0*K)));x1=min(N,int(np.ceil(x1*K)));y1=min(N,int(np.ceil(y1*K)))
  if x0>=x1 or y0>=y1:return
  y,x=np.mgrid[y0:y1,x0:x1].astype('float32');x=(x+.5)/K;y=(y+.5)/K
  self.h[y0:y1,x0:x1]=fn(x,y,self.h[y0:y1,x0:x1])
 def polygon(self,pts,depth=-12,bevel=3):
  self.records.append(dict(kind='pocket',points=pts,depth=depth,bevel=bevel));self.draw.line(pts+[pts[0]],fill=(255,90,60),width=1)
  pts=np.array(pts);lo=pts.min(0);hi=pts.max(0)
  def op(x,y,h):
   inside=np.zeros(x.shape,bool);dist=np.full(x.shape,1e6,np.float32)
   for j,(u,v) in enumerate(pts):
    w,z=pts[(j+1)%len(pts)];vx,vy=w-u,z-v;t=np.clip(((x-u)*vx+(y-v)*vy)/max(vx*vx+vy*vy,1e-6),0,1);dist=np.minimum(dist,np.hypot(x-u-t*vx,y-v-t*vy))
    if z!=v:inside^=((v>y)!=(z>y))&(x<(w-u)*(y-v)/(z-v)+u)
   return np.where(inside,depth*smooth(0,bevel,dist),h)
  self.apply((*lo,*hi),op)
 def line(self,a,b,width=3,depth=-4,style='groove'):
  self.records.append(dict(kind=style,a=a,b=b,width=width,depth=depth));self.draw.line([a,b],fill=(55,220,240),width=1)
  vx,vy=np.subtract(b,a);r=width/2
  def op(x,y,h):
   t=np.clip(((x-a[0])*vx+(y-a[1])*vy)/max(vx*vx+vy*vy,1e-6),0,1);d=np.hypot(x-a[0]-t*vx,y-a[1]-t*vy)
   m=1-smooth(r*.10,r,d)
   return h+depth*m*(h<-.01) if style=='pipe' else h+depth*m
  self.apply((min(a[0],b[0])-r-1,min(a[1],b[1])-r-1,max(a[0],b[0])+r+1,max(a[1],b[1])+r+1),op)
 def rect(self,bb,depth=-7,bevel=2):
  a,b,c,d=bb;self.polygon([(a,b),(c,b),(c,d),(a,d)],depth,bevel)
 def ribbed(self,bb,axis,centres,halfwidth=1.65,depth=-10,rise=12):
  a,b,c,d=bb
  # Snap each finite rib to the actual painted profile; catches accumulated pitch
  # drift in the tall bridge radiator while keeping regions/topology explicit.
  roi=np.asarray(self.base)[int(b):int(d),int(a):int(c)].mean(-1)
  profile=roi.mean(0 if axis=='x' else 1);profile=np.convolve(np.pad(profile,2,mode='edge'),[.06,.24,.4,.24,.06],'valid')
  origin=a if axis=='x' else b;measured=[]
  for q in centres:
   idx=int(q-origin);lo=max(1,idx-3);hi=min(len(profile)-1,idx+4)
   measured.append(float(np.argmax(profile[lo:hi])+lo+.5+origin) if hi>lo else q)
  centres=sorted(set(measured))
  self.records.append(dict(kind='ribs',box=bb,axis=axis,centres=centres))
  self.draw.rectangle(bb,outline=(255,90,60))
  for q in centres:self.draw.line([(q,b),(q,d)] if axis=='x' else [(a,q),(c,q)],fill=(55,220,240))
  def op(x,y,h):
   edge=np.minimum.reduce([x-a,c-x,y-b,d-y]);mask=smooth(0,2,edge);p=x if axis=='x' else y;rib=np.zeros_like(x)
   for q in centres:rib=np.maximum(rib,1-smooth(halfwidth*.15,halfwidth,np.abs(p-q)))
   if bb[0]==30:
    # Match the chamfered bank: preserve a flat frame outside the traced polygon.
    mask*=h<-.01
   return h*(1-mask)+(depth+rise*rib)*mask
  self.apply(bb,op)
 def slot(self,a,b,r,depth=-12):
  self.records.append(dict(kind='slot',a=a,b=b,radius=r));vx,vy=np.subtract(b,a)
  self.draw.line([a,b],fill=(255,190,0),width=1)
  def op(x,y,h):
   t=np.clip(((x-a[0])*vx+(y-a[1])*vy)/max(vx*vx+vy*vy,1e-6),0,1);dist=r-np.hypot(x-a[0]-t*vx,y-a[1]-t*vy);m=smooth(0,2.5,dist);return h*(1-m)+depth*m
  self.apply((min(a[0],b[0])-r,min(a[1],b[1])-r,max(a[0],b[0])+r,max(a[1],b[1])+r),op)
 def save(self):
  h=self.h;np.save(M/f'{self.stem}_height.npy',h/4)
  dy,dx=np.gradient(h,1/K);nx=-dx*.85;ny=dy*.85;slope=np.maximum(1,np.hypot(nx,ny)/2.4);n=np.stack([nx/slope,ny/slope,np.ones_like(h)],-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
  def png(a,suffix):Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).resize((4096,4096),Image.Resampling.LANCZOS).save(M/f'{self.stem}{suffix}.png')
  png(n*.5+.5,'_normal');p=M/f'{self.stem}_normal.png';v=np.asarray(Image.open(p)).astype('float32')/127.5-1;v/=np.linalg.norm(v,axis=-1,keepdims=True);Image.fromarray(np.uint8(np.clip(v*.5+.5,0,1)*255+.5)).save(p)
  png((h/4+8)/16,'_height')
  orm=np.asarray(Image.open(OLD/f'{self.stem}_orm.png').resize((N,N))).astype('float32')/255;orm[:,:,0]=1-.18*smooth(0,12,-h);png(orm,'_orm')
  self.overlay.save(W/f'aligned-overlay-{self.i}.png');(W/f'geometry-{self.i}.json').write_text(json.dumps(self.records,indent=2)+'\n')
  print('RELIEF',self.i,len(self.records),'features',flush=True)
# Hull 1: panel frames and mechanical channels, separated at markings and atlas islands.
a=Relief(1)
for x0,y0,x1,y1 in [(5,241,370,241),(5,325,370,325),(5,418,370,418),(5,766,415,766),(5,831,415,831),(5,851,415,851),(5,937,415,937),(5,954,415,954),(5,976,415,976),(5,1020,415,1020),(5,324,5,418),(121,327,121,410),(372,0,372,763),(460,110,460,613),(397,113,397,219),(441,113,441,219),(372,223,460,223),(372,427,460,427),(372,545,440,545),(372,618,440,618),(636,234,636,762),(716,215,716,719),(638,269,709,269),(638,318,709,318),(638,370,709,370),(638,420,709,420),(638,447,709,447),(483,271,621,271),(483,587,621,587),(483,271,483,587),(621,271,621,587),(492,338,617,338),(492,435,617,435),(492,521,617,521),(530,282,530,419),(533,435,533,518),(577,282,577,418),(577,435,577,518),(437,770,437,1019),(590,770,590,1019),(877,770,877,1019),(997,770,997,1019),(437,820,997,820),(437,974,997,974),(194,769,194,829),(216,854,216,933),(6,855,6,934),(6,976,6,1019),(87,977,87,1018)]:a.line((x0,y0),(x1,y1),3,-4)
# The two broad pipe runs are raised metal, rather than empty slots.
for y in [122,196]:
 a.slot((60,y),(313,y),17,-9);a.line((61,y),(312,y),12,15,'pipe')
a.slot((60,588),(313,588),21,-12)
for y in [575,588,601]:a.line((60,y),(313,y),4,12,'rib')
a.ribbed([496,18,913,103],'y',[23,39,55,71,87,101],2.2,-10,12)
# Tall bridge radiator: eight NON-periodic braces over seven thin vertical fins.
brace_y=[245.5,273.5,321.5,345.5,369.5,418.5,442.5,466.5]
fin_x=[739.5,743.5,746.5,750.5,753.5,757.5,760.5]
def bridge_radiator(x,y,h):
 edge=np.minimum.reduce([x-735.2,763.3-x,y-215.5,504-y]);m=smooth(0,1.2,edge)
 fins=np.zeros_like(x)
 for q in fin_x:fins=np.maximum(fins,1-smooth(.12,.85,abs(x-q)))
 field=-11+10*fins
 braces=np.zeros_like(x)
 for q in brace_y:braces=np.maximum(braces,1-smooth(.7,2,abs(y-q)))
 field=field*(1-braces)+2.5*braces
 out=h*(1-m)+field*m
 # The crossbar ends meet the mounting rails; they do not cross the plate border.
 rail_span=smooth(730,732,x)*(1-smooth(764.5,766,x))
 return out*(1-braces*rail_span)+2.5*braces*rail_span
a.apply((729,214,768,505),bridge_radiator)
a.records.append(dict(kind='bridge_radiator',bounds=[735.2,215.5,763.3,504],brace_centres=brace_y,fin_centres=fin_x))
for q in brace_y:a.draw.line([(730,q),(766,q)],fill=(255,90,60))
for q in fin_x:a.draw.line([(q,216),(q,504)],fill=(55,220,240))
a.ribbed([515,112,616,159],'x',[525,542,559,576,593,610],2.2,-9,12)
a.ribbed([169,249,196,312],'y',list(range(253,312,6)),1.2,-7,8)
# Engine disk: measured hub and individual radial vanes from the current atlas.
# A solid domed hub, recessed annulus, outer retaining rim and separate ribs.
def disk(x,y,h):
 cx,cy=426.8,58.2;rho=np.hypot(x-cx,y-cy);dist=55-rho;m=smooth(0,2.0,dist)
 ring=6*(1-smooth(1,3,abs(rho-51)))
 hub=23*np.sqrt(np.clip(1-(rho/15.5)**2,0,1))* (1-smooth(14,15.5,rho))
 hubrim=9*(1-smooth(.7,2.2,abs(rho-17.3)))
 ribs=np.zeros_like(rho)
 # Each angle is measured from the visible painted rib; no generic 12-spoke phase.
 for ex,ey in [(487,57),(477,25),(460,6),(428,2),(399,8),(379,30),(377,72),(383,92),(405,106),(430,109),(457,99),(476,85)]:
  theta=np.arctan2(ey-cy,ex-cx);ang=np.arctan2(y-cy,x-cx);delta=np.arctan2(np.sin(ang-theta),np.cos(ang-theta));v=np.abs(np.sin(delta)*rho)
  rib=(1-smooth(.65,2.4,v))*(np.cos(delta)>0)*smooth(19,23,rho)*(1-smooth(49,53,rho));ribs=np.maximum(ribs,rib)
 field=-15+ring+hub+hubrim+17*ribs
 return h*(1-m)+field*m
a.apply((371,0,493,115),disk);a.records.append(dict(kind='engine_disk',center=[426.8,58.2],depth=15,hub_height=23,radial_vanes=12));a.save()
# REL2: inner edges retraced from the finished artwork. Former approximate polygons removed.
a=Relief(2)
polys=[[(11,41),(25,27),(53,27),(65,40),(65,54),(27,91),(19,91),(11,83)],[(12,128),(76,65),(86,65),(105,84),(105,216),(94,228),(84,228),(12,156)],[(12,254),(30,235),(42,235),(105,298),(105,357),(30,415),(20,415),(12,407)],[(12,470),(75,407),(88,407),(105,424),(105,489),(87,507),(26,507),(12,494)],[(11,544),(25,530),(53,530),(65,543),(65,554),(27,592),(19,592),(11,584)],[(12,631),(76,567),(86,567),(105,586),(105,719),(94,730),(84,730),(12,658)],[(12,755),(30,737),(42,737),(105,801),(105,860),(30,917),(20,917),(12,909)],[(12,972),(75,910),(88,910),(105,927),(105,992),(87,1010),(26,1010),(12,997)],[(193,157),(206,144),(244,144),(273,171),(273,226),(265,234),(256,234),(193,174)],[(193,213),(208,197),(215,197),(239,221),(239,242),(224,255),(200,255),(193,246)],[(300,157),(313,144),(350,144),(378,171),(378,226),(370,234),(361,234),(300,174)],[(300,213),(314,198),(321,198),(346,222),(346,243),(333,255),(309,255),(300,247)],[(470,101),(483,89),(550,89),(576,113),(576,123),(557,141),(482,141),(470,128)],[(594,100),(603,89),(704,89),(718,103),(718,112),(691,141),(634,141)],[(775,89),(801,89),(817,105),(817,124),(801,142),(731,142),(731,130)],[(469,179),(482,167),(550,167),(577,190),(577,199),(559,216),(481,216),(469,204)],[(592,178),(604,166),(706,166),(719,178),(719,185),(706,192),(687,215),(632,215)],[(434,634),(469,603),(647,603),(662,619),(662,630),(599,695),(450,695),(434,677)],[(657,664),(719,603),(773,603),(818,650),(818,671),(795,695),(671,695),(657,680)],[(820,617),(854,603),(987,603),(1011,628),(1011,659),(975,695),(891,695),(820,627)]]
for p in polys:a.polygon(p,-13,2.8)
# Actual exposed pipe runs within the three machinery pockets. Keep their joints/rims separate.
for a0,b0,c0,d0,w in [(438,638,660,638,7),(674,638,814,638,7),(836,638,1009,638,7),(437,675,508,675,5),(550,675,620,675,5),(661,675,710,675,5),(730,675,771,675,5),(936,675,991,675,5),(465,644,465,685,8),(523,647,523,681,5),(577,644,577,694,9),(550,611,550,636,5),(576,609,576,636,6),(623,613,623,636,5),(727,644,727,694,9),(785,647,785,693,8),(724,607,724,636,6),(754,607,754,636,5),(873,644,873,683,6),(901,644,901,682,8),(936,646,936,678,6),(887,611,887,636,5)]:a.line((a0,b0),(c0,d0),w,15,'pipe')
for x0,y0,x1,y1 in [(110,21,110,515),(110,524,110,1020),(179,0,179,1024),(204,282,204,1024),(257,282,257,1024),(406,0,406,1024),(419,229,1018,229),(419,272,1018,272),(419,315,590,315),(419,448,590,448),(419,476,1018,476),(419,509,1018,509),(419,594,1018,594),(419,712,1018,712),(419,792,1018,792),(419,819,1018,819),(419,961,1018,961),(419,1018,1018,1018),(495,232,495,441),(590,232,590,476),(590,712,590,1018),(687,318,687,443),(789,274,789,474),(834,91,834,227),(942,89,942,269),(835,374,835,461),(978,374,978,462),(266,569,398,569),(266,628,398,628),(266,677,398,677),(266,708,398,708),(266,781,398,781),(266,825,398,825),(266,879,398,879),(266,966,398,966),(266,1013,398,1013),(303,712,303,958),(344,712,344,958),(665,823,665,955),(819,823,819,955)]:a.line((x0,y0),(x1,y1),2.5,-3.5)
# Windows: retain the already aligned shared glass/emission bounds, with no extra
# offset ring cut into the surrounding beam. A single recessed bevel is sufficient.
windows=json.loads((D/'work/refinement_v2/material_regions.json').read_text())['windows']
for bb in windows:
 x0,y0,x1,y1=np.array(bb)*4
 def win(x,y,h):
  dist=np.minimum.reduce([x-x0,x1-x,y-y0,y1-y]);m=smooth(-1.3,.7,dist);return h*(1-m)-19*m
 a.apply((x0-2,y0-2,x1+2,y1+2),win)
a.save()
# REL3 panels: no full-atlas guide lines crossing separate pieces.
a=Relief(3)
for x0,y0,x1,y1 in [(348,0,348,1024),(211,229,211,1024),(402,269,402,574),(627,269,627,574),(737,0,737,1024),(744,239,1018,239),(744,607,1018,607),(744,645,1018,645),(744,684,1018,684),(787,0,787,239),(850,0,850,239),(918,0,918,239),(988,0,988,239),(813,245,813,601),(919,245,919,601),(217,186,347,186),(217,228,347,228),(217,278,347,278),(217,365,347,365),(217,391,347,391),(217,441,347,441),(246,481,347,481),(246,516,347,516),(217,580,347,580),(217,627,347,627),(217,676,347,676),(217,749,347,749),(217,763,347,763),(217,885,347,885),(217,955,347,955),(217,1017,347,1017),(264,280,264,362),(287,280,287,362),(266,521,266,574),(17,243,191,243),(17,278,191,278),(17,336,191,336),(17,374,191,374),(61,379,61,514),(61,432,210,432),(61,493,210,493),(435,615,575,615),(435,641,575,641),(435,695,575,695),(435,741,575,741),(482,709,482,760),(523,709,523,749),(568,709,568,734),(382,165,691,165),(382,261,691,261),(454,454,583,454),(454,477,583,477),(348,574,650,574)]:a.line((x0,y0),(x1,y1),3,-4)
# Large front radiator cutouts are chamfered, and their ribs follow the exact painted peaks.
# Every bank is measured separately: no guessed pitch or shared phase.
a.polygon([(38,523),(177,523),(193,539),(193,726),(177,743),(38,743),(27,729),(27,539)],-10,3)
a.polygon([(38,767),(177,767),(193,782),(193,973),(177,989),(38,989),(27,975),(27,782)],-10,3)
# Structural rib centres measured from the 4k base profile inside each bounded bank.
for bb,axis,spacing in [([30,526,191,741],'x',15),([30,770,191,987],'x',15),([894,693,980,796],'x',15),([894,805,980,908],'x',15),([894,919,980,1017],'x',15),([655,273,703,566],'x',16),([358,502,397,565],'y',5.4),([564,502,603,565],'y',5.4),([215,450,235,574],'y',5.2),([215,582,235,668],'y',5.2),([215,684,235,743],'y',5.2),([215,958,235,1015],'y',5.2)]:
 l,t,r,b=map(int,bb);roi=np.asarray(a.base)[t:b,l:r].mean(-1);prof=roi.mean(0 if axis=='x' else 1);prof=np.convolve(np.pad(prof,2,mode='edge'),[.06,.24,.4,.24,.06],'valid');cand=np.where((prof[1:-1]>prof[:-2])&(prof[1:-1]>=prof[2:]))[0]+1;peaks=[]
 for v in sorted(cand,key=lambda p:-prof[p]):
  if all(abs(v-q)>spacing*.65 for q in peaks):peaks.append(int(v))
 coords=[p+.5+(l if axis=='x' else t) for p in sorted(peaks)];a.ribbed(bb,axis,coords,halfwidth=2.1 if spacing>10 else 1.1,depth=-11,rise=14)
for y in [133,220]:
 a.slot((397,y),(678,y),19,-12)
 for d in [-7,7]:a.line((397,y+d),(679,y+d),4.5,12,'rib')
for y in [332,377,424,471,517,564]:a.slot((941,y),(968,y),8.5,-12)
for x in [438,520]:
 a.slot((x,510),(x,541),9,-12);a.line((x,507),(x,544),4,10,'rib')
a.save()
# Shared underside capital turret: its original approximate rib phase also drifted.
a=Relief('orr_cgun')
a.rect([636,148,906,490],-7,3)
for x,y0,y1,w in [(670,158,485,9),(709,185,486,10),(763,185,486,9),(848,185,485,10)]:a.line((x,y0),(x,y1),w,14,'pipe')
for y in [369,402,433,465]:a.line((636,y),(905,y),14,14,'pipe')
a.slot((550,44),(698,44),17,-7);a.line((550,44),(698,44),13,16,'pipe')
for bb,axis,spacing in [([25,58,180,170],'y',26),([203,58,358,170],'y',26),([409,466,498,610],'y',10),([663,556,864,771],'x',20),([663,787,831,1015],'x',33),([121,918,647,980],'x',16)]:
 l,t,r,b=map(int,bb);roi=np.asarray(a.base)[t:b,l:r].mean(-1);prof=roi.mean(0 if axis=='x' else 1);prof=np.convolve(np.pad(prof,2,mode='edge'),[.06,.24,.4,.24,.06],'valid');cand=np.where((prof[1:-1]>prof[:-2])&(prof[1:-1]>=prof[2:]))[0]+1;peaks=[]
 for v in sorted(cand,key=lambda p:-prof[p]):
  if all(abs(v-q)>spacing*.65 for q in peaks):peaks.append(int(v))
 coords=[p+.5+(l if axis=='x' else t) for p in sorted(peaks)];a.ribbed(bb,axis,coords,halfwidth=2.5 if spacing>14 else 1.5,depth=-12,rise=16)
for y in [489,534,580]:
 for x in [174,224,274,323]:
  def port(xx,yy,h):
   d=16-np.hypot(xx-x,yy-y);m=smooth(0,3,d);return h*(1-m)-14*m
  a.apply((x-18,y-18,x+18,y+18),port)
for x0,y0,x1,y1 in [(67,263,67,525),(67,263,299,263),(299,263,333,296),(333,296,333,439),(67,376,203,376),(203,270,203,437),(71,439,471,439),(118,624,649,624),(118,856,649,856),(118,906,649,906),(278,632,278,851),(457,632,457,851),(603,632,603,851),(650,552,650,1019),(868,552,868,1019)]:a.line((x0,y0),(x1,y1),3,-4)
a.save()
print('ALIGNED_RELIEF_READY')
