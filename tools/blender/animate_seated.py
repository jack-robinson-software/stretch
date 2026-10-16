"""Seated movement library, retaining the approved Pip geometry and curve rig."""
import bpy,math,os,sys,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
B=os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'));sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from animate_pip import vec,empty,curve,drive_points,key,smooth,ramp,track,lerp,FLEX,HIGH,BELLY
OUT=os.path.join(B,'seated');CLIPS={'Side-reaches':300,'Gentle-turns':240,'Shoulder-rolls':180,'Seated-breathe':240}
def colour(h):
 c=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c)+(1,)
def mat(name,h,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=colour(h);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=colour(h);p.inputs['Roughness'].default_value=rough;return m

def chair(col,root):
 sage=mat('Chair • muted sage upholstery','91A292');wood=mat('Chair • honey oak frame','BA9671');pads=mat('Chair • felt feet','756B60')
 chairroot=empty('Chair • placement',col,root)
 def rounded(name,loc,size,material,bevel):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.parent=chairroot;o.data.materials.append(material)
  b=o.modifiers.new('Soft rounded edges','BEVEL');b.width=bevel;b.segments=6
  o.modifiers.new('Balanced surface normals','WEIGHTED_NORMAL');return o
 def pole(name,a,b,r,material):
  a=vec(a);b=vec(b);bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.parent=chairroot;o.data.materials.append(material);be=o.modifiers.new('Rounded timber ends','BEVEL');be.width=.018;be.segments=3
  for p in o.data.polygons:p.use_smooth=True
 rounded('Chair • seat cushion',(0,.06,.595),(1.87,1.26,.15),sage,.07)
 rounded('Chair • seat frame',(0,.08,.49),(1.72,1.13,.10),wood,.045)
 rounded('Chair • back cushion',(0,.79,1.63),(1.83,.22,1.88),sage,.105)
 for x in [-.73,.73]:
  for y in [-.38,.54]:
   end=(x*1.08,y*1.15,.025);pole('Chair • oak leg',end,(x,y,.50),.047,wood)
   rounded('Chair • felt foot',(end[0],end[1],.014),(.105,.105,.028),pads,.012)
  pole('Chair • lower back support',(x,.54,.49),(x,.85,.80),.048,wood)
  pole('Chair • upper back support',(x,.85,.80),(x,.85,2.48),.048,wood)
 return chairroot

def build(name,n):
 bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'animations','Idle','Pip.blend'));s=bpy.context.scene;s.name=name;s.frame_start=1;s.frame_end=n;s.render.fps=30
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data.action=None
 # Face and curve data retain their functional drivers; the old performance keys are removed.
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 root=bpy.data.objects['CTRL • placement'];root.location=(0,0,0);root.rotation_euler=(0,0,0)
 bc=bpy.data.objects['CTRL • body lean and stretch'];bc.location=(0,0,1.02);bc.rotation_euler=(0,0,0);bc.scale=(1,1,1)
 bpy.context.view_layer.update();body=bpy.data.objects['Pip • asymmetric bean'];tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
 coll=bpy.data.collections.new('Chair • fixed support');s.collection.children.link(coll);chair(coll,root)
 arms={side:([bpy.data.objects['CTRL • '+label+'.'+side] for label in ['shoulder','elbow','wrist']],bpy.data.objects['Mitten.'+side],sgn) for side,sgn in [('L',-1),('R',1)]}
 legs={side:([bpy.data.objects['CTRL • '+label+'.'+side] for label in ['hip','knee','ankle']],bpy.data.objects['Foot.'+side],vec((-.34 if side=='L' else .4,.015,1.21))) for side in ['L','R']}
 eyes=bpy.data.objects['CTRL • eyes and expression'];cam=s.camera;cam.data.ortho_scale=4.35;cam.location=(-4.8,-11.5,4.25);cam.rotation_euler=(vec((0,-.04,1.78))-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.resolution_x=600;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.film_transparent=True;bpy.data.objects['Studio ground'].hide_render=True
 for material in bpy.data.materials:
  if material.node_tree:
   p=next((p for p in material.node_tree.nodes if p.type=='BSDF_PRINCIPLED'),None)
   if p:material.diffuse_color=p.inputs['Base Color'].default_value
 for f in range(1,n+2):
  t=(f-1)/30;lean=0;yaw=0;rise=0;stretch=0;rollz=0;rolly=0;reachL=0;reachR=0;belly=0;blink=0
  bc.rotation_euler=(0,0,0);bc.scale=(1,1,1)
  if name=='Side-reaches':
   reachR=ramp(t,.6,1.8)*(1-ramp(t,3.3,4.45));reachL=ramp(t,5.0,6.2)*(1-ramp(t,7.7,8.9))
   lean=-.085*ramp(t,1.8,2.55)*(1-ramp(t,3.05,3.65))+.085*ramp(t,6.2,6.95)*(1-ramp(t,7.45,8.05))
   stretch=.012*max(reachL,reachR);blink=track(t,[(0,0),(1.7,0),(2.0,1),(3.4,1),(3.8,0),(6.1,0),(6.4,1),(7.8,1),(8.2,0),(10,0)])
  elif name=='Gentle-turns':
   yaw=track(t,[(0,0),(.7,0),(1.8,-.38),(2.6,-.38),(3.55,0),(4.1,0),(5.2,.38),(6.0,.38),(7.1,0),(8,0)])
   stretch=.004;blink=track(t,[(0,0),(.2,0),(.3,1),(.43,0),(3.6,0),(3.7,1),(3.83,0),(7.4,0),(7.5,1),(7.63,0),(8,0)])
  elif name=='Shoulder-rolls':
   w=ramp(t,.45,1)*(1-ramp(t,5,5.6));phase=2*math.pi*(t-1)/2;rollz=.095*(.5-.5*math.cos(phase))*w;rolly=-.06*math.sin(phase)*w
   bc.rotation_euler.x=.018*rollz/.095;stretch=.003*rollz/.095;blink=track(t,[(0,0),(.8,0),(1.2,1),(4.8,1),(5.2,0),(6,0)])
  else:
   belly=ramp(t,.5,1.5)*(1-ramp(t,6.4,7.55));inhale=track(t,[(0,0),(1.5,0),(3.5,1),(4.0,1),(6.3,0),(8,0)])
   stretch=.018*inhale;bc.scale.y=1+.02*inhale;blink=belly
  bc.location=(0,0,.72+rise);bc.rotation_euler.y=lean;bc.rotation_euler.z=yaw;bc.scale.z=1+stretch;bc.scale.x=1-stretch*.20
  M=Matrix.Translation(bc.location)@bc.rotation_euler.to_matrix().to_4x4()@Matrix.Diagonal((*bc.scale,1))@Matrix.Translation(vec((0,0,-1.02)))
  def world(p):return M@vec(p)
  def shoulder(side,sgn,lift=0):
   yy=lerp(-.25 if side=='L' else .11,.06,min(1,lift/.46))+rolly
   z=(2.02 if side=='L' else 2.04)+lift+rollz;p=tree.ray_cast(vec((sgn*3,yy,z)),vec((-sgn,0,0)))[0];p.x-=sgn*.08;return p
  def posed(side,sgn,p):
   sh=shoulder(side,sgn,p['lift']);a=math.radians(p['upper']);b=math.radians(p['lower']);el=sh+vec((sgn*math.cos(a)*p['lu'],0,math.sin(a)*p['lu']));el.y=p['ey'];hand=el+vec((sgn*math.cos(b)*p['ll'],0,math.sin(b)*p['ll']));hand.y=p['hy'];return [world(v) for v in [sh,el,hand]]
  for side,(cs,hand,sgn) in arms.items():
   rest=[world(shoulder(side,sgn)),vec((sgn*.98,-.40+rolly*.65,1.25+rollz*.8)),vec((sgn*.44,-.77,.90))]
   amount=reachL if side=='L' else reachR
   if amount>0:
    # Through the raised-elbow reference pose, then overhead. A three-dimensional
    # hand path avoids rotating a bent elbow through its opposite hinge direction.
    if amount<.48:target=[a.lerp(b,smooth(amount/.48)) for a,b in zip(rest,posed(side,sgn,FLEX))]
    else:target=[a.lerp(b,smooth((amount-.48)/.52)) for a,b in zip(posed(side,sgn,FLEX),posed(side,sgn,HIGH))]
    target[2].y-=.12*math.sin(math.pi*amount)
   elif belly>0:
    breathing=[world(shoulder(side,sgn)),vec((sgn*1.02,-.47,1.36)),world((sgn*.34,-.69,1.78))]
    target=[a.lerp(b,belly) for a,b in zip(rest,breathing)]
   else:target=rest
   sh,el,palm=target;direction=(palm-el).normalized();wrist=palm-direction*.14
   for c,p in zip(cs,[sh,el,wrist]):c.location=p;key(c,'location',f)
   hand.location=palm;zz=-direction;xx=vec((0,1,0)).cross(zz).normalized();yy=zz.cross(xx).normalized();q=Matrix((xx,yy,zz)).transposed().to_quaternion()
   if f>1 and q.dot(hand.rotation_quaternion)<0:q.negate()
   hand.rotation_quaternion=q;key(hand,'location',f);key(hand,'rotation_quaternion',f)
  for side,(cs,foot,hip) in legs.items():
   sgn=-1 if side=='L' else 1;foot.location=(sgn*.48,-.86,.13);foot.rotation_euler=(0,0,sgn*-.07)
   top=world(hip);knee=vec((sgn*.45,-.67,.74));ankle=foot.location+foot.rotation_euler.to_matrix()@vec((.02,.125,.05))
   # A rounded right-angle knee: the thigh leaves the seat towards the camera,
   # then the shin descends to a fixed ankle. Separate tangent directions at the
   # ends keep it from becoming a straight standing leg.
   for c,p in zip(cs,[top,knee,ankle]):c.location=p;key(c,'location',f)
   key(foot,'location',f);key(foot,'rotation_euler',f)
  for p in ['location','rotation_euler','scale']:key(bc,p,f)
  eyes['blink']=blink;key(eyes,'["blink"]',f)
 for a in bpy.data.actions:
  a.use_fake_user=True
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
 bc.animation_data.action.name=name
 s.timeline_markers.clear()
 marks={'Side-reaches':[(1,'Hands on lap'),(55,'Right arm reaches'),(78,'Lean left'),(135,'Hands on lap'),(187,'Left arm reaches'),(210,'Lean right'),(270,'Return to lap')],'Gentle-turns':[(1,'Sit tall'),(55,'Turn one way'),(108,'Centre'),(157,'Turn other way'),(214,'Centre')],'Shoulder-rolls':[(1,'Relaxed'),(31,'First slow roll'),(91,'Second slow roll'),(169,'Shoulders settle')],'Seated-breathe':[(1,'Hands on lap'),(46,'Hands to belly'),(106,'Inhale'),(121,'Exhale'),(226,'Hands on lap')]}
 for fr,label in marks[name]:s.timeline_markers.new(label,frame=fr)
 s['Movement']=name;s['Notes']='Seated companion movements. Chair is static, feet stay planted and hands return to lap. Approved Pip mesh and facial rig retained.'
 s.frame_set(1);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');bc.select_set(True);bpy.context.view_layer.objects.active=bc
 for screen in bpy.data.screens:
  for a in screen.areas:
   if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.color_type='MATERIAL';a.spaces.active.overlay.show_extras=False
 folder=os.path.join(OUT,name);os.makedirs(folder,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder,'Pip.blend'),compress=True);print('BUILT',name,flush=True)

names=sys.argv[sys.argv.index('--clips')+1].split(',') if '--clips' in sys.argv else list(CLIPS)
for name in names:build(name,CLIPS[name])
