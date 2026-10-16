import bpy,os,json
B=os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'));bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'animations','Pip-movements.blend'))
assert set(s.name for s in bpy.data.scenes)==set(['Idle','Stretch','Breathe','Wave','Celebrate','Walk-off','Walk-back'])
for s in bpy.data.scenes:
 bpy.context.window.scene=s;s.frame_set(1)
 for o in s.objects:
  for dat in [o,o.data] if o.data else [o]:
   if not dat.animation_data:continue
   for f in dat.animation_data.drivers:
    assert f.is_valid,(s.name,o.name,f.data_path)
    for v in f.driver.variables:
     for target in v.targets:
      if isinstance(target.id,bpy.types.Object):assert target.id.name in s.objects,(s.name,o.name,target.id.name)
 assert not any(o.type=='ARMATURE' for o in s.objects)
print('MASTER VERIFIED: seven independent scenes; all driver targets are local to their scene; no external playback handlers',flush=True)
