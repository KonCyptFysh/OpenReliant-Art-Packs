import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parents[2];W=D/'recipes/reconstruction_v1';state={'latest_scene':str(D/'crusader_source_review.blend')};bpy.ops.wm.open_mainfile(filepath=state['latest_scene']);bpy.context.view_layer.update();out={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 m=o.data;verts=np.array([list(o.matrix_world@v.co) for v in m.vertices]);faces=[]
 for p in m.polygons:
  pp=verts[list(p.vertices)];e=pp[1:]-pp[0];norm=np.cross(*e);area=np.linalg.norm(norm)/2;norm/=max(np.linalg.norm(norm),1e-10);uvs={u.name:[list(u.data[i].uv) for i in p.loop_indices] for u in m.uv_layers};q=np.array(uvs[m.uv_layers.active.name]);q=q[1:]-q[0];t=np.stack((e[0]/max(np.linalg.norm(e[0]),1e-10),np.cross(norm,e[0]/max(np.linalg.norm(e[0]),1e-10))),axis=1);local=e@t;sing=np.linalg.svd(np.linalg.solve(local,q),compute_uv=False) if abs(np.linalg.det(local))>1e-10 else [1,0]
  faces.append({'id':p.index,'vertices':list(p.vertices),'material':p.material_index,'center':pp.mean(0).tolist(),'normal':norm.tolist(),'area':float(area),'uv_aspect':float(sing[0]/max(sing[-1],1e-12)),'texel_density':float(np.sqrt(abs(np.linalg.det(q))/max(2*area,1e-12))*4096),'uvs':uvs})
 out[o.name]={'vertices':verts.tolist(),'local_vertices':[list(v.co) for v in m.vertices],'matrix':[list(row) for row in o.matrix_world],'materials':[a.name for a in m.materials],'faces':faces}
(W/'mesh_original.json').write_text(json.dumps(out,indent=2));(W/'prior_project_state.json').write_text(json.dumps(state,indent=2));print('SOURCE',state['latest_scene'],hashlib.sha256(Path(state['latest_scene']).read_bytes()).hexdigest())
for name,obj in out.items():
 print('OBJECT',name)
 for f in obj['faces']:
  if f['material']==0 and f['uv_aspect']>4:print('FACE',f['id'],'v',f['vertices'],'xyz',np.round(f['center'],3).tolist(),'n',np.round(f['normal'],2).tolist(),'aspect',round(f['uv_aspect'],1),'uv',f['uvs'][list(f['uvs'])[-1]])
