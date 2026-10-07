from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
D=Path(__file__).resolve().parents[2];W=D/'work/seams_v3';state=json.loads((W/'prior_project_state.json').read_text());bpy.ops.wm.open_mainfile(filepath=state['latest_scene']);s=bpy.context.scene;bpy.context.view_layer.update();obs=[o for o in s.objects if o.type=='MESH'];new='Naginata_Aligned_UV_v3'
def sig():return hashlib.sha256(json.dumps({o.name:{'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'normals':[list(n.vector) for n in o.data.corner_normals],'matrix':[list(r) for r in o.matrix_world],'original_uv':[list(q.uv) for q in o.data.uv_layers['Original_Naginata_UV'].data]} for o in obs},sort_keys=True).encode()).hexdigest()
before=sig();groups=[]
for o in obs:
 old=[tuple(q.uv) for q in o.data.uv_layers.active.data];layer=o.data.uv_layers.new(name=new)
 for a,b in zip(layer.data,old):a.uv=b
 o.data.uv_layers.active=layer;layer.active_render=True
body=bpy.data.objects['Naginata_Body'];m=body.data;uv=m.uv_layers[new];verts=[body.matrix_world@v.co for v in m.vertices];original={p.index:[list(uv.data[i].uv) for i in p.loop_indices] for p in m.polygons}
def loop(fi,vi):return m.polygons[fi].loop_indices[list(m.polygons[fi].vertices).index(vi)]
def get(fi,vi):q=uv.data[loop(fi,vi)].uv;return Vector((q.x*1254,(1-q.y)*1254))
def put(fi,vi,q):uv.data[loop(fi,vi)].uv=(q[0]/1254,1-q[1]/1254)
mirror={i:min(range(len(verts)),key=lambda j:(verts[j]-Vector((-v.x,v.y,v.z))).length) for i,v in enumerate(verts)};byset={frozenset(p.vertices):p.index for p in m.polygons}
def mirror_faces(fs):
 others=[]
 for fi in fs:
  p=m.polygons[fi];other=byset[frozenset(mirror[v] for v in p.vertices)];others.append(other)
  for v in p.vertices:put(other,mirror[v],get(fi,v))
 return others
def rec(name,fs,mir=False):groups.append({'name':name,'object':body.name,'faces':sorted(set(fs+(mirror_faces(fs) if mir else [])))})
def unfold(base,child):
 a,b=sorted(set(m.polygons[base].vertices)&set(m.polygons[child].vertices));c=next(i for i in m.polygons[base].vertices if i not in [a,b]);d=next(i for i in m.polygons[child].vertices if i not in [a,b]);e=verts[b]-verts[a];l=e.length;t=e/l;vc=verts[c]-verts[a];vd=verts[d]-verts[a];sc=vc.dot(t);sd=vd.dot(t);hc=(vc-t*sc).length;hd=(vd-t*sd).length;qa,qb,qc=get(base,a),get(base,b),get(base,c);step=(qb-qa)/l;perp=(qc-qa-step*sc)/hc;qd=qa+step*sd-perp*hd
 for v,q in [(a,qa),(b,qb),(d,qd)]:put(child,v,q)
# Preserve main nose/engine UVs for the local composite bake; only the thin nose side bevel is unfolded.
unfold(25,30);unfold(30,31);rec('Nose side bevel continuation',[30,31],True)
# One projection around upper-fin livery and aperture edges. A subpixel thickness term avoids collapsed tangents on the thin edge faces.
for fi in range(206,246):
 if m.polygons[fi].material_index:continue
 for vi in m.polygons[fi].vertices:
  x,y,z=verts[vi];put(fi,vi,(1447.7+582.6*y+(abs(x)-(.802-.282*z))*3,374.9-544.5*z))
rec('Upper fin livery and opening-wall registration',list(range(206,246)),True)
# Lower fins retain the original steel/bronze chart split, with shared coordinates around each blade and its opening walls.
for fi in range(246,276):
 if m.polygons[fi].material_index:continue
 for vi in m.polygons[fi].vertices:
  x,y,z=verts[vi];thin=(abs(x)-(.802+.214*z))*3
  if 264<=fi<=270:q=(8+.82*(567.604849+582.593998*y+14)+thin,713.691091-544.480384*z)
  else:q=(1146.64603+539.439285*y+thin,8.38151964-544.480433*z)
  put(fi,vi,q)
rec('Lower fin blades and aperture-wall registration',list(range(246,276)),True)
# Cockpit perimeter follows the longitudinal coordinates of the hull side. The actual glass/frame faces are excluded.
cp=bpy.data.objects['Naginata_c-pit'];cm=cp.data;cu=cm.uv_layers[new]
# Fit u to the hull's top-edge end anchors; the frame has a solid strip of steel inside this border.
a=verts[18];b=verts[46];qa=get(5,18);qb=get(5,46)
for fi in range(28,36):
 for li in cm.polygons[fi].loop_indices:
  v=cp.matrix_world@cm.vertices[cm.loops[li].vertex_index].co;t=(v.y-a.y)/(b.y-a.y);u=qa.x+t*(qb.x-qa.x);outer_x=abs(a.x)+t*(abs(b.x)-abs(a.x));edge_v=qa.y+t*(qb.y-qa.y);vv=edge_v+max(0,outer_x-abs(v.x))*520;cu.data[li].uv=(u/1254,1-vv/1254)
groups.append({'name':'Cockpit perimeter lines registered to hull sides','object':cp.name,'faces':list(range(28,36))})
# Close minor vertex quantisation gaps using connected-loop components, preserving full-tile wrap offsets.
joined=[]
for o in obs:
 mesh=o.data;layer=mesh.uv_layers[new];edges={};parent=list(range(len(layer.data)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def lid(fi,v):p=mesh.polygons[fi];return p.loop_indices[list(p.vertices).index(v)]
 for f in mesh.polygons:
  if f.material_index:continue
  for a,b in zip(f.vertices,list(f.vertices[1:])+[f.vertices[0]]):edges.setdefault(tuple(sorted((a,b))),[]).append(f.index)
 for edge,ff in edges.items():
  if len(ff)!=2:continue
  qs=[[layer.data[lid(f,v)].uv.copy() for v in edge] for f in ff];sh=[Vector((round(a.x-b.x),round(a.y-b.y))) for a,b in zip(*qs)];ds=[(a-b-z).length*1254 for a,b,z in zip(*qs,sh)]
  if (sh[0]-sh[1]).length<1e-8 and max(ds)<7.5:
   for v in edge:parent[root(lid(ff[1],v))]=root(lid(ff[0],v))
   if max(ds)>.01:joined.append({'object':o.name,'faces':ff,'pixel_gap_before':ds})
 sets={}
 for i in range(len(parent)):sets.setdefault(root(i),[]).append(i)
 for ids in sets.values():
  if len(ids)<2:continue
  first=layer.data[ids[0]].uv.copy();qs=[layer.data[i].uv.copy() for i in ids];sh=[Vector((round(first.x-q.x),round(first.y-q.y))) for q in qs];avg=sum((q+z for q,z in zip(qs,sh)),Vector((0,0)))/len(ids)
  for i,z in zip(ids,sh):layer.data[i].uv=avg-z
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   if hasattr(n,'uv_map') and n.uv_map=='Naginata_Atlas_UV_v1':n.uv_map=new
assert sig()==before
report={'source_scene':state['latest_scene'],'scene':str(D/'naginata_worn_aligned_v3.blend'),'original_geometry_normals_uv_preserved':True,'geometry_signature':before,'active_uv':new,'groups':groups,'minor_joins':joined,'models':{}}
for o in obs:
 report['models'][o.name]={'vertices':[list(v.co) for v in o.data.vertices],'faces':[{'id':p.index,'vertices':list(p.vertices),'uv':[list(o.data.uv_layers[new].data[i].uv) for i in p.loop_indices],'material':p.material_index} for p in o.data.polygons]}
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=report['scene']);(W/'repair_report.json').write_text(json.dumps(report,indent=2));print('UV_REPAIR_SAVED',len(groups),len(joined),flush=True)
