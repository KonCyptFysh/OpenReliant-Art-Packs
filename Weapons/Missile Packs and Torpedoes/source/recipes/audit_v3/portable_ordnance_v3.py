import os
import bpy,json,hashlib,re
from pathlib import Path
D=Path(os.environ.get('ORDNANCE_WORKSPACE', str(Path.cwd()))).expanduser().resolve()
R=Path(os.environ['ORDNANCE_ASSET_ROOT']).expanduser().resolve()
bpy.ops.wm.open_mainfile(filepath=str(D/'ordnance_worn_audit_v3.blend'));out=R/'source/resources';out.mkdir(parents=True,exist_ok=True);resources=[]
for im in bpy.data.images:
 if im.type!='IMAGE':continue
 if not im.packed_file:
  try:im.pack()
  except RuntimeError:continue
 data=bytes(im.packed_file.data);sha=hashlib.sha256(data).hexdigest();name=Path(im.filepath).name or re.sub(r'[^A-Za-z0-9_.-]','_',im.name)+'.png';target=out/(sha[:12]+'_'+name);target.write_bytes(data);im.filepath='//resources/'+target.name;resources.append(dict(image=im.name,path=str(target.relative_to(R)),sha256=sha,bytes=len(data)))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/ordnance_worn_audit_v3.blend'),compress=True)
(R/'source/snapshot_v3.json').write_text(json.dumps(dict(scene='source/ordnance_worn_audit_v3.blend',active_uv='Ordnance_Delivery_UV_v3',resources=resources),indent=2)+'\n');print('PORTABLE_V3_SAVED',len(resources),flush=True)
