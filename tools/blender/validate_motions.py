import bpy,os,json,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier
B=os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'));report=os.path.join(B,'animations','validation.json');out=json.load(open(report)) if os.path.exists(report) else {}
names=sys.argv[sys.argv.index('--clips')+1].split(',') if '--clips' in sys.argv else ['Idle','Stretch','Breathe','Wave','Celebrate','Walk-off','Walk-back']
for name in names:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'animations',name,'Pip.blend'));s=bpy.context.scene
 errors=[];maxstep=0;previous={};penetrations=[];maxpenetration=0
 for f in range(1,s.frame_end+2):
  s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();body=bpy.data.objects['Pip • asymmetric bean'];tree=BVHTree.FromObject(body,deps);inv=body.matrix_world.inverted()
  for side in ['L','R']:
   controls=[bpy.data.objects['CTRL • '+x+'.'+side] for x in ['shoulder','elbow','wrist']]
   for c in controls:
    p=c.matrix_world.translation
    if c.name in previous:maxstep=max(maxstep,(p-previous[c.name]).length)
    previous[c.name]=p.copy()
   arm=bpy.data.objects['Arm.'+side].evaluated_get(deps);points=arm.data.splines[0].bezier_points
   centerline=[]
   for a,b in zip(points,points[1:]):centerline+=list(interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,17))
   for co in centerline[5:]:
    local=inv@(arm.matrix_world@co);hit,n,_,dist=tree.find_nearest(local)
    signed=(local-hit).dot(n)
    if signed<-.045:penetrations.append((f,side,round(signed,4)))
    maxpenetration=max(maxpenetration,-signed)
  for obj in bpy.data.objects:
   if obj.animation_data:
    for d in obj.animation_data.drivers:
     if not d.is_valid:errors.append('Invalid object driver '+obj.name)
  if f==1:
   initial={o.name:(list(o.matrix_world),tuple(o.scale)) for o in bpy.data.objects if o.type in ['MESH','EMPTY']}
  if f==s.frame_end+1 and not name.startswith('Walk'):
   for o in bpy.data.objects:
    if o.name not in initial:continue
    old,sc=initial[o.name];diff=max(abs(x-y) for a,b in zip(old,o.matrix_world) for x,y in zip(a,b))
    if diff>1e-5:errors.append('Loop transform mismatch '+o.name+' '+str(diff))
 out[name]={'errors':list(set(errors)),'max_control_step':maxstep,'centerline_penetration_count':len(penetrations),'max_penetration':maxpenetration,'examples':penetrations[:10],'frames':s.frame_end}
 print(name,out[name],flush=True)
with open(os.path.join(B,'animations','validation.json'),'w') as f:json.dump(out,f,indent=2)
