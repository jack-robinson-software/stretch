"""Reference-pose animation rig for the approved fresh Pip. No retired rig code."""
import bpy,math,os,json,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
B=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(B,'animations');FPS=30
CLIPS={'Idle':180,'Stretch':300,'Breathe':240,'Wave':120,'Celebrate':90,'Walk-off':165,'Walk-back':165}
def smooth(v):
 v=max(0,min(1,v));return v*v*v*(10+v*(-15+6*v))
def ramp(t,a,b):return smooth((t-a)/(b-a))
def lerp(a,b,t):return a+(b-a)*t
def track(t,keys):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return lerp(x,y,smooth((t-a)/(b-a)))
 return keys[-1][1]
def vec(v):return Vector(v)
def empty(name,col,parent=None,location=(0,0,0),size=.09):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.empty_display_type='SPHERE';o.empty_display_size=size;o.location=location;o.parent=parent;return o
def key(o,path,f):o.keyframe_insert(data_path=path,frame=f)
def keep_parent(o,p):
 bpy.context.view_layer.update();m=o.matrix_world.copy();o.parent=p;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=p.matrix_world.inverted()@m

def profile(upper=-55,lower=-70,lu=.53,ll=.50,lift=0,ey=-.27,hy=-.28):return dict(upper=upper,lower=lower,lu=lu,ll=ll,lift=lift,ey=ey,hy=hy)
NEUTRAL=profile();HIP=profile(-5,-145,.46,.40,.04,-.35,-.52);FLEX=profile(30,92,.56,.57,.13,-.26,-.30);HIGH=profile(76,140,.85,.94,.46,-.15,-.20);CHEER=profile(33,78,.58,.55,.12,-.24,-.29);BELLY=profile(-12,-163,.48,.53,.0,-.49,-.73)
def blend(a,b,v):return {k:lerp(a[k],b[k],v) for k in a}
def pose_track(t,keys):
 if t<=keys[0][0]:return keys[0][1].copy()
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return blend(x,y,smooth((t-a)/(b-a)))
 return keys[-1][1].copy()

def curve(name,points,radius,material,col,parent):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=24;c.bevel_resolution=5;c.bevel_depth=radius;c.use_fill_caps=True;s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);col.objects.link(o);c.materials.append(material);o.parent=parent;return o

def drive_points(o,controls):
 # Drive handles as well as centers: AUTO handles do not update reliably
 # when their centers are driven on evaluated curve data.
 for index,(p,control) in enumerate(zip(o.data.splines[0].bezier_points,controls)):
  p.handle_left_type='FREE';p.handle_right_type='FREE'
  for axis in range(3):
   d=p.driver_add('co',axis).driver;v=d.variables.new();v.name='v';v.type='SINGLE_PROP';v.targets[0].id=control;v.targets[0].data_path='location['+str(axis)+']';d.expression='v'
   tangent=['(v1-v0)*.30','(v2-v0)*.17','(v2-v1)*.30'][index]
   for prop,sign in [('handle_left','-'),('handle_right','+')]:
    d=p.driver_add(prop,axis).driver
    for j,target in enumerate(controls):
     v=d.variables.new();v.name='v'+str(j);v.type='SINGLE_PROP';v.targets[0].id=target;v.targets[0].data_path='location['+str(axis)+']'
    d.expression='v'+str(index)+sign+'('+tangent+')'

def travel(t):
 # Integral of an eased velocity: move while turning; no stationary pivot.
 a=.35;b=4.85;r=.45;u=max(0,min(b-a,t-a));dur=b-a
 def integral(x):return x**3-.5*x**4
 if u<r:d=r*integral(u/r)
 elif u>dur-r:d=dur-r-r*integral((dur-u)/r)
 else:d=u-r*.5
 return 4.1*d/(dur-r)
def path(name,t):
 d=travel(t)
 if name=='Walk-off':return vec((d,0,0)),math.pi/2*ramp(t,.35,1.15)
 return vec((4.1-d,0,0)),-math.pi/2*(1-ramp(t,3.95,4.85))
def yawmat(y):return Matrix.Rotation(y,3,'Z')

def create_clip(name,length):
 bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'model','Pip.blend'));scene=bpy.context.scene;scene.name=name
 scene.frame_start=1;scene.frame_end=length;scene.render.fps=FPS
 root=bpy.data.objects['Pip • placement'];root.name='CTRL • placement';root.empty_display_type='CIRCLE';root.empty_display_size=1.2
 col=bpy.data.collections.new('Movement controls');scene.collection.children.link(col)
 bodyctrl=empty('CTRL • body lean and stretch',col,root,(0,0,1.02),.35)
 face=list(bpy.data.collections['Pip • body and face'].objects)
 for o in face:keep_parent(o,bodyctrl)
 bpy.context.view_layer.update();body=bpy.data.objects['Pip • asymmetric bean'];surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
 arms={};legs={};cocoa=bpy.data.materials['Cocoa • hand formed clay'];line=bpy.data.materials['Expression • soft dark cocoa']
 for side,sign in [('L',-1),('R',1)]:
  old=bpy.data.objects['Arm.'+side];bpy.data.objects.remove(old,do_unlink=True)
  controls=[empty('CTRL • '+label+'.'+side,col,root) for label in ('shoulder','elbow','wrist')]
  arm=curve('Arm.'+side,[(0,0,0)]*3,.055,cocoa,col,root);drive_points(arm,controls)
  hand=bpy.data.objects['Mitten.'+side];hand.rotation_mode='QUATERNION';hand.parent=root
  arms[side]=(controls,hand,sign)
  old=bpy.data.objects['Leg.'+side];hip=old.data.splines[0].bezier_points[0].co.copy();bpy.data.objects.remove(old,do_unlink=True)
  lc=[empty('CTRL • '+label+'.'+side,col,root) for label in ('hip','knee','ankle')]
  leg=curve('Leg.'+side,[(0,0,0)]*3,.061,cocoa,col,root);drive_points(leg,lc)
  foot=bpy.data.objects['Foot.'+side];foot.rotation_mode='XYZ';foot.parent=root
  legs[side]=(lc,foot,hip,foot.location.copy())
 facecontrol=empty('CTRL • eyes and expression',col,bodyctrl,(0,0,0),.12);facecontrol['blink']=0.;facecontrol['Expression']='Blink closes the oval eyes and reveals soft curved lids.'
 for side in ('L','R'):
  eye=bpy.data.objects['Eye.'+side]
  d=eye.driver_add('scale',2).driver;v=d.variables.new();v.name='b';v.type='SINGLE_PROP';v.targets[0].id=facecontrol;v.targets[0].data_path='["blink"]';d.expression='1-.985*b'
  center=eye.location.copy();co=[(-.067,0,.012),(0,-.005,-.025),(.067,0,.012)]
  lid=curve('Closed eyelid.'+side,co,.012,line,col,bodyctrl);lid.location=center+vec((0,-.041,0));lid.rotation_euler=eye.rotation_quaternion.to_euler()
  for axis in range(3):
   d=lid.driver_add('scale',axis).driver;v=d.variables.new();v.name='b';v.type='SINGLE_PROP';v.targets[0].id=facecontrol;v.targets[0].data_path='["blink"]';d.expression='max(.001,b)'
 # A fixed camera with room for all the overhead poses.
 camera=scene.camera;camera.data.ortho_scale=4.85;camera.location=(-1.3,-13,4.0);camera.rotation_euler=(vec((0,0,2.1))-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.render.resolution_x=600;scene.render.resolution_y=720;scene.render.resolution_percentage=100
 scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.cycles.device='GPU'
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='METAL'
 scene.render.film_transparent=True;bpy.data.objects['Studio ground'].hide_render=True
 scene['Movement']=name;scene['Reference']='references/stretch-pose-reference.png';scene['Notes']='Approved bean body retained. Fresh curve controls; baked control keys, no external scripts or handlers required for playback.'
 samples=[];contacts=[]
 for f in range(1,length+2):
  t=(f-1)/FPS;u=t/(length/FPS);breath=math.sin(2*math.pi*u)
  bodyctrl.location=(0,0,1.02);bodyctrl.rotation_euler=(0,0,0);bodyctrl.scale=(1,1,1);root.location=(0,0,0);root.rotation_euler=(0,0,0)
  blink=0.;lp=NEUTRAL.copy();rp=NEUTRAL.copy();bodylift=0.;lean=0.;stretch=0.;walk=name.startswith('Walk-');walkweight=0
  if name=='Idle':
   stretch=.0025*math.sin(2*math.pi*u);lean=.006*math.sin(2*math.pi*u);blink=track(t,[(0,0),(1.5,0),(1.60,1),(1.73,0),(4.5,0),(4.60,1),(4.73,0),(6,0)])
  elif name=='Stretch':
   lp=pose_track(t,[(0,NEUTRAL),(.75,NEUTRAL),(1.6,HIP),(2.65,FLEX),(3.8,HIGH),(6.8,HIGH),(8.0,FLEX),(9.4,NEUTRAL),(10,NEUTRAL)]);rp=lp.copy()
   # The reference clasp is approached gently, then the torso bends beneath it.
   clasp=track(t,[(0,0),(3.8,0),(4.35,1),(6.65,1),(7.1,0),(10,0)])
   for p in (lp,rp):p['lower']+=clasp*4
   lean=track(t,[(0,0),(3.9,0),(5.2,-.075),(5.9,-.075),(6.7,.035),(7.2,0),(10,0)])
   stretch=track(t,[(0,0),(.8,-.009),(1.6,0),(3.8,.026),(6.8,.026),(8,0),(9.4,0),(10,0)])
   bodylift=track(t,[(0,0),(.8,-.014),(1.6,0),(3.8,.018),(6.8,.018),(8,0),(10,0)])
   blink=track(t,[(0,0),(.3,0),(.40,1),(.53,0),(2.8,0),(3.5,1),(7.2,1),(8,0),(10,0)])
  elif name=='Breathe':
   w=ramp(t,.4,1.5)*(1-ramp(t,6.6,7.8));lp=blend(NEUTRAL,BELLY,w);rp=lp.copy()
   inhale=track(t,[(0,0),(1.5,0),(3.6,1),(4.1,1),(6.5,0),(8,0)])
   stretch=.022*inhale;bodylift=.018*inhale;bodyctrl.scale.y=1+.025*inhale;blink=w
  elif name=='Wave':
   w=ramp(t,.35,1.5)*(1-ramp(t,2.8,3.95));rp=blend(NEUTRAL,profile(31,85,.56,.60,.14,-.25,-.28),w)
   rp['lower']+=9*math.sin(2*math.pi*(t-1.5)/.8)*ramp(t,1.5,1.7)*(1-ramp(t,2.55,2.8));lean=-.015*w
   blink=track(t,[(0,0),(2.6,0),(2.7,1),(2.83,0),(4,0)])
  elif name=='Celebrate':
   w=ramp(t,.30,1.15)*(1-ramp(t,1.8,2.9));lp=blend(NEUTRAL,CHEER,w);rp=lp.copy();stretch=.012*w;bodylift=.035*w
   blink=track(t,[(0,0),(.65,0),(.85,1),(1.8,1),(2.2,0),(3,0)])
  elif walk:
   pos,yaw=path(name,t);root.location=pos;root.rotation_euler.z=yaw
   walkweight=ramp(t,.35,.85)*(1-ramp(t,4.85,5.30));phase=2*math.pi*(t-.35)/.82
   bodylift=.025*(.5-.5*math.cos(2*phase))*walkweight;lean=-.018*math.sin(phase)*walkweight
   bodyctrl.rotation_euler.x=.035*walkweight;stretch=-.004*walkweight
   blink=track(t,[(0,0),(1.3,0),(1.4,1),(1.53,0),(5.5,0)])
  bodyctrl.location.z+=bodylift;bodyctrl.rotation_euler.y=lean;bodyctrl.scale.x=1-stretch*.35;bodyctrl.scale.z=1+stretch
  # Body-relative endpoints are transformed together with the face and trunk.
  bodymat=Matrix.Translation(bodyctrl.location)@bodyctrl.rotation_euler.to_matrix().to_4x4()@Matrix.Diagonal((*bodyctrl.scale,1))@Matrix.Translation(vec((0,0,-1.02)))
  def bodypoint(p):return bodymat@vec(p)
  for side,p in [('L',lp),('R',rp)]:
   cs,hand,sign=arms[side]
   def localarm(pp):
    z=(2.02 if side=='L' else 2.04)+pp['lift'];y=lerp(-.25 if side=='L' else .11,.06,min(1,pp['lift']/.46))
    sh=surface.ray_cast(vec((sign*3,y,z)),vec((-sign,0,0)))[0];sh.x-=sign*.08
    aa=math.radians(pp['upper']);bb=math.radians(pp['lower'])
    el=sh+vec((sign*math.cos(aa)*pp['lu'],0,math.sin(aa)*pp['lu']));el.y=pp['ey']
    ha=el+vec((sign*math.cos(bb)*pp['ll'],0,math.sin(bb)*pp['ll']));ha.y=pp['hy']
    return sh,el,ha
   shoulder,elbow,palm=localarm(p)
   if name=='Stretch' and 1.6<t<2.65:
    # Hands travel upward in front of the torso while the elbow opens.
    # This avoids reversing the hinge through a large planar rotation.
    v=smooth((t-1.6)/1.05);a=localarm(HIP);b=localarm(FLEX)
    shoulder,elbow,palm=[x.lerp(y,v) for x,y in zip(a,b)];palm.y-=.38*math.sin(math.pi*v)
   if walk:
    ph=2*math.pi*(t-.35)/.82+(0 if side=='L' else math.pi)
    elbow.y-=.14*math.sin(ph)*walkweight;palm.y-=.29*math.sin(ph)*walkweight
   shoulder=bodypoint(shoulder);elbow=bodypoint(elbow);palm=bodypoint(palm)
   direction=(palm-elbow).normalized();wrist=palm-direction*.14
   for control,co in zip(cs,[shoulder,elbow,wrist]):control.location=co;key(control,'location',f)
   hand.location=palm
   zz=-direction;yy=vec((0,1,0));xx=yy.cross(zz).normalized();yy=zz.cross(xx).normalized();q=Matrix((xx,yy,zz)).transposed().to_quaternion()
   if f>1 and q.dot(hand.rotation_quaternion)<0:q.negate()
   hand.rotation_quaternion=q;key(hand,'location',f);key(hand,'rotation_quaternion',f)
   if f%15==1:samples.append({'frame':f,'side':side,'shoulder':list(shoulder),'elbow':list(elbow),'hand':list(palm)})
  for side,(cs,foot,hip,neutralfoot) in legs.items():
   foot.location=neutralfoot;foot.rotation_euler=(0,0,0);swing=0
   if walk:
    offset=0 if side=='L' else .5;phase=(t-.35)/.82+offset;cycle=math.floor(phase);p=phase-cycle
    ta=.35+(cycle-offset)*.82;tb=ta+.82
    pa,ya=path(name,ta);pb,yb=path(name,tb)
    wa=pa+yawmat(ya)@neutralfoot;wb=pb+yawmat(yb)@neutralfoot
    if p<.60:world=wa;fyaw=ya
    else:
     swing=(p-.60)/.40;world=wa.lerp(wb,smooth(swing));moving=(wb-wa).length>.001
     if moving:world.z+=.14*math.sin(math.pi*swing)**2
     else:swing=0
     fyaw=lerp(ya,yb,smooth(swing))
    rootpos,rootyaw=path(name,t);local=yawmat(-rootyaw)@(world-rootpos)
    # Stance feet remain fixed in world space, including acceleration
    # and stopping. Final swing targets land at the neutral foot placements.
    foot.location=local;foot.rotation_euler.z=fyaw-rootyaw;foot.rotation_euler.x=.10*math.sin(2*math.pi*swing)
    if p<.6 and walkweight>.999:contacts.append({'frame':f,'side':side,'world':list(world)})
   hippos=bodypoint(hip);ankle=foot.location+foot.rotation_euler.to_matrix()@vec((.02,.125,.05));knee=hippos.lerp(ankle,.52);knee.y-=.025+.065*math.sin(math.pi*swing)**2;knee.x+=(-.018 if side=='L' else .018)
   for control,co in zip(cs,[hippos,knee,ankle]):control.location=co;key(control,'location',f)
   key(foot,'location',f);key(foot,'rotation_euler',f)
  for path_ in ('location','rotation_euler','scale'):key(bodyctrl,path_,f)
  for path_ in ('location','rotation_euler'):key(root,path_,f)
  facecontrol['blink']=blink;key(facecontrol,'["blink"]',f)
 # Linear dense keys preserve authored trajectories without Bezier overshoot.
 for action in bpy.data.actions:
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
 if bodyctrl.animation_data:bodyctrl.animation_data.action.name=name
 for o in col.objects:
  o.hide_render=o.type=='EMPTY'
  if o.animation_data and o.animation_data.action:o.animation_data.action.use_fake_user=True
 scene.timeline_markers.clear()
 marks={'Stretch':[(1,'Relaxed'),(49,'Waist preparation'),(80,'Elbows raised'),(115,'Overhead'),(132,'Hands together'),(158,'Side bend'),(214,'Release'),(241,'Elbows lower'),(283,'Neutral')],'Breathe':[(46,'Hands settle'),(109,'Inhale'),(196,'Exhale')],'Wave':[(37,'Greeting'),(88,'Release')],'Celebrate':[(31,'Small cheer')],'Walk-off':[(12,'Step and turn'),(130,'Off screen')],'Walk-back':[(1,'Approach'),(146,'Face forward')],'Idle':[(1,'Quiet breathing')]}
 for fr,label in marks[name]:scene.timeline_markers.new(label,frame=fr)
 scene.frame_set(1);bpy.context.view_layer.update()
 bpy.ops.object.select_all(action='DESELECT');bodyctrl.select_set(True);bpy.context.view_layer.objects.active=bodyctrl
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
 os.makedirs(os.path.join(OUT,name),exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,name,'Pip.blend'),compress=True)
 with open(os.path.join(OUT,name,'pose-checks.json'),'w') as f:json.dump({'clip':name,'frames':length,'samples':samples,'stance':contacts},f,indent=2)
 print('BUILT',name,flush=True)

if __name__=='__main__':
 selected=sys.argv[sys.argv.index('--clips')+1].split(',') if '--clips' in sys.argv else list(CLIPS)
 for name in selected:create_clip(name,CLIPS[name])
