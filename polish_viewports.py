import bpy,os
B=os.path.dirname(os.path.abspath(__file__));names=['Stretch','Idle','Wave','Breathe','Celebrate','Walk-off','Walk-back']
for name in names:
 path=os.path.join(B,'animations',name,'Pip.blend');bpy.ops.wm.open_mainfile(filepath=path)
 for m in bpy.data.materials:
  if not m.node_tree:continue
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs:m.diffuse_color=bs.inputs['Base Color'].default_value
 for screen in bpy.data.screens:
  for a in screen.areas:
   if a.type=='VIEW_3D':a.spaces.active.shading.color_type='MATERIAL';a.spaces.active.overlay.show_extras=False
 bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
 print('VIEWPORT READY',name,flush=True)
