"""Fresh reference-led Pip model. No geometry or rigs from the retired version."""
import bpy,math,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(BASE,'renders')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene

def srgb(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in a)+(1,)
def collection(name):
 c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
body_collection=collection('Pip • body and face');limb_collection=collection('Pip • relaxed limbs');studio=collection('Studio');design=collection('Design controls • not animated')
def move(o,c):
 for current in list(o.users_collection):current.objects.unlink(o)
 c.objects.link(o)
def clay(name,colour,roughness=.73,grain=.006):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=srgb(colour);bs.inputs['Roughness'].default_value=roughness
 bs.inputs['Subsurface Weight'].default_value=.035;bs.inputs['Subsurface Radius'].default_value=(.7,.3,.15)
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=62;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.65
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=grain;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
 tone=n.new('ShaderNodeTexNoise');tone.inputs['Scale'].default_value=6;tone.inputs['Detail'].default_value=2
 ramp=n.new('ShaderNodeValToRGB');base=srgb(colour);ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[1].position=.88
 ramp.color_ramp.elements[0].color=tuple(v*.89 for v in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,v*1.07) for v in base[:3])+(1,)
 l.new(tone.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],bs.inputs['Base Color']);l.new(bs.outputs['BSDF'],out.inputs['Surface']);return m
terracotta=clay('Terracotta • warm fine clay','D46832',.76,.007)
cocoa=clay('Cocoa • hand formed clay','683C24',.70,.004)
eye_material=clay('Eyes • dark cocoa satin','35190C',.38,.0005)
line_material=clay('Expression • soft dark cocoa','4A2715',.77,.001)

def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
# Elongated bean: full rounded ends, relatively even width, and a broad
# gentle bend. Avoid a spherical belly or a sharp hourglass waist.
verts=[];faces=[];RINGS=80;SIDES=96
for i in range(1,RINGS):
 theta=math.pi*i/RINGS;t=math.cos(theta);r=math.sin(theta)
 z=2.25+1.30*t
 cx=.02+.24*ease((t+.80)/1.80)-.13*math.exp(-((t-.15)/.52)**2)
 rx=r**.78*(.79-.045*t-.07*math.exp(-((t-.20)/.50)**2))
 ry=r*(.55+.09*math.exp(-((t+.35)/.45)**2));cy=-.035*math.exp(-((t+.25)/.6)**2)
 for j in range(SIDES):
  a=2*math.pi*j/SIDES;verts.append((cx+rx*math.cos(a),cy+ry*math.sin(a),z))
for i in range(RINGS-2):
 for j in range(SIDES):
  a=i*SIDES+j;b=i*SIDES+(j+1)%SIDES;faces.append((a,a+SIDES,b+SIDES,b))
top=len(verts);verts.append((.251,0,3.55));bottom=len(verts);verts.append((.02,-.003,.95))
for j in range(SIDES):faces.append((top,j,(j+1)%SIDES));a=(RINGS-2)*SIDES;faces.append((bottom,a+(j+1)%SIDES,a+j))
mesh=bpy.data.meshes.new('Bean • rounded quad surface');mesh.from_pydata(verts,[],faces);mesh.update();body=bpy.data.objects.new('Pip • asymmetric bean',mesh);body_collection.objects.link(body);mesh.materials.append(terracotta)
for p in mesh.polygons:p.use_smooth=True
sub=body.modifiers.new('Gentle continuous surface','SUBSURF');sub.levels=1;sub.render_levels=2
tex=bpy.data.textures.new('Restrained hand-made surface','CLOUDS');tex.noise_scale=.085;tex.noise_depth=2
mod=body.modifiers.new('Very shallow clay variation','DISPLACE');mod.texture=tex;mod.strength=.006;mod.mid_level=.5
bpy.context.view_layer.update();surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
def front(x,z,offset=.014):
 p,n,_,_=surface.ray_cast(Vector((x,-3,z)),Vector((0,1,0)));assert p is not None,(x,z)
 return p+n*offset,n

def sphere(name,center,scale,material,group=limb_collection,rotation=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=center);o=bpy.context.object;o.name=name;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if rotation is not None:o.rotation_mode='QUATERNION';o.rotation_quaternion=rotation
 o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 move(o,group);return o
# Face sits in the upper third, with small uneven brows and a tiny smile.
for side,x,z in [('L',-.07,2.63),('R',.38,2.69)]:
 p,n=front(x,z,.023);q=Vector((0,-1,0)).rotation_difference(n)
 sphere('Eye.'+side,p,(.073,.045,.105),eye_material,body_collection,q)

def curve_object(name,points,radius,material,group,cyclic=False,radii=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=32;c.bevel_resolution=6;c.bevel_depth=radius;c.use_fill_caps=True
 s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for i,(p,v) in enumerate(zip(s.bezier_points,points)):
  p.co=v;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
  if radii:p.radius=radii[i]
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,c);group.objects.link(o);c.materials.append(material);return o

def expression(name,xz,radius):
 points=[front(x,z,.016)[0] for x,z in xz]
 o=curve_object(name,points,radius,line_material,body_collection)
 for index,p in enumerate((points[0],points[-1])):sphere(name+'.soft end.'+str(index),p,(radius,radius,radius),line_material,body_collection)
 return o
expression('Brow.L',[(-.22,2.88),(-.12,2.94),(-.015,2.965)],.019)
expression('Brow.R',[(.31,3.00),(.41,2.985),(.50,2.93)],.019)
expression('Smile',[(.075,2.41),(.15,2.365),(.235,2.365),(.31,2.42)],.014)

def join_shapes(objects,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=objects[0];o.name=name
 remesh=o.modifiers.new('Joined soft clay forms','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.006;remesh.use_smooth_shade=True
 smooth=o.modifiers.new('Hand finished clay','SMOOTH');smooth.factor=.65;smooth.iterations=4
 return o

def hand(side,center,sign):
 p=Vector(center)
 palm=sphere('Palm.'+side,p,(.148,.13,.17),cocoa)
 thumb=sphere('Thumb.'+side,p+Vector((-sign*.09,-.065,-.025)),(.074,.078,.105),cocoa)
 return join_shapes([palm,thumb],'Mitten.'+side)

for side,sign in [('L',-1),('R',1)]:
 y=-.25 if side=='L' else .11;z=2.02 if side=='L' else 2.04
 shoulder=surface.ray_cast(Vector((sign*3,y,z)),Vector((-sign,0,0)))[0];shoulder.x-=sign*.075
 if side=='L':points=[shoulder,Vector((-.96,-.32,1.82)),Vector((-1.09,-.31,1.48)),Vector((-1.13,-.28,1.27))];palm=(-1.14,-.29,1.14)
 else:points=[shoulder,Vector((1.00,.11,1.81)),Vector((1.045,.075,1.52)),Vector((1.04,.03,1.31))];palm=(1.05,.015,1.18)
 arm=curve_object('Arm.'+side,points,.055,cocoa,limb_collection,radii=[1.05,1,.93,.88]);arm['Design']='Relaxed downward arm; one editable curve with a soft taper. No inherited elbow solve.'
 hand(side,palm,sign)
# Long slim legs and broad low feet. There are no hard knee/ankle corners.
for side,points,foot in [
 ('L',[(-.34,.015,1.21),(-.41,0,.73),(-.50,-.035,.38),(-.55,-.075,.18)],(-.57,-.20,.13)),
 ('R',[(.40,.025,1.21),(.42,.01,.72),(.44,-.025,.38),(.46,-.065,.18)],(.48,-.19,.13))]:
 curve_object('Leg.'+side,points,.061,cocoa,limb_collection,radii=[.93,.96,1.02,1.10])
 o=sphere('Foot.'+side,foot,(.24,.31,.13),cocoa)
 for v in o.data.vertices:
  world_z=v.co.z+o.location.z
  if world_z<.035:v.co.z=(.012*(max(0,world_z)/.035)**2)-o.location.z
 # Feet remain separate editable meshes; the curve ends are concealed inside.
 o['Sole']='Lowest point on z=0; broad soft toe, no angular ankle.'

# No animation rig is introduced at the design checkpoint.
root=bpy.data.objects.new('Pip • placement',None);design.objects.link(root)
for o in list(body_collection.objects)+list(limb_collection.objects):o.parent=root
root['Stage']='Fresh neutral model for identity/proportion review. Animation is intentionally deferred.'

floor_material=clay('Warm ivory studio','F4EEE1',.9,.0001)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));floor=bpy.context.object;floor.name='Studio ground';move(floor,studio);floor.data.materials.append(floor_material)
world=bpy.data.worlds.new('Warm soft studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.66,.54,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;scene.world=world

def area(name,position,power,size,colour):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=colour
 o=bpy.data.objects.new(name,data);studio.objects.link(o);o.location=position;o.rotation_euler=(Vector((0,0,1.9))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large warm key',(-3.5,-4.5,6),500,4.2,(1,.89,.76))
area('Soft front fill',(3,-4,3.5),150,4.0,(1,.96,.89))
area('Gentle rim',(2,3,5),280,3.5,(1,.86,.70))
camdata=bpy.data.cameras.new('Pip neutral camera');camera=bpy.data.objects.new('Pip neutral camera',camdata);studio.objects.link(camera);scene.camera=camera;camdata.type='ORTHO';camdata.ortho_scale=4.15;camdata.lens=55

def camera_pose(position,target=(0,0,1.82)):
 camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.resolution_x=800;scene.render.resolution_y=960;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
try:scene.view_settings.look='AgX - Medium High Contrast'
except:pass
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.cycles.device='GPU';scene.render.use_persistent_data=False
scene['README']='A completely fresh Pip model from the reference images. Editable body, curve limbs, mitten meshes, face curves, studio camera and lights. Neutral checkpoint only; no inherited geometry, rig, sampled arm keys or animation.'
for name,position in [('Pip-neutral',(-2.0,-12,4.0)),('Pip-front',(0,-12,3.8)),('Pip-side',(10,-.3,3.4))]:
 camera_pose(position);scene.render.filepath=os.path.join(OUT,name+'.png');bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
camera_pose((-2,-12,4.0));floor.hide_render=True;scene.render.film_transparent=True;scene.render.filepath=os.path.join(OUT,'Pip-neutral-alpha.png');bpy.ops.render.render(write_still=True)
floor.hide_render=False;scene.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'model','Pip.blend'),compress=True)
print('FRESH PIP MODEL COMPLETE',flush=True)
