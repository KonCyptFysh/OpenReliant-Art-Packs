"""Patriot v2: local material repairs on the latest scene; immutable geometry/legacy UVs.
A second atlas gives the corrected wrap surfaces real area. All base colours reuse
existing artwork; glass is a masked selection from the built-in edited reference.
"""
import bpy,numpy as np,math,json,hashlib
from pathlib import Path
D=Path('local-only://worn');W=D/'work/refinement_v2';M=D/'maps/refinement_v2';N=4096
state=json.loads((W/'prior_project_state.json').read_text());src=Path(state['latest_scene']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();srcsha=sha(src)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];oldname='Patriot_Delivery_UV_v1';newname='Patriot_Delivery_UV_v2';before={}
for o in obs:
 m=o.data;before[o.name]={'v':[list(v.co) for v in m.vertices],'f':[list(p.vertices) for p in m.polygons],'n':[list(q.vector) for q in m.corner_normals],'uv':{u.name:[list(q.uv) for q in u.data] for u in m.uv_layers},'m':[p.material_index for p in m.polygons]}
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def load(path,scale=None):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='Non-Color'
 if scale:im.scale(scale,scale)
 w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);return a.reshape(h,w,4)[::-1,:,:3].copy()
def save(a,key):
 h,w=a.shape[:2];buf=np.ones((h,w,4),np.float32);buf[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new(key,w,h,alpha=False,float_buffer=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(buf[::-1]).ravel());p=M/(key+'.png');im.filepath_raw=str(p);im.file_format='PNG';s.render.image_settings.color_depth='8' if 'basecolor' in key else '16';im.save();bpy.data.images.remove(im);return {'path':str(p),'sha256':sha(p)}
def sample(im,q):
 h,w=im.shape[:2];x=(q[:,0]%1)*w-.5;y=(1-q[:,1]%1)*h-.5;x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[:,None];fy=(y-y0)[:,None];return (im[y0%h,x0%w]*(1-fx)+im[y0%h,(x0+1)%w]*fx)*(1-fy)+(im[(y0+1)%h,x0%w]*(1-fx)+im[(y0+1)%h,(x0+1)%w]*fx)*fy
main={k:load(state['maps'][k]['path']) for k in ['basecolor','normal','roughness','metallic']};glass=load(state['maps']['glass']['path'])[:,:,0];edited=load(M/'glass_edit_reference.png',N)
# Replace only the pane interiors; the rest of the accepted main atlas stays identical.
editmask=glass.copy()
for _ in range(12):editmask=np.maximum.reduce([editmask,np.roll(editmask,1,0),np.roll(editmask,-1,0),np.roll(editmask,1,1),np.roll(editmask,-1,1)])
main['basecolor']=main['basecolor']*(1-editmask[:,:,None])+edited*editmask[:,:,None];main['roughness']=main['roughness']*(1-glass[:,:,None])+.115*glass[:,:,None];main['metallic']*=1-glass[:,:,None];main['normal']=main['normal']*(1-glass[:,:,None])+np.array([.5,.5,1])*glass[:,:,None]
mainrecords={k:save(a,'patriot_main_'+k+'_4k_v2') for k,a in main.items()} if '--reuse-main' not in __import__('sys').argv else json.loads((W/'validation.json').read_text())['main_maps'];assert all(sha(r['path'])==r['sha256'] for r in mainrecords.values());del edited
# Source-matched clean swatches, with mirrored addressing to avoid tile jumps.
coarse=load(state['maps']['basecolor']['path'],1254)
swatches={'bronze':coarse[352:405,182:255].copy(),'steel':coarse[555:629,944:1007].copy(),'green':coarse[195:237,918:985].copy()}
reference=load(M/'repair_wear_reference.png');mid=reference.shape[1]//2;refbrown=reference[:,:mid];refsteel=reference[:,mid:];targets={k:np.median(v.reshape(-1,3),axis=0) for k,v in swatches.items()};swatches={k:(refsteel if k=='steel' else refbrown).copy() for k in targets}
for k in swatches:swatches[k]*=targets[k]/np.median(swatches[k].reshape(-1,3),axis=0)
neutral=refbrown.mean(-1);swatches['green']=neutral[:,:,None]/np.median(neutral)*targets['green']
def triplanar(pos,norm,kind,scale=1.18):
 p=pos/scale+np.array([.08,.29,.17]);weights=np.abs(norm)**4;weights/=np.maximum(weights.sum(1)[:,None],1e-9);out=np.zeros_like(p)
 for ax,(a,b) in enumerate([(1,2),(0,2),(0,1)]):
  q=np.column_stack((p[:,a],p[:,b]));q=1-np.abs(q%2-1);out+=sample(swatches[kind],q)*weights[:,ax,None]
 return out
# Selected surface groups are paired explicitly; no topology changes or hidden caps.
groups={
 'Patriot_Cockpit':{'nose':[0,1,8,15,*range(18,28),34,35,46,47],'pod':list(range(48,54))},
 'Patriot_Body':{'arm_fins':[35,36,53,54,91,92,293,294,311,312,349,350],
 'joint':[45,46,47,48,77,303,304,305,306,335],
 'radiator':[10,11,268,269],
 'long_vent':[*range(18,25),108,109,*range(276,283),366,367],
 'engine':[0,1,*range(138,142),*range(158,166),186,187,*range(215,235),*range(240,252)],
 'rear':[188,189,208,209,210,211,212,213,214,252,253,259],
 'muzzle':list(range(368,376))}}
selected={name:{i:k for k,ids in gs.items() for i in ids} for name,gs in groups.items()};frames_old={};frames_new={};positions={};normrot={}
def frames(o,uvname):
 m=o.data;m.calc_tangents(uvmap=uvname);rot=np.array(o.matrix_world.to_3x3());nr=np.array(o.matrix_world.to_3x3().inverted().transposed());ret={}
 for p in m.polygons:
  ts=np.array([list(m.loops[i].tangent) for i in p.loop_indices])@rot.T;ts/=np.maximum(np.linalg.norm(ts,axis=1)[:,None],1e-10);ns=np.array([list(m.corner_normals[i].vector) for i in p.loop_indices])@nr.T;ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-10);ret[p.index]=(ts,ns,np.array([m.loops[i].bitangent_sign for i in p.loop_indices]))
 return ret
for o in obs:
 m=o.data;positions[o.name]=np.array([list(o.matrix_world@v.co) for v in m.vertices]);frames_old[o.name]=frames(o,oldname);u=m.uv_layers.new(name=newname,do_init=True);m.uv_layers.active=u;u.active_render=True
 for a,b in zip(u.data,m.uv_layers[oldname].data):a.uv=b.uv
# Pack all selected triangles together. Each original UV layer remains untouched.
bpy.ops.object.select_all(action='DESELECT');bpy.context.tool_settings.mesh_select_mode=(False,False,True)
for o in obs:
 if o.name not in selected:continue
 o.select_set(True);bpy.context.view_layer.objects.active=o
 for p in o.data.polygons:p.select=p.index in selected[o.name]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.uv.smart_project(angle_limit=math.radians(35),island_margin=.008,area_weight=0,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
for o in obs:
 for p in o.data.polygons:
  if p.index not in selected.get(o.name,{}):
   for i in p.loop_indices:o.data.uv_layers[newname].data[i].uv=o.data.uv_layers[oldname].data[i].uv
 frames_new[o.name]=frames(o,newname)
# Per-group exterior edges let the grilles retain a continuous rim around folded faces.
boundaries={}
for name,gs in groups.items():
 o=bpy.data.objects[name];m=o.data
 for kind,ids in gs.items():
  sets=[ids]
  if name=='Patriot_Cockpit' and kind=='pod':sets=[[50,51,52,53]]
  count={}
  for i in sets[0]:
   vv=list(m.polygons[i].vertices)
   for a,b in zip(vv,vv[1:]+vv[:1]):e=tuple(sorted((a,b)));count[e]=count.get(e,0)+1
  boundaries[(name,kind)]=[(positions[name][a],positions[name][b]) for (a,b),v in count.items() if v==1]
def edgedist(p,edges):
 d=np.full(len(p),1e3)
 for a,b in edges:
  v=b-a;t=np.clip((p-a)@v/np.dot(v,v),0,1);d=np.minimum(d,np.linalg.norm(p-a-t[:,None]*v,axis=1))
 return d
def linecut(v,c,w=.0028):return 1-smooth(w*.3,w,np.abs(v-c))
def poly_dist(q,vertices):
 pp=np.array(vertices);d=np.full(len(q),1e6);area=np.sum(pp[:,0]*np.roll(pp[:,1],-1)-pp[:,1]*np.roll(pp[:,0],-1))
 for a,b in zip(pp,np.roll(pp,-1,axis=0)):
  v=b-a;d=np.minimum(d,np.sign(area)*(v[0]*(q[:,1]-a[1])-v[1]*(q[:,0]-a[0]))/np.linalg.norm(v))
 return d
def capdist(q,a,b,r):
 v=np.subtract(b,a);t=np.clip((q-a)@v/np.dot(v,v),0,1);return r-np.linalg.norm(q-a-t[:,None]*v,axis=1)
def basis(fr,b):
 ts,ns,sign=fr;n=b@ns;n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-8);t=b@ts;t-=n*np.sum(n*t,axis=1)[:,None];t/=np.maximum(np.linalg.norm(t,axis=1)[:,None],1e-8);bt=np.cross(n,t)*np.sign(b@sign)[:,None];return t,bt,n
# Muzzle centres follow the area centroid of each original polygon end, not an atlas guess.
muzzle={};body=bpy.data.objects['Patriot_Body'];bp=positions[body.name]
for ids in [list(range(368,372)),list(range(372,376))]:
 vv=[];areas=[];cc=[]
 for i in ids:
  pts=bp[list(body.data.polygons[i].vertices)];ar=np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]));areas.append(ar);cc.append(pts.mean(0));vv.extend(pts.tolist())
 center=np.average(cc,axis=0,weights=areas);edges=boundaries[(body.name,'muzzle')];radius=min(np.linalg.norm(center[[0,2]]-np.array(a)[[0,2]]) for a,b in edges if np.sign(a[0])==np.sign(center[0]))*.54
 for i in ids:muzzle[i]=(center,.028)
# Atlas targets are evaluated on the real surface, with normals rebaked into its new tangent frame.
out={k:np.zeros((N,N,3),np.float32) for k in ['basecolor','normal','roughness','metallic','height']};out['normal'][:]=(.5,.5,1);coverage=np.zeros((N,N),bool);classification=np.zeros((N,N),np.uint8);face_reports=[];kindids={k:i+1 for i,k in enumerate(['nose','pod','arm_fins','joint','radiator','long_vent','engine','rear','muzzle'])}
for name,lookup in selected.items():
 o=bpy.data.objects[name];m=o.data;vp=positions[name]
 for fi,kind in sorted(lookup.items()):
  f=m.polygons[fi];uv=np.array([list(m.uv_layers[newname].data[i].uv) for i in f.loop_indices]);old=np.array([list(m.uv_layers[oldname].data[i].uv) for i in f.loop_indices]);fv=vp[list(f.vertices)];xy=np.column_stack((uv[:,0]*N,(1-uv[:,1])*N));lo=np.maximum(0,np.floor(xy.min(0)).astype(int));hi=np.minimum(N,np.ceil(xy.max(0)).astype(int));yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];pt=np.column_stack((xx.ravel()+.5,yy.ravel()+.5));bb=(pt-xy[0])@np.linalg.inv(np.column_stack((xy[1]-xy[0],xy[2]-xy[0]))).T;b=np.column_stack((1-bb.sum(1),bb));inside=b.min(1)>=-1e-7;b=b[inside];rx=xx.ravel()[inside];ry=yy.ravel()[inside];dup=coverage[ry,rx];assert not dup.any() or np.max(b[dup].min(1))<.0001,(name,fi,'UV overlap');b=b[~dup];rx=rx[~dup];ry=ry[~dup];coverage[ry,rx]=True;classification[ry,rx]=kindids[kind];pos=b@fv;q=b@old;px=np.column_stack(((q[:,0]%1)*1254,(1-q[:,1]%1)*1254));col=sample(main['basecolor'],q);rough=sample(main['roughness'],q)[:,0];metal=sample(main['metallic'],q)[:,0];orig_n=sample(main['normal'],q)*2-1
  oldt,oldbt,ns=basis(frames_old[name][fi],b);ts,bts,n=basis(frames_new[name][fi],b);oldworld=oldt*orig_n[:,0,None]+oldbt*orig_n[:,1,None]+ns*orig_n[:,2,None];oldworld/=np.maximum(np.linalg.norm(oldworld,axis=1)[:,None],1e-8);fn=np.cross(fv[1]-fv[0],fv[2]-fv[0]);fn/=np.linalg.norm(fn);gn=np.broadcast_to(fn,pos.shape);replacement=np.ones(len(pos));h=np.zeros(len(pos));heightfn=None;edges=boundaries[(name,kind)]
  # Affine lookup for fixed motifs and physical gradients, continuous within each original chart.
  pinv=np.linalg.pinv((fv[1:]-fv[0]).T)
  def px_at(p):
   st=(p-fv[0])@pinv.T;qq=old[0]+st@(old[1:]-old[0]);return np.column_stack(((qq[:,0]%1)*1254,(1-qq[:,1]%1)*1254))
  if kind=='nose':
   colnew=triplanar(pos,gn,'bronze');roughnew=np.full(len(pos),.80);metalnew=np.full(len(pos),.04)
   if fi in [8,15]:replacement=smooth(174,193,px[:,0])
   # Keep the framed back join; all front wrap panels share the same physical cuts.
   replacement*=smooth(.831,.865,pos[:,1])
   def heightfn(p):
    cap=linecut(p[:,1],1.195,.0027);centre=linecut(p[:,0],.00058,.0022)*smooth(1.18,1.20,p[:,1]);ring=linecut(p[:,2],.294,.0026)*smooth(1.19,1.205,p[:,1]);side=linecut(p[:,1],1.007,.0025)*(1-smooth(.18,.20,p[:,2]));return -.0015*np.maximum.reduce([cap,centre,ring,side])
   h=heightfn(pos);cut=np.clip(-h/.0015,0,1);colnew*=1-.70*cut[:,None];roughnew=roughnew*(1-cut)+.87*cut;col=col*(1-replacement[:,None])+colnew*replacement[:,None];rough=rough*(1-replacement)+roughnew*replacement;metal=metal*(1-replacement)+metalnew*replacement
  elif kind in ['pod','arm_fins']:
   if kind=='pod' and fi in [48,49]:
    col=triplanar(pos,gn,'bronze');rough[:]=.81;metal[:]=.06
    def heightfn(p):return -.0013*np.maximum(linecut(p[:,1],1.113),linecut(p[:,0],.00058)*.7)
    h=heightfn(pos);col*=1-.65*np.clip(-h/.0013,0,1)[:,None]
   else:
    pitch=.029 if kind=='pod' else .047;start=.825 if kind=='pod' else .91
    def data(p):
     d=edgedist(p,edges);floor=smooth(.004,.008,d);fin=(1-smooth(pitch*.11,pitch*.28,np.abs((p[:,1]-start+pitch/2)%pitch-pitch/2)))*floor;return floor,fin,d
    def heightfn(p):
     floor,fin,d=data(p);return -.0038*floor+.0044*fin
    floor,fin,dd=data(pos);h=heightfn(pos);housing=triplanar(pos,gn,'bronze')
    if kind=='arm_fins':
     green=smooth(1.19,1.17,pos[:,1]);housing=housing*(1-green[:,None])+triplanar(pos,gn,'green')*green[:,None]
    col=housing*(1-floor[:,None])+(np.array([.023,.028,.03])+(np.array([.19,.20,.205])-.026)*fin[:,None])*floor[:,None];rough=.80*(1-floor)+(.86-.43*fin)*floor;metal=.05*(1-floor)+(.12+.74*fin)*floor
  elif kind=='joint':
   col=triplanar(pos,gn,'steel');rough[:]=.57;metal[:]=.84
   def heightfn(p):return -.0015*np.maximum.reduce([linecut(p[:,1],-.46),linecut(p[:,1],-.77),linecut(np.abs(p[:,0]),.79)])
   h=heightfn(pos);cut=np.clip(-h/.0015,0,1);col*=1-.72*cut[:,None];metal*=1-.8*cut;rough=rough*(1-cut)+.88*cut
  elif kind=='engine':
   brown=smooth(-1.185,-1.205,pos[:,1]);col=triplanar(pos,gn,'green')*(1-brown[:,None])+triplanar(pos,gn,'bronze')*brown[:,None];rough[:]=.81;metal[:]=.045
   def heightfn(p):
    ring=np.maximum(linecut(p[:,1],-1.20,.0027),linecut(p[:,1],-1.355,.0026));angle=np.arctan2(p[:,2]-.565,np.abs(p[:,0])-.307);seam=1-smooth(.007,.025,np.abs(np.sin(angle*2)));end=linecut(p[:,1],-1.51,.0028);return -.0015*np.maximum.reduce([ring,seam,end])
   h=heightfn(pos);cut=np.clip(-h/.0015,0,1);col*=1-.75*cut[:,None];rough=rough*(1-cut)+.88*cut
   # Retain the original outboard engine louvre instead of replacing it with blank paint.
   if fi in [227,228,229,230,231,232,233,234]:
    d=capdist(px,np.array([1002,882]),np.array([1002,1163]),17);keep=smooth(-3,0,d);col=col*(1-keep[:,None])+sample(main['basecolor'],q)*keep[:,None];rough=rough*(1-keep)+sample(main['roughness'],q)[:,0]*keep;metal=metal*(1-keep)+sample(main['metallic'],q)[:,0]*keep;replacement=1-keep
  elif kind=='radiator':
   polygon=[(193,1189),(222,1159),(250,1147),(356,1147),(389,1176),(389,1221),(193,1221)]
   def data(p):
    uvp=px_at(p);d=poly_dist(uvp,polygon);floor=smooth(0,3,d);fin=np.zeros(len(p))
    for x in [231,275,318,361]:fin=np.maximum(fin,smooth(0,7.5,capdist(uvp,np.array([x,1173]),np.array([x,1204]),9.5)))
    return floor,fin*floor,d
   def heightfn(p):
    floor,fin,d=data(p);return -.0040*floor+.0052*fin
   floor,fin,d=data(pos);replacement=smooth(-1,0,d);h=heightfn(pos);newcol=np.array([.021,.026,.029])+(np.array([.225,.235,.237])-.024)*fin[:,None];col=col*(1-replacement[:,None])+newcol*replacement[:,None];rough=rough*(1-replacement)+(.85-.40*fin)*replacement;metal=metal*(1-replacement)+(.15+.70*fin)*replacement
  elif kind=='long_vent':
   # One longitudinal channel runs across both old charts. Outside its local repair strip, artwork is retained.
   def data(p):
    pp=np.column_stack((np.abs(p[:,0]),p[:,1]));d=capdist(pp,np.array([.563,-.12]),np.array([.563,.87]),.026);floor=smooth(0,.0025,d);rim=smooth(-.008,-.006,d)*(1-floor);fins=np.zeros(len(p))
    for off in [-.011,0,.011]:fins=np.maximum(fins,1-smooth(.001,.0027,np.abs(np.abs(p[:,0])-.563-off)))
    fins*=smooth(.003,.007,d);return d,floor,rim,fins
   def heightfn(p):
    d,floor,rim,fins=data(p);return -.0035*floor+.0039*fins+.0006*rim
   d,floor,rim,fins=data(pos);h=heightfn(pos);replacement=smooth(-.016,-.013,d);background=triplanar(pos,gn,'steel');newcol=background*(1-np.clip(floor+rim,0,1)[:,None])+np.array([.27,.29,.29])*rim[:,None]+(np.array([.018,.025,.028])+.13*fins[:,None])*floor[:,None];col=col*(1-replacement[:,None])+newcol*replacement[:,None];rough=rough*(1-replacement)+(.55*rim+(.87-.43*fins)*floor+.63*(1-np.clip(rim+floor,0,1)))*replacement;metal=metal*(1-replacement)+(.80*rim+(.12+.72*fins)*floor+.78*(1-np.clip(rim+floor,0,1)))*replacement
  elif kind=='rear':
   col=triplanar(pos,gn,'steel')*.87;rough[:]=.60;metal[:]=.79
   # Reproject the original hatch as one feature; surrounding panel cuts share world positions.
   hatchpx=np.column_stack((173-(pos[:,2]-.184)*645,1117.5+pos[:,0]*646));hq=np.column_stack((hatchpx[:,0]/1254,1-hatchpx[:,1]/1254));hd=poly_dist(hatchpx,[(8,1034),(165,1034),(165,1204),(8,1204)]);hm=smooth(-2,0,hd);col=col*(1-hm[:,None])+sample(main['basecolor'],hq)*hm[:,None];rough=rough*(1-hm)+sample(main['roughness'],hq)[:,0]*hm;metal=metal*(1-hm)+sample(main['metallic'],hq)[:,0]*hm
   # Keep every original red warning marker around the hatch, including those beyond its frame.
   hc=sample(main['basecolor'],hq);red=smooth(1.35,1.8,hc[:,0]/(hc[:,1]+.004))*smooth(1.3,1.7,hc[:,0]/(hc[:,2]+.004));bounds=(hatchpx[:,0]>=0)&(hatchpx[:,0]<=178)&(hatchpx[:,1]>=985)&(hatchpx[:,1]<=1237);red*=bounds;col=col*(1-red[:,None])+hc*red[:,None];rough=rough*(1-red)+.83*red;metal*=1-red
   def heightfn(p):
    hp=np.column_stack((173-(p[:,2]-.184)*645,1117.5+p[:,0]*646));inside=smooth(-2,0,poly_dist(hp,[(8,1034),(165,1034),(165,1204),(8,1204)]));return -.0016*np.maximum.reduce([linecut(np.abs(p[:,0]),.205),linecut(p[:,2],.493),linecut(p[:,2],.233)])*(1-inside)
   h=heightfn(pos);cut=np.clip(-h/.0016,0,1)*(1-hm);col*=1-.74*cut[:,None];h*=1-hm
   # Preserve the existing black corner fittings at their original mapped positions.
   if fi in [212,213]:
    rr=np.linalg.norm(px-np.array([857,372]),axis=1);mask=1-smooth(21,24,rr);col=col*(1-mask[:,None])+sample(main['basecolor'],q)*mask[:,None];rough=rough*(1-mask)+sample(main['roughness'],q)[:,0]*mask;metal=metal*(1-mask)+sample(main['metallic'],q)[:,0]*mask
  elif kind=='muzzle':
   center,radius=muzzle[fi];off=pos[:,[0,2]]-center[[0,2]];rr=np.linalg.norm(off,axis=1);mq=np.column_stack(((662+off[:,0]/radius*15)/1254,1-(496-off[:,1]/radius*15)/1254));mask=1-smooth(radius*.97,radius*1.03,rr);col=triplanar(pos,gn,'bronze')*(1-mask[:,None])+sample(main['basecolor'],mq)*mask[:,None];rough=.80*(1-mask)+.42*mask;metal=.05*(1-mask)+.76*mask
   def heightfn(p):
    r=np.linalg.norm(p[:,[0,2]]-center[[0,2]],axis=1);return -.004*(1-smooth(radius*.70,radius*.82,r))+.0007*(1-smooth(.001,.0025,np.abs(r-radius*.9)))
   h=heightfn(pos)
  grad=np.zeros_like(pos)
  if heightfn:
   eps=.0001
   for ax in range(3):
    off=np.zeros(3);off[ax]=eps;grad[:,ax]=(heightfn(pos+off)-heightfn(pos-off))/(2*eps)
   grad-=n*np.sum(grad*n,axis=1)[:,None]
  world=n-grad;world/=np.maximum(np.linalg.norm(world,axis=1)[:,None],1e-9);world=world*replacement[:,None]+oldworld*(1-replacement[:,None]);world/=np.maximum(np.linalg.norm(world,axis=1)[:,None],1e-9);normal=np.column_stack((np.sum(world*ts,1),np.sum(world*bts,1),np.sum(world*n,1)));normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
  for key,val in [('basecolor',col),('normal',normal*.5+.5),('roughness',rough[:,None]),('metallic',metal[:,None]),('height',(h+.012)[:,None]/.024)]:out[key][ry,rx]=np.clip(val,0,1)
  e=fv[1:]-fv[0];area=np.linalg.norm(np.cross(*e))/2;t=e[0]/np.linalg.norm(e[0]);local=e@np.stack((t,np.cross(fn,t)),axis=1);sing=np.linalg.svd(np.linalg.solve(local,uv[1:]-uv[0]),compute_uv=False);face_reports.append({'part':name,'face':fi,'kind':kind,'pixels':len(rx),'uv_anisotropy':float(sing[0]/sing[1]),'texel_density':float(np.sqrt(sing.prod())*N)});print('BAKED',name,fi,kind,len(rx),flush=True)
# Pad twelve pixels outside islands to keep filtering away from unrelated artwork.
idx=np.full((N,N),-1,np.int32);idx[coverage]=np.flatnonzero(coverage)
for _ in range(12):
 updated=idx.copy()
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
  q=np.roll(idx,shift,axis);take=(updated<0)&(q>=0);updated[take]=q[take]
 idx=updated
pad=(idx>=0)&~coverage;records={}
for key,a in out.items():a[pad]=a.reshape(-1,3)[idx[pad]];records[key]=save(a,'patriot_repairs_'+key+'_4k_v2')
records['regions']=save(classification.astype(np.float32)/16,'patriot_repairs_regions_4k_v2')
def material(name,maps):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links;uv=nodes.new('ShaderNodeUVMap');uv.uv_map=newname;bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Specular IOR Level'].default_value=.4;bs.inputs['IOR'].default_value=1.46;out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
 for key in ['basecolor','normal','roughness','metallic']:
  im=bpy.data.images.load(maps[key]['path'],check_existing=False);im.colorspace_settings.name='sRGB' if key=='basecolor' else 'Non-Color';im.pack();node=nodes.new('ShaderNodeTexImage');node.name='Delivered '+key;node.image=im;links.new(uv.outputs[0],node.inputs[0])
  if key=='normal':nm=nodes.new('ShaderNodeNormalMap');nm.uv_map=newname;links.new(node.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
  else:links.new(node.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 return mat
mainmat=material('Patriot_Hull_Glass_PBR_v2',mainrecords);fixmat=material('Patriot_Seams_Fins_PBR_v2',records);models={}
for o in obs:
 m=o.data;m.materials[0]=mainmat
 if o.name in selected:
  m.materials.append(fixmat);assert len(m.materials)==3
  for fi in selected[o.name]:m.polygons[fi].material_index=2
 b=before[o.name];assert b['v']==[list(v.co) for v in m.vertices] and b['f']==[list(p.vertices) for p in m.polygons] and b['n']==[list(q.vector) for q in m.corner_normals]
 for name,values in b['uv'].items():assert values==[list(q.uv) for q in m.uv_layers[name].data]
 for p in m.polygons:
  if p.index not in selected.get(o.name,{}):assert all((m.uv_layers[oldname].data[i].uv-m.uv_layers[newname].data[i].uv).length<1e-7 for i in p.loop_indices)
 models[o.name]={'vertices':[list(v.co) for v in m.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(m.uv_layers[newname].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in m.polygons]}
assert max(f['uv_anisotropy'] for f in face_reports)<2.0
for material_old in list(bpy.data.materials):
 if material_old.users==0:bpy.data.materials.remove(material_old)
for image_old in list(bpy.data.images):
 if image_old.users==0 and Path(image_old.filepath).name!='yank_3.png':bpy.data.images.remove(image_old)
s['v2_repair_note']='Clean masked glass including hatch; legacy ribbed under-nose wedge; local UV charts with continuous physical fin/panel fields; centred muzzles. Original topology, vertices, custom normals, hidden caps, turret and all prior UVs retained. No emissives.';s.render.image_settings.color_depth='8';bpy.context.preferences.filepaths.save_version=0;scene=D/'patriot_worn_refined_v2.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene));assert sha(src)==srcsha
report={'source':str(src),'source_sha256':srcsha,'scene':str(scene),'scene_sha256':sha(scene),'active_uv':newname,'main_maps':mainrecords,'maps':records,'groups':groups,'face_reports':face_reports,'models':models,'original_geometry_normals_and_uvs_preserved':True,'unchanged_face_uvs_preserved':True,'glass_panes':6,'glass_roughness':.115,'glass_metallic':0,'muzzle_centres':{str(k):c.tolist() for k,(c,r) in muzzle.items()},'max_repaired_uv_anisotropy':max(f['uv_anisotropy'] for f in face_reports),'emissives':'deferred','runtime_visual_validation':'pending user review'};(W/'validation.json').write_text(json.dumps(report,indent=2));print('PATRIOT_V2_COMPLETE',len(face_reports),flush=True)
