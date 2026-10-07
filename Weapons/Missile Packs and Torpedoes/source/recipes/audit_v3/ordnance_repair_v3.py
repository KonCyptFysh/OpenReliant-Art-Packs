import os
import bpy,sys,json,math
from pathlib import Path
import numpy as np
D=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve();W=D/'work/audit_v3';sys.path.insert(0,str(W));import ordnance_native as n
bpy.ops.wm.open_mainfile(filepath=str(D/'ordnance_worn_audit_v2.blend'));bpy.context.view_layer.update();UV='Ordnance_Delivery_UV_v3';log=[]
objs={}
for o in bpy.data.objects:
 if o.type!='MESH' or not o.get('native_model'):continue
 objs[o['native_model'],int(o['native_part']),int(o['native_lod'])]=o
 uv=o.data.uv_layers.new(name=UV)
 for a,b in zip(uv.data,o.data.uv_layers['Ordnance_Delivery_UV_v2'].data):a.uv=b.uv
 o.data.uv_layers.active=uv;uv.active_render=True
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type in ('UVMAP','NORMAL_MAP') and node.uv_map=='Ordnance_Delivery_UV_v2':node.uv_map=UV

def getuv(o,p):return np.array([[o.data.uv_layers[UV].data[l].uv.x,1-o.data.uv_layers[UV].data[l].uv.y] for l in p.loop_indices])*1254

def put(o,p,q):
 for l,(u,v) in zip(p.loop_indices,np.array(q)/1254):o.data.uv_layers[UV].data[l].uv=(u,1-v)

def record(o,label,ids):
 if ids:log.append(dict(file=o['native_model'],part=int(o['native_part']),lod=int(o['native_lod']),repair=label,faces=list(map(int,ids))))

def planar(o,ids,box,axes=None):
 if not ids:return
 vv=np.array([v.co[:] for v in o.data.vertices]);idx=sorted({i for f in ids for i in o.data.polygons[f].vertices});xyz=vv[idx];c=xyz.mean(0)
 if axes is None:_,_,vh=np.linalg.svd(xyz-c,full_matrices=False);xy=(xyz-c)@vh[:2].T
 else:xy=xyz[:,axes]
 lo,hi=xy.min(0),xy.max(0);a,b,c,d=box;s=min((c-a)/max(hi[0]-lo[0],1e-8),(d-b)/max(hi[1]-lo[1],1e-8));q=(xy-(lo+hi)/2)*s+[(a+c)/2,(b+d)/2];lookup=dict(zip(idx,q))
 for f in ids:p=o.data.polygons[f];put(o,p,[lookup[i] for i in p.vertices])

def ring(o,ids,box,zlimits=None):
 if not ids:return
 vv=np.array([v.co[:] for v in o.data.vertices]);pts=np.concatenate([vv[list(o.data.polygons[f].vertices)] for f in ids]);zlo,zhi=(pts[:,2].min(),pts[:,2].max()) if zlimits is None else zlimits;a,b,c,d=box
 for i in ids:
  p=o.data.polygons[i];xyz=vv[list(p.vertices)];k=np.rint((np.arctan2(xyz[:,1],xyz[:,0])-math.pi/8)/(math.pi/4)).astype(int);u=np.where(k%2==0,a,c);v=d-(xyz[:,2]-zlo)/max(zhi-zlo,1e-8)*(d-b);put(o,p,np.column_stack((u,v)))

for (name,part,lod),o in objs.items():
 if name not in ['01_screamer_pod.SHP','02_raptor.SHP','02_raptor_POD.SHP','04_jackhammer.SHP','05_bandit.SHP','08_imp.SHP','fuel_pod.SHP']:continue
 v=np.array([x.co[:] for x in o.data.vertices]);ff=o.data.polygons
 if name=='02_raptor.SHP':
  # Solve each complete fin side, including the formerly isolated red tip triangle.
  ids=[p.index for p in ff if all(-44<v[i,2]<7 for i in p.vertices) and max(np.linalg.norm(v[list(p.vertices),:2],axis=1))>23 and abs(p.normal.z)<.1]
  rem=set(ids)
  while rem:
   seed=min(rem);g={seed};rem.remove(seed);more=True
   while more:
    more=False
    for i in sorted(rem):
     if any(len(set(ff[i].vertices)&set(ff[j].vertices))>=2 and np.dot(ff[i].normal,ff[j].normal)>.985 for j in g):g.add(i);rem.remove(i);more=True
   # Same physical fin projection on both triangles; original worn steel region.
   ps=np.concatenate([v[list(ff[i].vertices)] for i in g]);radial=ps[:,:2].mean(0);radial/=np.linalg.norm(radial);coords=np.column_stack((ps[:,:2]@radial,ps[:,2]));lo,hi=coords.min(0),coords.max(0);s=min(65/max(hi[0]-lo[0],1e-8),160/max(hi[1]-lo[1],1e-8))
   for i in g:
    p=ff[i];xyz=v[list(p.vertices)];xy=np.column_stack((xyz[:,:2]@radial,xyz[:,2]));q=(xy-(lo+hi)/2)*[s,-s]+[599,571];put(o,p,q)
   record(o,'unified inboard fin side with no red corner or stretched seam',sorted(g))
  leading=[p.index for p in ff if max(np.linalg.norm(v[p.vertices[:],:2],axis=1))>23 and min(v[p.vertices[:],2])>-44 and max(v[p.vertices[:],2])<7 and abs(p.normal.z)>.2]
  for i in leading:planar(o,[i],(747,375,853,516))
  record(o,'undistorted inboard fin leading and root closure faces',leading)
 if name=='04_jackhammer.SHP':
  ids=[p.index for p in ff if min(v[p.vertices[:],2])>-35 and max(v[p.vertices[:],2])<200 and np.ptp(v[p.vertices[:],2])>100]
  ring(o,ids,(952,160,1016,610));record(o,'continuous cylinder bands on a single axial scale',ids)
  zmax=v[:,2].max();nose=[p.index for p in ff if max(v[p.vertices[:],2])>zmax-.1]
  planar(o,nose,(954,113,1011,185),axes=(0,1));record(o,'bronze nose cap matched to the bronze fairing',nose)
  ids=[p.index for p in ff if min(v[p.vertices[:],2])>-76 and max(v[p.vertices[:],2])<-65 and max(np.linalg.norm(v[p.vertices[:],:2],axis=1))<29]
  ring(o,ids,(944,20,1045,59));record(o,'continuous aft collar, replacing mismatched steel sections',ids)
 if name=='05_bandit.SHP':
  zmax=v[:,2].max();cap=[p.index for p in ff if max(v[p.vertices[:],2])>zmax-.1]
  fair=[p.index for p in ff if min(v[p.vertices[:],2])>10 and p.index not in cap]
  ring(o,fair,(1188,119,1246,335));record(o,'reconstructed continuous red nose fairing and silver circumferential bands',fair)
  planar(o,cap,(1046,132,1100,200),axes=(0,1));record(o,'coherent red terminal nose cap',cap)
  aft=[p.index for p in ff if min(v[p.vertices[:],2])>-31 and max(v[p.vertices[:],2])<-15 and max(np.linalg.norm(v[p.vertices[:],:2],axis=1))<23]
  ring(o,aft,(1187,515,1248,550));record(o,'consistent aft connector ring instead of unrelated steel patches',aft)
  body=[p.index for p in ff if min(v[p.vertices[:],2])>-18 and max(v[p.vertices[:],2])<13 and max(np.linalg.norm(v[p.vertices[:],:2],axis=1))<23]
  ring(o,body,(1187,337,1245,512));record(o,'aligned central body panels',body)
 if name=='08_imp.SHP':
  # Each longitudinal range is one complete ring, with identical mirrored edge samples.
  for label,zlo,zhi,box in [('blue barrel',22,101,(792,201,861,398)),('blue shoulder',99,121,(792,140.6,861,201))]:
   ids=[p.index for p in ff if min(v[p.vertices[:],2])>=zlo and max(v[p.vertices[:],2])<=zhi]
   ring(o,ids,box);record(o,'aligned '+label+' seams',ids)
 if name=='fuel_pod.SHP':
  visible=[p.index for p in ff if o.data.materials[p.material_index].name=='Original hidden damage caps' and p.normal.y<-.9]
  o['native_visible_cap_faces']=visible
  for i in visible:ff[i].material_index=0
  planar(o,visible,(747,371,858,514),axes=(0,2));record(o,'restore existing hidden top panel and planar worn-metal UVs',visible)
 if name=='01_screamer_pod.SHP':
  # Quiet metal on the sloping crown before the continuous mouth collar is baked.
  ids=[p.index for p in ff if p.normal.y<-.5 and .3<p.normal.z<.8 and min(v[p.vertices[:],2])>60]
  planar(o,ids,(749,380,854,520));record(o,'remove misplaced crown artwork behind mouth collar',ids)
 if name=='02_raptor_POD.SHP':
  ids=[]
  for p in ff:
   q=getuv(o,p);xyz=v[list(p.vertices)]
   if min(xyz[:,2])>-11 and max(xyz[:,2])<86 and abs(p.normal.z)<.6 and q[:,0].min()>1100 and q[:,0].max()<1176 and q[:,1].min()>160 and q[:,1].max()<405:
    q[:,1]=396.2-(xyz[:,2]+10.585)*227/95.914;put(o,p,q);ids.append(p.index)
  record(o,'align forward housing indents on a common longitudinal scale',ids)
# Save a checkpoint before baking new pod collars.
bpy.context.scene['active_delivery_uv']=UV;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'ordnance_worn_audit_v3_work.blend'),compress=True)
(W/'uv_repairs.json').write_text(json.dumps(log,indent=2));print('UV_V3_CHECKPOINT',len(log),flush=True)
