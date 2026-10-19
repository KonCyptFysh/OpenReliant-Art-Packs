import bpy
from pathlib import Path
D=Path('${RELIANT_WORKSPACE}');M=D/'maps/windows_v5'
bpy.ops.wm.open_mainfile(filepath=str(D/'reliant_worn_pbr_v4.blend'))
mat=bpy.data.materials['Reliant_Worn_REL_2_PBR'];changed=[]
for node in mat.node_tree.nodes:
 if node.type!='TEX_IMAGE' or not node.image:continue
 name=Path(bpy.path.abspath(node.image.filepath)).name
 if name not in ['orr2_hull.png','orr2_hull_emissive.png','orr2_hull_normal.png','orr2_hull_orm.png']:continue
 image=bpy.data.images.load(str(M/name),check_existing=False);image.colorspace_settings.name='sRGB' if name in ['orr2_hull.png','orr2_hull_emissive.png'] else 'Non-Color';image.pack();node.image=image;changed.append(name)
assert len(changed)==4,changed
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'reliant_worn_pbr_v5.blend'));print('SCENE_V5_SAVED',changed)
