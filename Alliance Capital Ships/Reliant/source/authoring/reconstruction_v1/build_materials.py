from pathlib import Path
import bpy,numpy as np,json,hashlib,math
from mathutils import Vector
D=Path('${RELIANT_WORKSPACE}');W=D/'work/reconstruction_v1';M=D/'maps';N=1254;OUT=4096
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_source_review.blend'));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH'];before={o.name:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],{u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers}) for o in obs}
yy,xx=np.mgrid[:N,:N].astype(np.float32);X=(xx+.5)*256/N;Y=(yy+.5)*256/N

def smooth(a,b,z):
 t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def capsule(a,b,r):
 v=np.subtract(b,a);t=np.clip(((X-a[0])*v[0]+(Y-a[1])*v[1])/max(np.dot(v,v),1e-10),0,1);return r-np.hypot(X-a[0]-t*v[0],Y-a[1]-t*v[1])
def box(a,b,c,d):return np.minimum.reduce([X-a,c-X,Y-b,d-Y])
# Coordinates are hand traced against the native 256px atlases. No diffuse-to-height.
R={1:{'flat':[(1,81,93,103),(6,203,97,207),(6,239,97,244),(119,69,123,146),(239,0,256,17),(116,28,129,40)],
'lines':[(6,59,6,192),(25,59,25,80),(59,59,59,80),(72,59,72,191),(93,0,93,255),(114,40,114,153),(158,40,158,192),(93,61,114,61),(93,106,114,106),(93,136,114,136),(107,27,107,55),(6,191,96,191),(6,201,96,201),(6,214,96,214),(6,224,96,224),(6,233,96,233),(126,86,155,86),(126,101,155,101),(126,109,155,109),(126,130,155,130),(126,146,155,146),(161,67,178,67),(161,80,178,80),(161,93,178,93),(161,106,178,106),(6,108,70,108),(6,116,70,116),(22,110,22,187),(22,154,70,154),(30,81,30,103),(28,194,28,202),(55,194,55,202),(82,194,82,202),(114,192,114,255),(148,193,148,255),(220,193,220,255)],
'slots':[(15,30,78,30,3.8),(15,48,78,48,3.8),(15,146,78,146,4.8),(133,106,150,106,1.3),(133,132,150,132,1.3)],
'ribs':[(119,5,227,26,'y',4.1),(181,54,193,126,'y',5.5),(218,196,247,204,'x',2.0),(149,196,218,201,'x',1.4),(41,61,49,78,'y',1.5),(173,110,178,130,'y',1.8),(161,112,166,129,'y',1.8),(129,28,152,40,'x',4)],
'circles':[(107,14,11),(144,49,4.2),(156,49,4.2)],'window_rois':[],'white':[(34,195,38,199),(64,195,68,199),(34,248,38,252),(64,248,68,252),(185,182,188,185)],
'red':[(8,34,11,38),(81,34,84,38),(149,77,152,80),(149,88,152,91),(149,124,152,127),(149,136,152,139),(110,161,113,165),(153,161,156,165),(110,181,113,184),(131,181,134,184),(153,181,156,184),(107,194,110,197),(107,199,110,202),(107,246,110,249),(107,251,110,254),(250,194,253,197),(250,199,253,202),(250,246,253,249),(250,251,253,254),(250,151,253,155),(250,156,253,159),(250,172,253,175),(250,176,253,179)]},
2:{'flat':[(65,76,99,126),(44,145,51,184)],
'lines':[(27,3,27,130),(27,132,27,255),(44,3,44,255),(51,71,51,255),(64,71,64,255),(101,0,101,255),(106,57,256,57),(106,68,256,68),(106,78,256,78),(106,85,147,85),(106,112,256,112),(106,124,256,124),(106,148,256,148),(106,177,256,177),(106,197,256,197),(106,212,256,212),(106,240,256,240),(143,177,143,256),(198,68,198,120),(210,21,210,57),(235,21,235,68),(209,92,209,118),(65,142,99,142),(65,156,99,156),(65,180,99,180),(65,234,99,234),(65,250,99,250),(65,193,99,193),(65,204,99,204),(65,217,99,217),(75,180,75,234),(86,180,86,234),(34,21,34,53),(34,146,34,181),(34,217,34,254),(147,68,147,111),(171,85,171,111),(123,85,123,111),(169,201,169,239),(204,201,204,239)],
'slots':[],
'ribs':[(23,6,27,16,'y',1),(48,15,56,24,'y',1.3),(58,15,71,24,'y',1.3),(78,16,85,26,'y',1.3),(103,26,109,33,'y',2),(103,46,109,53,'y',2),(22,99,26,113,'y',1.2),(47,220,50,242,'y',1.3),(177,213,181,235,'y',1.2),(186,213,190,235,'y',1.2),(215,2,250,17,'y',3)],
'circles':[(182,9,4),(193,9,4)],
'window_rois':[(4,7,24,17),(4,23,24,54),(4,62,24,100),(4,107,24,123),(4,134,24,143),(4,148,24,179),(4,186,24,226),(4,234,24,250),(49,6,84,11),(50,38,68,65),(77,38,94,65),(120,23,138,35),(151,23,177,35),(190,24,200,35),(119,42,140,54),(150,42,177,54)],
'white':[(35,26,38,29),(35,99,38,102),(35,152,38,155),(35,189,38,192),(35,224,38,227),(120,131,123,134),(156,131,159,134),(193,131,196,134),(232,131,235,134),(128,243,131,246),(182,243,185,246),(229,243,232,246)],
'red':[(67,151,71,154),(94,151,98,154),(67,173,71,176),(94,173,98,176),(67,244,71,247),(94,244,98,247)]},
3:{'flat':[(189,1,255,67),(157,67,162,142),(206,171,220,256),(114,83,138,86),(114,86,117,101),(135,86,138,101),(114,100,138,103)],
'lines':[(53,57,53,256),(86,0,86,256),(100,67,100,256),(143,67,143,143),(164,67,164,143),(183,0,183,256),(195,0,195,256),(222,68,222,150),(251,0,251,256),(61,30,85,30),(61,44,85,44),(53,58,85,58),(53,75,85,75),(53,90,85,90),(53,96,85,96),(53,111,85,111),(61,114,85,114),(61,127,85,127),(53,144,86,144),(53,157,86,157),(53,170,86,170),(53,185,86,185),(53,191,86,191),(53,207,86,207),(53,222,86,222),(53,237,86,237),(106,104,139,104),(106,112,139,112),(106,120,139,120),(106,142,156,142),(109,158,139,158),(109,171,139,171),(109,186,140,186),(188,150,251,150),(188,161,251,161),(188,170,251,170),(31,8,31,30),(45,8,45,30),(5,59,49,59),(5,70,49,70),(5,85,49,85),(5,94,49,94)],
'slots':[(99,33,170,33,4.5),(99,55,170,55,4.5),(120,91,133,91,4),(109,125,109,134,4),(129,125,129,134,4)]+[(233,y,243,y,2.4) for y in (82,94,106,118,129,141)],
'ribs':[(9,132,47,185,'x',4),(9,192,47,246,'x',4),(224,173,245,199,'x',4),(224,202,245,227,'x',4),(54,113,59,142,'y',1.3),(54,146,59,167,'y',1.3),(54,174,59,185,'y',1.3),(54,236,59,251,'y',1.3),(87,126,100,141,'y',1.4),(140,126,151,141,'y',1.4),(150,81,156,93,'y',1.2),(114,223,144,232,'x',3),(150,222,159,232,'y',2)],
'circles':[(24,12,3.7),(50,12,3.7),(24,22,3.7),(50,22,3.7),(114,164,3.3),(124,164,3.3),(134,164,3.3)],'window_rois':[],'white':[],
'red':[(20,3,24,6),(51,3,55,6),(149,152,152,156),(154,152,158,156),(149,174,152,177),(154,174,158,177),(110,215,114,219),(110,220,114,223),(110,235,114,238),(110,240,114,243)]}}
(W/'regions.json').write_text(json.dumps({'native_atlas_size':256,'regions':R,'policy':'Explicit native structural regions only. Windows restricted to existing REL_2 amber clusters; painted stripes and ship name flat.'},indent=2)+'\n')
records={};materials={}
for i,r in R.items():
 im=bpy.data.images.load(str(M/f'reliant_rel{i}_reconstructed_v1.png'));im.colorspace_settings.name='Non-Color';assert tuple(im.size)==(N,N);buf=np.empty(N*N*4,np.float32);im.pixels.foreach_get(buf);rgb=buf.reshape(N,N,4)[::-1,:,:3].copy();bpy.data.images.remove(im)
 h=np.zeros((N,N),np.float32);flat=h.copy();structure=h.copy();fins=h.copy();pan=h.copy();glass=h.copy();emit=np.zeros_like(rgb)
 for b in r['flat']:flat=np.maximum(flat,smooth(0,.35,box(*b)))
 for a,b,c,d,rad in r['slots']:
  dist=capsule((a,b),(c,d),rad);mask=smooth(0,.4,dist);h-=1.2*smooth(0,1,dist);structure=np.maximum(structure,mask)
 for cx,cy,rad in r['circles']:
  dist=rad-np.hypot(X-cx,Y-cy);mask=smooth(0,.4,dist);h=h*(1-mask)-.85*smooth(0,.9,dist)*mask;structure=np.maximum(structure,mask)
 for a,b,c,d,axis,pitch in r['ribs']:
  dist=box(a,b,c,d);mask=smooth(0,.35,dist);p=X-a if axis=='x' else Y-b
  rib=(1-smooth(.18,.6,np.abs((p+pitch/2)%pitch-pitch/2)))*smooth(.5,1,dist)
  h=h*(1-mask)+(-1*smooth(0,.9,dist)+.65*rib)*mask;structure=np.maximum(structure,mask);fins=np.maximum(fins,rib)
 for a,b,c,d in r['lines']:pan=np.maximum(pan,smooth(0,.28,capsule((a,b),(c,d),.40)))
 pan*=1-np.maximum(flat,structure);h-=.42*pan;h*=1-flat
 for b in r['window_rois']:
  roi=smooth(0,.3,box(*b));lit=smooth(.35,.70,rgb[:,:,0])*smooth(.20,.42,rgb[:,:,1])*smooth(.06,.18,rgb[:,:,0]-rgb[:,:,2]);glass=np.maximum(glass,roi*lit)
 # Glow and recess share exactly the same mask; frames remain metal. No global bright-pixel selection.
 h=h*(1-glass)-.9*glass;emit+=glass[:,:,None]*np.array([.62,.40,.16])
 for b in r['white']:
  m=smooth(0,.2,box(*b))*smooth(.50,.83,rgb.min(-1));emit+=m[:,:,None]*np.array([.29,.30,.26])
 for b in r['red']:
  m=smooth(0,.2,box(*b))*smooth(.17,.42,rgb[:,:,0]-rgb[:,:,1]);emit+=m[:,:,None]*np.array([.48,.018,.005])
 mx=rgb.max(-1);mn=rgb.min(-1);lum=rgb.mean(-1);paint=smooth(.1,.3,(mx-mn)/(mx+1e-6));metal=(1-paint)*smooth(.12,.5,lum)*.58;metal=metal*(1-structure)+(.1+.4*fins)*structure;metal*=1-flat;metal=metal*(1-pan)+.05*pan;metal*=1-glass
 rough=np.clip(.79-.24*metal,.52,.87);rough=rough*(1-structure)+(.84-.25*fins)*structure;rough=rough*(1-pan)+.87*pan;rough=rough*(1-flat)+.74*flat;rough=rough*(1-glass)+.28*glass
 dy,dx=np.gradient(h);normal=np.stack((-dx*2.2,dy*2.2,np.ones_like(h)),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 rec={}
 def save(a,key,cs='Non-Color'):
  rgba=np.ones((N,N,4),np.float32);rgba[:,:,:3]=a if a.ndim==3 else a[:,:,None];im=bpy.data.images.new(f'Reliant rel{i} {key}',N,N,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel());im.scale(OUT,OUT)
  if key=='normal':
   buf=np.empty(OUT*OUT*4,np.float32);im.pixels.foreach_get(buf);a=buf.reshape(-1,4);n=a[:,:3]*2-1;n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8);a[:,:3]=n*.5+.5;im.pixels.foreach_set(a.ravel())
  p=M/f'reliant_rel{i}_{key}_v1.png';im.filepath_raw=str(p);im.file_format='PNG';im.save();bpy.data.images.remove(im);rec[key]=dict(path=str(p),sha256=sha(p),dimensions=[OUT,OUT]);im=bpy.data.images.load(str(p),check_existing=False);im.colorspace_settings.name=cs;return im
 maps={'basecolor':save(rgb,'basecolor','sRGB'),'normal':save(normal*.5+.5,'normal'),'roughness':save(rough,'roughness'),'metallic':save(metal,'metallic'),'emissive':save(emit,'emissive','sRGB')}
 for key,a in [('height',(h+2)/4),('flat_graphics',flat),('structure',structure),('glass',glass)]:bpy.data.images.remove(save(a,key))
 mat=bpy.data.materials.new(f'Reliant_Worn_REL_{i}_PBR');mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');links=mat.node_tree.links
 for key,im in maps.items():
  im.pack();tx=nodes.new('ShaderNodeTexImage');tx.name='Delivered '+key;tx.image=im;tx.extension='REPEAT'
  if key=='normal':nm=nodes.new('ShaderNodeNormalMap');links.new(tx.outputs[0],nm.inputs['Color']);links.new(nm.outputs[0],bs.inputs['Normal'])
  elif key=='emissive':links.new(tx.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
  else:links.new(tx.outputs[0],bs.inputs[{'basecolor':'Base Color','roughness':'Roughness','metallic':'Metallic'}[key]])
 materials['REL_'+str(i)]=mat;records['rel'+str(i)]=rec;print('MATERIAL_READY',i,flush=True)
for o in obs:
 for j,mat in enumerate(o.data.materials):
  name=mat.name.upper().split('.')[0]
  if name in materials:o.data.materials[j]=materials[name]
 b=before[o.name];assert b[0]==[list(v.co) for v in o.data.vertices] and b[1]==[list(p.vertices) for p in o.data.polygons]
 for name,values in b[2].items():assert values==[list(q.uv) for q in o.data.uv_layers[name].data]
visible=[o for o in obs if not o.hide_render];points=[o.matrix_world@v.co for o in visible for v in o.data.vertices];lo=Vector([min(p[k] for p in points) for k in range(3)]);hi=Vector([max(p[k] for p in points) for k in range(3)]);center=(lo+hi)/2;size=(hi-lo).length
for name,vec in [('Front',(1,-1.4,.9)),('Opposite',(-1,-1.4,.9)),('Rear',(.8,1.4,.65)),('Belly',(1,-1,-.7))]:
 cam=bpy.data.objects[name];cam.location=center+Vector(vec).normalized()*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*.87
s.camera=bpy.data.objects['Front'];s.render.resolution_x=1400;s.render.resolution_y=1050;s.cycles.samples=20
scene=D/'reliant_worn_pbr_v1.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(scene))
report=dict(scene=str(scene),scene_sha256=sha(scene),maps=records,original_geometry_and_uvs_preserved=True,structural_height_only=True,colour_method='Built-in imagegen edits of preserved original atlases; 1254px reconstruction masters resampled to 4096px delivery',shared_parts='Native turrets and hangar interior unchanged',runtime_visual_validation='pending')
(W/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
for name in ['Front','Rear','Belly']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(D/'review'/('material_'+name.lower()+'.png'));bpy.ops.render.render(write_still=True)
print('RELIANT_MATERIALS_COMPLETE',flush=True)
