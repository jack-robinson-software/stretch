import bpy,os,hashlib,array,json
B=os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
def meshhash(o):
 a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'model','Pip.blend'));approved=meshhash(bpy.data.objects['Pip • asymmetric bean'])
bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'seated','Pip-seated-movements.blend'))
assert set(s.name for s in bpy.data.scenes)==set(['Side-reaches','Gentle-turns','Shoulder-rolls','Seated-breathe'])
for s in bpy.data.scenes:
 bpy.context.window.scene=s;s.frame_set(1)
 body=next(o for o in s.objects if o.name.startswith('Pip • asymmetric bean'));assert meshhash(body)==approved,s.name
 for o in s.objects:
  for data in [o,o.data] if o.data else [o]:
   if data.animation_data:
    for d in data.animation_data.drivers:
     assert d.is_valid,(s.name,o.name,d.data_path)
     for v in d.driver.variables:
      for target in v.targets:
       if isinstance(target.id,bpy.types.Object):assert target.id.name in s.objects,(s.name,o.name,target.id.name)
print('VERIFIED: four independent seated scenes; approved body geometry unchanged; all curve and face drivers valid and local to their scene',flush=True)
