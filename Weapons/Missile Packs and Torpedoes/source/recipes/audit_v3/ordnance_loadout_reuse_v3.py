"""Reuse flight repairs on corresponding loadout faces without changing native geometry."""
import os
import bpy,numpy as np,json,sys
from pathlib import Path
D=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve();W=D/'work/audit_v3';UV='Ordnance_Delivery_UV_v3'
bpy.ops.wm.open_mainfile(filepath=str(D/'ordnance_worn_audit_v3_baked.blend'));bpy.context.view_layer.update();snap=json.loads((W/'snapshot.json').read_text());obs={(o['native_model'],int(o['native_part']),int(o['native_lod'])):o for o in bpy.data.objects if o.type=='MESH' and o.get('native_model')};logs=[]
# Coarse native LODs can join more than one cylinder facet in a triangle.
# Retain their established mapping wherever an LOD0-based projection would collapse it.
sys.path.insert(0,str(W));import ordnance_native as native
for (name,part,lod),o in obs.items():
 if name not in snap['change_flight'] or lod==0 or 'pod' in name.lower():continue
 restored=[];vv=np.array([v.co[:] for v in o.data.vertices]);new=o.data.uv_layers[UV];old=o.data.uv_layers['Ordnance_Delivery_UV_v2']
 for p in o.data.polygons:
  xyz=vv[list(p.vertices)];q=np.array([new.data[l].uv[:] for l in p.loop_indices]);base=np.array([old.data[l].uv[:] for l in p.loop_indices])
  if native.ratio(xyz,q)>max(12,native.ratio(xyz,base)*1.1):
   for l in p.loop_indices:new.data[l].uv=old.data[l].uv
   restored.append(p.index)
 if restored:logs.append(dict(file=name,lod=lod,repair='retain established nondegenerate mapping on coarse spanning triangles',faces=restored))
# The restored top needs an uninterrupted steel sample, clear of the atlas panel edges.
for (name,part,lod),o in obs.items():
 if name!='fuel_pod.SHP':continue
 ids=list(o.get('native_visible_cap_faces',[]));vv=np.array([v.co[:] for v in o.data.vertices]);verts=sorted({i for f in ids for i in o.data.polygons[f].vertices});xy=vv[verts][:,[0,2]];lo,hi=xy.min(0),xy.max(0);scale=min(56/(hi[0]-lo[0]),105/(hi[1]-lo[1]));q=(xy-(lo+hi)/2)*scale+[663,193.5];lookup=dict(zip(verts,q/1254))
 for f in ids:
  for li in o.data.polygons[f].loop_indices:
   u,v=lookup[o.data.loops[li].vertex_index];o.data.uv_layers[UV].data[li].uv=(u,1-v)
for name,pair in snap['loadout_pairs'].items():
 for (file,part,lod),target in obs.items():
  if file!=pair:continue
  candidates=[o for (f,p,l),o in obs.items() if f==name and l==lod]
  if not candidates:continue
  src=candidates[0];sv=np.array([v.co[:] for v in src.data.vertices]);tv=np.array([v.co[:] for v in target.data.vertices]);mapping={}
  if 'pod' not in name.lower() and len(sv)==len(tv):mapping={i:i for i in range(len(tv))}
  else:
   best=None
   for signs in [(1,1,1),(-1,-1,1),(-1,1,1),(1,-1,1)]:
    vv=sv*np.array(signs);scale=np.ptp(tv[:,2])/max(np.ptp(vv[:,2]),1e-9);delta=(tv.min(0)+tv.max(0))/2-(vv.min(0)+vv.max(0))/2*scale;dist=np.linalg.norm(tv[:,None,:]-(vv*scale+delta)[None,:,:],axis=2);near=dist.argmin(1);err=dist.min(1);score=sum(err<.005*max(np.ptp(tv,axis=0)))
    if best is None or score>best[0]:best=(score,near,err,signs)
   mapping={i:int(j) for i,(j,e) in enumerate(zip(best[1],best[2])) if e<.005*max(np.ptp(tv,axis=0))}
  lookup={}
  for f in src.data.polygons:lookup.setdefault(tuple(sorted(f.vertices)),[]).append(f)
  count=0;visible=[];suppress=set(target.get('native_suppressed_duplicate_faces',[]));source_visible=set(src.get('native_visible_cap_faces',[]))
  for p in target.data.polygons:
   if p.index in suppress:continue
   if not all(i in mapping for i in p.vertices):continue
   idx=[mapping[i] for i in p.vertices];choices=lookup.get(tuple(sorted(idx)))
   if not choices:continue
   sf=choices[0];suv={src.data.loops[l].vertex_index:src.data.uv_layers[UV].data[l].uv[:] for l in sf.loop_indices}
   for l in p.loop_indices:target.data.uv_layers[UV].data[l].uv=suv[mapping[target.data.loops[l].vertex_index]]
   mat=src.data.materials[sf.material_index]
   if mat.name not in target.data.materials:target.data.materials.append(mat)
   p.material_index=target.data.materials.find(mat.name)
   if sf.index in source_visible:visible.append(p.index)
   count+=1
  if visible:target['native_visible_cap_faces']=visible
  logs.append(dict(file=pair,part=part,lod=lod,source=name,matched_faces=count,total_faces=len(target.data.polygons),suppressed=list(suppress),restored_top_faces=visible))
# The display fuel pod has a different simplified mesh at LOD1; restore its matching cap directly.
for (name,part,lod),o in obs.items():
 if name!='31_fuel_pod.SHP' or lod!=1:continue
 ids=[p.index for p in o.data.polygons if p.normal.y<-.9 and o.data.materials[p.material_index].name=='Original hidden damage caps']
 assert ids==[48,49],ids
 vv=np.array([v.co[:] for v in o.data.vertices]);verts=sorted({i for f in ids for i in o.data.polygons[f].vertices});xy=vv[verts][:,[0,2]];lo,hi=xy.min(0),xy.max(0);scale=min(56/(hi[0]-lo[0]),105/(hi[1]-lo[1]));q=(xy-(lo+hi)/2)*scale+[663,193.5];lookup=dict(zip(verts,q/1254))
 o['native_visible_cap_faces']=ids
 for f in ids:
  p=o.data.polygons[f];p.material_index=0
  for li in p.loop_indices:
   u,v=lookup[o.data.loops[li].vertex_index];o.data.uv_layers[UV].data[li].uv=(u,1-v)
 logs.append(dict(file=name,lod=lod,repair='display-only simplified top cap restored with shared steel projection',restored_top_faces=ids))
for (name,part,lod),o in obs.items():o.hide_render=bool(lod);o.hide_set(bool(lod))
(W/'loadout_reuse.json').write_text(json.dumps(logs,indent=2));bpy.context.scene['asset']='Missile Packs, Torpedoes and Fuel Pod - audit v3';bpy.context.scene['audit_notes']='Second user audit: seven corrected families reused in loadout; nine approved families preserved. All native geometry, custom normals, attachments, animations and LODs retained. Existing fuel top cap restored. Release held for user visual review.';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'ordnance_worn_audit_v3.blend'),compress=True);print('AUDIT_V3_SAVED',len(logs),flush=True)
