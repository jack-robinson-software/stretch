import bpy,json
assert not bpy.data.actions, 'Unexpected animation actions'
assert not any(o.type=='ARMATURE' for o in bpy.data.objects), 'Unexpected inherited rig'
assert not any(o.animation_data for o in bpy.data.objects), 'Unexpected animation data'
assert not any(i.source=='FILE' for i in bpy.data.images), 'Unexpected external texture'
for name in ['Arm.L','Arm.R','Leg.L','Leg.R']:
 assert bpy.data.objects[name].type=='CURVE',name
for name in ['Pip • asymmetric bean','Mitten.L','Mitten.R','Foot.L','Foot.R']:
 assert bpy.data.objects[name].type=='MESH',name
print('VERIFIED: fresh editable model; no rig, animation or external texture dependencies')
print(json.dumps({'objects':len(bpy.data.objects),'materials':len(bpy.data.materials),'actions':len(bpy.data.actions)}))
