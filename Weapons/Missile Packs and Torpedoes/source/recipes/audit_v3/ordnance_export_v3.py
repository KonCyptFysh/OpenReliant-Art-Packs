"""Portable audit exporter. Preserve original geometry, metadata, animation and LODs.
Edited per-corner UVs must not be coalesced by native fan/strip continuation.
Usage: blender -b --python ordnance_export_v2.py -- SCENE NATIVE OUTPUT
"""
import bpy,sys,json,struct,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent));import ordnance_native as n
scene,native,out=map(Path,sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(scene));out.mkdir(parents=True,exist_ok=True);bpy.context.view_layer.update();records=[]
for file in sorted(native.glob('*.SHP')):
 raw=file.read_bytes();parts=n.models(raw);objects={};names={'orord1_hull'};standalone=False
 for p in parts:
  found=[o for o in bpy.data.objects if o.type=='MESH' and o.get('native_model')==file.name and o.get('native_part')==p['part'] and o.get('native_lod')==p['lod']];assert len(found)==1;(o,)=found;mesh=o.data;objects[p['part'],p['lod']]=o;standalone|=bool(o.get('native_standalone_triangles',False))
  assert np.array_equal(np.array([list(v.co) for v in mesh.vertices]),p['verts']),'Native positions changed';assert len(mesh.polygons)==len(p['faces']);assert np.array_equal(np.array([list(v.vector) for v in mesh.attributes['NativeVertexNormal'].data]),p['normals'])
  assert all(np.linalg.norm(np.array(v.vector)-base.vector)<1e-6 for v,base in zip(mesh.corner_normals,mesh.attributes['ImportedCornerNormal'].data)),'Custom normals changed'
  p['new_uv']={};p['materials']={};uv=mesh.uv_layers['Ordnance_Delivery_UV_v3'];orders=o['native_corner_order']
  for f in p['faces']:
   poly=mesh.polygons[f['id']];qs=np.zeros((3,2));assert len(poly.vertices)==3
   for k,li in enumerate(poly.loop_indices):
    corner=orders[li];assert poly.vertices[k]==f['indices'][corner],'Topology changed';u,v=uv.data[li].uv;qs[corner]=(u,1-v)
   assert np.isfinite(qs).all();p['new_uv'][f['id']]=np.array(f['uv']) if np.max(np.abs(qs-np.array(f['uv'])))<1e-7 else qs
   mat=mesh.materials[poly.material_index];mn=mat.get('native_material','orord1_hull');p['materials'][f['id']]=mn;names.add(mn)
 names=['orord1_hull']+sorted(names-{'orord1_hull'});lookup={(p['part'],p['lod']):p for p in parts};output=[];changed=0;split=0;swaps=0;anis=[]
 for c in n.chunks(raw):
  tag,size,count=c['tag'],c['size'],c['count'];data=bytearray(c['data'])
  if tag==6:
   assert size==64;count=len(names);data=b''.join(x.encode().ljust(64,b'\0') for x in names)
  elif tag==3:
   p=lookup[c['part'],c['lod']]
   for f in p['faces']:
    off=f['id']*size;qs=p['new_uv'][f['id']].copy();idx=f['indices'].copy();old=bytes(data[off:off+size]);struct.pack_into('<I',data,off,names.index(p['materials'][f['id']]))
    suppressed=set(objects[p['part'],p['lod']].get('native_suppressed_duplicate_faces',[]))
    visible=set(objects[p['part'],p['lod']].get('native_visible_cap_faces',[]))
    if f['id'] in visible:struct.pack_into('<I',data,off+8,struct.unpack_from('<I',data,off+8)[0]&~1)
    if f['id'] in suppressed:struct.pack_into('<I',data,off+8,struct.unpack_from('<I',data,off+8)[0]|1)
    if standalone and size>=80:
     if f['fan']==3:
      idx[1],idx[2]=idx[2],idx[1];qs[[1,2]]=qs[[2,1]];swaps+=1
      edge=struct.unpack_from('<I',data,off+68)[0];edge=(edge&~7)|((edge&1)<<2)|(edge&2)|((edge&4)>>2);struct.pack_into('<I',data,off+68,edge)
     split+=int(f['fan']!=0);struct.pack_into('<II',data,off+72,0,0)
    struct.pack_into('<3I',data,off+12,*idx);struct.pack_into('<6f',data,off+24,*qs[:,0],*qs[:,1]);changed+=int(old[24:48]!=bytes(data[off+24:off+48]));r=n.ratio(np.array(p['verts'])[idx],qs);anis.append(r)
    allowed=set(range(0,4))|set(range(12,48))
    if f['id'] in suppressed or f['id'] in visible:allowed|=set(range(8,12))
    if standalone and size>=80:allowed|=set(range(68,80))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(old,data[off:off+size])))
    # The effective triangle winding is identical to the original fan/strip.
    effective=f['indices'].copy()
    if f['fan']==3:effective[1],effective[2]=effective[2],effective[1]
    current=idx.copy()
    if not standalone and f['fan']==3:current[1],current[2]=current[2],current[1]
    assert effective==current
  output.append(struct.pack('<HHH',tag,size,count)+data)
 result=b''.join(output);dest=out/file.name;dest.write_bytes(result)
 # Every chunk other than faces/material names is byte-exact, including all vertices.
 for a,b in zip(n.chunks(raw),n.chunks(result)):
  assert a['tag']==b['tag']
  if a['tag'] not in (3,6):assert a['data']==b['data']
 records.append(dict(file=file.name,sha256=n.sha(dest),source_sha256=n.sha(file),part_lods=len(parts),triangles=sum(len(p['faces']) for p in parts),changed_uv_records=changed,split_group_records=split,preserved_winding_swaps=swaps,standalone_triangles=standalone,suppressed_duplicate_faces=[dict(part=p['part'],lod=p['lod'],faces=list(objects[p['part'],p['lod']].get('native_suppressed_duplicate_faces',[]))) for p in parts if objects[p['part'],p['lod']].get('native_suppressed_duplicate_faces')],materials=names,max_uv_anisotropy=max(anis),positions_normals_metadata_attachments_animation_lods_byte_exact=True,effective_triangle_winding_preserved=True))
(out/'scene_export.json').write_text(json.dumps(records,indent=2));print('AUDIT_V3_EXPORT_COMPLETE',len(records),flush=True)
