import bpy,os
from mathutils import Vector
B=os.path.dirname(os.path.abspath(__file__))
for name in ['Stretch','Wave','Celebrate','Walk-off']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'animations',name,'Pip.blend'));s=bpy.context.scene;maxima=[];old={}
 for f in range(1,s.frame_end+2):
  s.frame_set(f)
  for label in ['shoulder','elbow','wrist']:
   for side in ['L','R']:
    o=bpy.data.objects['CTRL • '+label+'.'+side];p=o.matrix_world.translation
    if o.name in old:maxima.append(((p-old[o.name]).length,f,o.name,tuple(p),tuple(old[o.name])))
    old[o.name]=p.copy()
 print(name,sorted(maxima,reverse=True)[:4],flush=True)
