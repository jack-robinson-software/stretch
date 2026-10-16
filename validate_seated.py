import bpy,os,json,math,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier
B=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(B,'seated');report=os.path.join(OUT,'pose-validation.json');results=json.load(open(report)) if os.path.exists(report) else {}
names=sys.argv[sys.argv.index('--clips')+1].split(',') if '--clips' in sys.argv else ['Side-reaches','Gentle-turns','Shoulder-rolls','Seated-breathe']
for name in names:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT,name,'Pip.blend'));s=bpy.context.scene;body=bpy.data.objects['Pip • asymmetric bean'];verts=np.asarray([v.co[:] for v in body.data.vertices]);errors=[];bottom=[];first={};maxfoot=0;chairdrift=0;depth=0;penetrations=[]
 for f in range(1,s.frame_end+2):
  s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(body,deps);inv=body.matrix_world.inverted();m=np.asarray(body.matrix_world);bottom.append(float((verts@m[:3,:3].T+m[:3,3])[:,2].min()))
  for side in ['L','R']:
   foot=bpy.data.objects['Foot.'+side]
   if f==1:first[foot.name]=foot.matrix_world.copy()
   maxfoot=max(maxfoot,max(abs(x-y) for a,b in zip(first[foot.name],foot.matrix_world) for x,y in zip(a,b)))
   arm=bpy.data.objects['Arm.'+side].evaluated_get(deps);ps=arm.data.splines[0].bezier_points;points=[]
   for a,b in zip(ps,ps[1:]):points+=list(interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,17))
   for p in points[5:]:
    p=inv@(arm.matrix_world@p);hit,n,_,_=tree.find_nearest(p);d=(p-hit).dot(n);depth=max(depth,-d)
    if d<-.05:penetrations.append([f,side,round(d,4)])
  for obj in s.objects:
   if f==1:first[obj.name]=obj.matrix_world.copy()
   if obj.name.startswith('Chair'):
    chairdrift=max(chairdrift,max(abs(x-y) for a,b in zip(first[obj.name],obj.matrix_world) for x,y in zip(a,b)))
   if f==s.frame_end+1:
    err=max(abs(x-y) for a,b in zip(first[obj.name],obj.matrix_world) for x,y in zip(a,b))
    if err>1e-5:errors.append('Loop mismatch '+obj.name)
   for data in [obj,obj.data] if obj.data else [obj]:
    if data.animation_data:
     for d in data.animation_data.drivers:
      if not d.is_valid:errors.append('Invalid driver '+obj.name)
  if f==1:initialbody=body.data.vertices[0].co.copy()
 assert not errors,(name,errors)
 assert maxfoot<1e-6 and chairdrift<1e-6,(name,maxfoot,chairdrift)
 assert min(bottom)>.61 and max(bottom)<.69,(name,min(bottom),max(bottom))
 results[name]={'loop':'matched','drivers':'valid','max_foot_drift':maxfoot,'max_chair_drift':chairdrift,'body_bottom_z':[min(bottom),max(bottom)],'seat_top_z':.67,'max_arm_centerline_penetration':depth,'deep_arm_penetration_samples':len(penetrations),'examples':penetrations[:8]}
 print(name,results[name],flush=True)
with open(os.path.join(OUT,'pose-validation.json'),'w') as f:json.dump(results,f,indent=2)
