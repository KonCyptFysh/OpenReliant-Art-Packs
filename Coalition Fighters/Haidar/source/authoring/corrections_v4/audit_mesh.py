import os
from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
D=Path(os.environ['HAIDAR_WORKSPACE']);W=D/'work/corrections_v4';R=D/'review/corrections_v4'
bpy.ops.wm.open_mainfile(filepath=str(D/'haidar_worn_pbr_v3.blend'));s=bpy.context.scene;obs=[o for o in s.objects if o.type=='MESH'];uvname='Haidar_Delivery_UV_v3'
edges={};faces=[]
for o in obs:
 m=o.data
 for p in m.polygons:
  if p.material_index:continue
  xyz=np.array([m.vertices[v].co[:] for v in p.vertices]);uv=np.array([m.uv_layers[uvname].data[i].uv[:] for i in p.loop_indices])*[1254,-1254]+[0,1254]
  area=np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))/2
  faces.append(dict(part=o.name,face=p.index,vertices=list(p.vertices),xyz=xyz.tolist(),uv=uv.tolist(),area=float(area)))
  for i,j in [(0,1),(1,2),(2,0)]:
   a=tuple(np.round(xyz[i],1));b=tuple(np.round(xyz[j],1));key=tuple(sorted((a,b)));ix=[i,j] if a==key[0] else [j,i]
   edges.setdefault(key,[]).append(dict(part=o.name,face=p.index,vertices=[int(p.vertices[k]) for k in ix],uv=uv[ix].tolist(),third=uv[3-i-j].tolist()))
joins=[]
for xyz,ff in edges.items():
 if len(ff)!=2:continue
 a,b=[np.array(f['uv']) for f in ff];gap=np.linalg.norm(a-b,axis=1)
 if max(gap)>.01:joins.append(dict(xyz=xyz,faces=ff,gaps=gap.tolist(),length=float(np.linalg.norm(np.subtract(*xyz)))))
(W/'mesh_audit.json').write_text(json.dumps(dict(faces=faces,joins=joins),indent=2))
for name in ['Han_Body','Han_Cockpit','Han_Right_Wing']:
 print(name,flush=True)
 for f in faces:
  if f['part']!=name or f['area']<2000:continue
  print(f['face'],'xyz',np.round(f['xyz'],1).tolist(),'uv',np.round(f['uv'],1).tolist(),flush=True)
cam=bpy.data.objects['Cockpit'];cam.data.type='ORTHO';cam.data.ortho_scale=2.25;s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=1000;s.cycles.samples=16
target=bpy.data.objects['Han_Body'].matrix_world@Vector((0,-10,5))
for name,off in [('body_right',(3,.4,1.8)),('body_roof',(.1,0,4)),('body_belly',(2.2,.4,-2.6))]:
 cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/(name+'_before.png'));bpy.ops.render.render(write_still=True)
 if name=='body_right':
  mat=bpy.data.materials.new('Audit labels');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(1,.23,.025,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs[0]);labels=[]
  for o in obs:
   if o.name!='Han_Body':continue
   for p in o.data.polygons:
    if p.material_index:continue
    centre=o.matrix_world@p.center;normal=o.matrix_world.to_3x3()@p.normal
    if normal.dot(cam.location-centre)<0 or p.area<1800:continue
    data=bpy.data.curves.new('face label','FONT');data.body=str(p.index);data.align_x='CENTER';data.align_y='CENTER';data.size=.035
    label=bpy.data.objects.new('label',data);s.collection.objects.link(label);label.location=centre+(cam.location-centre).normalized()*.015;label.rotation_euler=cam.rotation_euler;data.materials.append(mat);labels.append(label)
  s.render.filepath=str(R/(name+'_face_ids.png'));bpy.ops.render.render(write_still=True)
  for label in labels:bpy.data.objects.remove(label,do_unlink=True)
print('AUDIT_COMPLETE',flush=True)
