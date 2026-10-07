"""Apply targeted audit repairs to the latest editable v1, not an old reconstruction."""
import bpy,sys,json,math,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import ordnance_native as n
from ordnance_wrap_v2 import make_wrap
from ordnance_nozzle_v2 import make_nozzle
D=n.D;W=D/'work/audit_v2';W.mkdir(parents=True,exist_ok=True);uvname='Ordnance_Delivery_UV_v2';bpy.ops.wm.open_mainfile(filepath=str(D/'ordnance_worn_pbr_v1.blend'));bpy.context.view_layer.update()
files={p.name:n.models(p.read_bytes()) for p in (D/'source/native').glob('*.SHP')};objs={};data={};log=[]
protected={'07_Solomon_POD.SHP','27_Solomon_POD.SHP','09_hawk_POD.SHP','29_hawk_POD.SHP','10_torpedo.SHP','30_torpedo.SHP','torpedo.SHP'}
for o in list(bpy.data.objects):
 if o.type!='MESH' or not o.get('native_model'):continue
 key=(o['native_model'],o['native_part'],o['native_lod']);objs[key]=o;m=next(p for p in files[key[0]] if (p['part'],p['lod'])==key[1:]);m['new_uv']={};m['mat']={}
 new=o.data.uv_layers.new(name=uvname);old=o.data.uv_layers['Ordnance_Delivery_UV_v1']
 for a,b in zip(new.data,old.data):a.uv=b.uv
 o.data.uv_layers.active=new;new.active_render=True
 for f in m['faces']:
  q=np.zeros((3,2));poly=o.data.polygons[f['id']]
  for li in poly.loop_indices:q[o['native_corner_order'][li]]=(new.data[li].uv.x,1-new.data[li].uv.y)
  m['new_uv'][f['id']]=q;m['mat'][f['id']]=0
 data[key]=m
for mat in bpy.data.materials:
 if mat.use_nodes:
  for no in mat.node_tree.nodes:
   if no.type in ('UVMAP','NORMAL_MAP') and no.uv_map=='Ordnance_Delivery_UV_v1':no.uv_map=uvname

def planar_groups(m):
 v=np.array(m['verts']);ff=m['faces'];norm=[];orient=[]
 for f in ff:
  xyz=v[f['indices']];nn=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);norm.append(nn/max(np.linalg.norm(nn),1e-12));q=m['new_uv'][f['id']];d=q[1:]-q[0];orient.append(np.sign((d[0,0]*d[1,1]-d[0,1]*d[1,0])*nn[np.argmax(abs(nn))]))
 edges={}
 for f in ff:
  if f['hidden']:continue
  for a,b in zip(f['indices'],np.roll(f['indices'],-1)):edges.setdefault(tuple(sorted((a,b))),[]).append(f['id'])
 adj={i:set() for i in range(len(ff))}
 for (a,b),fs in edges.items():
  for i in fs:
   for j in fs:
    if i>=j or abs(np.dot(norm[i],norm[j]))<.9995 or orient[i]!=orient[j] or orient[i]==0:continue
    fi,fj=ff[i],ff[j]
    if a==b:continue
    err=max(np.linalg.norm(m['new_uv'][i][fi['indices'].index(vert)]-m['new_uv'][j][fj['indices'].index(vert)]) for vert in (a,b))
    if err*1254<2.5:adj[i].add(j);adj[j].add(i)
 remain=set(adj)
 while remain:
  g={min(remain)};walk=list(g);remain-=g
  while walk:
   i=walk.pop();new=adj[i]&remain;g|=new;remain-=new;walk+=list(new)
  if len(g)>1:yield sorted(g)

def affine_cleanup(name,m):
 v=np.array(m['verts']);changed=0;maxerr=0
 for g in planar_groups(m):
  xyz=np.concatenate([v[m['faces'][i]['indices']] for i in g]);qs=np.concatenate([m['new_uv'][i] for i in g]);c=xyz.mean(0);_,_,vh=np.linalg.svd(xyz-c,full_matrices=False);xy=(xyz-c)@vh[:2].T;A=np.column_stack((xy,np.ones(len(xy))));pred=A@np.linalg.lstsq(A,qs,rcond=None)[0];err=np.linalg.norm(pred-qs,axis=1).max()*1254
  if err<.12:continue
  # Keep the corrected affine island inside its established atlas allocation.
  lo,hi=qs.min(0),qs.max(0);pl,ph=pred.min(0),pred.max(0);scale=min(1,*((hi-lo)/np.maximum(ph-pl,1e-9)));pred=(pred-(pl+ph)/2)*scale+(lo+hi)/2
  before=[n.ratio(v[m['faces'][i]['indices']],m['new_uv'][i]) for i in g];after=[n.ratio(v[m['faces'][i]['indices']],pred[3*j:3*j+3]) for j,i in enumerate(g)]
  if max(after)>max(12,max(before)*1.1):continue
  for j,i in enumerate(g):m['new_uv'][i]=pred[3*j:3*j+3]
  changed+=len(g);maxerr=max(maxerr,err)
 if changed:log.append(dict(file=name,part=m['part'],lod=m['lod'],repair='straight affine panel and fin islands',faces=changed,max_old_kink_px=maxerr))

def plane_patch(m,faceids,box,axes=(0,1)):
 v=np.array(m['verts']);ids=sorted({j for i in faceids for j in m['faces'][i]['indices']});xyz=v[ids];p=xyz[:,axes];lo,hi=p.min(0),p.max(0);a,b,c,d=box;scale=min((c-a)/max(hi[0]-lo[0],1e-9),(d-b)/max(hi[1]-lo[1],1e-9));q=(p-(lo+hi)/2)*scale+[(a+c)/2,(b+d)/2];lookup=dict(zip(ids,q/1254))
 for i in faceids:m['new_uv'][i]=np.array([lookup[j] for j in m['faces'][i]['indices']])

def missile(name,m):
 v=np.array(m['verts']);ff=m['faces'];rear=[f['id'] for f in ff if np.array(f['uv'])[:,0].min()>.92 and np.array(f['uv'])[:,1].max()<.08 and not f['hidden']]
 if rear:
  ids=sorted({j for i in rear for j in ff[i]['indices']});xy=v[ids,:2];c=(xy.min(0)+xy.max(0))/2;radius=np.max(np.linalg.norm(xy-c,axis=1));scale=.495/radius
  for i in rear:
   p=v[ff[i]['indices'],:2]-c;m['new_uv'][i]=np.column_stack((.5-p[:,0]*scale,.5-p[:,1]*scale));m['mat'][i]=2
  log.append(dict(file=name,part=m['part'],lod=m['lod'],repair='rear nozzle and normal centred together',faces=rear,mesh_centre=c.tolist(),uv_centre=[.5,.5],uv_radius=.495))
 # Do not alter Imp nose: user approved it; Raptor nose also left as-is.
 if name[:2] not in ('02','08'):
  zmax=v[:,2].max();nose=[f['id'] for f in ff if max(v[f['indices'],2])>zmax-1e-4 and not f['hidden']]
  box=(1046,132,1100,200) if name[:2] in ('03','04','05','07') else (747,371,858,514)
  if nose:
   previous={i:m['new_uv'][i].copy() for i in nose};plane_patch(m,nose,box)
   if max(n.ratio(v[ff[i]['indices']],m['new_uv'][i]) for i in nose)>12:
    for i,q in previous.items():m['new_uv'][i]=q
   else:log.append(dict(file=name,part=m['part'],lod=m['lod'],repair='coherent nose cap, no pinched UV fan',faces=nose,atlas_box=box))
 if name[:2]=='03' and m['lod']==0:
  # Remove overlapping bolt stamps on the long red fairing as well.
  targets=[f['id'] for f in ff if np.array(f['uv'])[:,0].min()>.87 and np.array(f['uv'])[:,1].max()<.16 and v[f['indices'],2].min()>v[:,2].max()*.57]
  for i in targets:
   if i in nose:continue
   p=v[ff[i]['indices']];theta=np.unwrap(np.arctan2(p[:,1],p[:,0]));theta=(theta-theta.min())/max(np.ptp(theta),1e-9);m['new_uv'][i]=np.column_stack((1050+36*theta,189-(p[:,2]-77.2)*1.35))/1254
  if targets:log.append(dict(file=name,part=m['part'],lod=m['lod'],repair='clear overlapping nose bolts',faces=targets))
 if name[:2]=='01':
  body=[f['id'] for f in ff if np.array(f['uv'])[:,0].min()>708/1254 and np.array(f['uv'])[:,0].max()<746/1254 and np.array(f['uv'])[:,1].min()>118/1254 and np.array(f['uv'])[:,1].max()<714/1254 and not f['hidden']]
  for i in body:
   p=v[ff[i]['indices']];u=(np.arctan2(p[:,1],p[:,0])+math.pi)/(2*math.pi)
   if np.ptp(u)>.5:u=np.where(u<.5,u+1,u)
   t=(p[:,2]+17.14)/(109.37+17.14);m['new_uv'][i]=np.column_stack((u,1-t));m['mat'][i]=1
  log.append(dict(file=name,part=m['part'],lod=m['lod'],repair='continuous seven-start barber-pole wrap',faces=body))

flight=[x for x in files if x not in protected and (x.startswith('0') or x in ['fuel_pod.SHP','Rus_Torp.SHP'])]
for name in flight:
 for key,m in data.items():
  if key[0]!=name:continue
  affine_cleanup(name,m)
  if name=='Rus_Torp.SHP':
   v=np.array(m['verts']);fixed=[]
   for f in m['faces']:
    old=np.array(f['uv'])*1254
    if old[:,0].max()>81 or f['hidden']:continue
    p=v[f['indices']];z=p[:,2];yy=np.where(z<=422.67,216+(422.67-z)/(422.67+713.79)*(1157.5-216),np.where(z<=485.09,98+(485.09-z)/(485.09-422.67)*118,98-(z-485.09)/(510.85-485.09)*70));m['new_uv'][f['id']][:,1]=yy/1254;fixed.append(f['id'])
   affine_cleanup(name,m);log.append(dict(file=name,part=m['part'],lod=m['lod'],repair='keep radiator wholly on straight nose side, clear bevel and cap',faces=fixed))
  if name.startswith('0') and 'pod' not in name.lower():missile(name,m)
  if name=='01_screamer_pod.SHP' and m['lod']==0:
   plane_patch(m,[39,40],(748,375,855,519),axes=(0,2));log.append(dict(file=name,lod=0,repair='undistorted worn upper access panel',faces=[39,40]))
# Transfer corrected in-flight faces into display variants; retain display-only geometry and animation.
for name in flight:
 if name=='Rus_Torp.SHP':continue
 pair='31_fuel_pod.SHP' if name=='fuel_pod.SHP' else str(int(name[:2])+20)+name[2:]
 for key,target in data.items():
  if key[0]!=pair:continue
  candidates=[m for k,m in data.items() if k[0]==name and m['lod']==target['lod']]
  if not candidates:continue
  source=candidates[0];sv=np.array(source['verts']);tv=np.array(target['verts']);mapping={}
  if 'pod' not in name.lower() and len(sv)==len(tv):mapping={i:i for i in range(len(tv))}
  else:
   # Native pod vertex lists may split seam vertices or add animated doors.
   # Estimate scale/translation using bounding boxes; a reflection is tested too.
   best=None
   for signs in [(1,1,1),(-1,-1,1),(-1,1,1),(1,-1,1)]:
    vv=sv*np.array(signs);scale=np.ptp(tv[:,2])/max(np.ptp(vv[:,2]),1e-9);delta=(tv.min(0)+tv.max(0))/2-(vv.min(0)+vv.max(0))/2*scale;dist=np.linalg.norm(tv[:,None,:]-(vv*scale+delta)[None,:,:],axis=2);near=dist.argmin(1);err=dist.min(1);score=sum(err<.005*max(np.ptp(tv,axis=0)))
    if best is None or score>best[0]:best=(score,near,err)
   mapping={i:int(j) for i,(j,e) in enumerate(zip(best[1],best[2])) if e<.005*max(np.ptp(tv,axis=0))}
  lookup={}
  for f in source['faces']:lookup.setdefault(tuple(sorted(f['indices'])),[]).append(f)
  count=0
  for f in target['faces']:
   if not all(i in mapping for i in f['indices']):continue
   idx=[mapping[i] for i in f['indices']];choices=lookup.get(tuple(sorted(idx)))
   if not choices:continue
   sf=choices[0];q=source['new_uv'][sf['id']];target['new_uv'][f['id']]=np.array([q[sf['indices'].index(j)] for j in idx]);target['mat'][f['id']]=source['mat'][sf['id']];count+=1
  if count<len(target['faces']):affine_cleanup(pair,target)
  log.append(dict(file=pair,part=target['part'],lod=target['lod'],repair='reuse in-flight UVs and materials',matched_faces=count,total_faces=len(target['faces']),source=name))
wrap=make_wrap(D,uvname)
nozzle=make_nozzle(D,uvname)
for key,m in data.items():
 o=objs[key];layer=o.data.uv_layers[uvname]
 if key[0].startswith(('01_screamer.','21_screamer.')):
  o.data.materials.append(wrap);wrap_slot=len(o.data.materials)-1
 if any(x==2 for x in m['mat'].values()):o.data.materials.append(nozzle);nozzle_slot=len(o.data.materials)-1
 for f in m['faces']:
  p=o.data.polygons[f['id']]
  for li in p.loop_indices:
   u,v=m['new_uv'][f['id']][o['native_corner_order'][li]];layer.data[li].uv=(u,1-v)
  if m['mat'][f['id']]==1:p.material_index=wrap_slot
  elif m['mat'][f['id']]==2:p.material_index=nozzle_slot
 o['native_standalone_triangles']=key[0] not in protected
bpy.context.scene['asset']='Missile Packs, Torpedoes and Fuel Pod - audit v2';bpy.context.scene['active_delivery_uv']=uvname;bpy.context.scene['audit_notes']='Corrected in-flight models reused in loadout; legacy fan/strip export groups split to preserve edited per-corner UVs. Original positions, normals, metadata, animation and all LODs retained. Seven approved models untouched in runtime. Engine controls loadout tint. Emissives deferred; release held.'
bpy.context.scene.render.bake.margin=16;bpy.context.scene.cycles.samples=24;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(D/'ordnance_worn_audit_v2.blend'),compress=True)
(W/'uv_repairs.json').write_text(json.dumps(log,indent=2));print('AUDIT_V2_SAVED',len(log),flush=True)
