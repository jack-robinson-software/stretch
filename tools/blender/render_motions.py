import bpy,os,sys,time,json
from array import array
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'));OUT=os.path.join(B,sys.argv[sys.argv.index('--library')+1] if '--library' in sys.argv else 'animations')
clips=sys.argv[sys.argv.index('--clips')+1].split(',') if '--clips' in sys.argv else ['Stretch']
review='--review' in sys.argv;eevee='--eevee' in sys.argv
selection={'Stretch':[1,49,80,115,132,158,201,241,283],'Idle':[1,49],'Wave':[1,37,61,83],'Breathe':[1,46,109,196],'Celebrate':[1,31,55],'Walk-off':[1,25,45,75,105,135],'Walk-back':[1,45,75,105,135,165]}
selection.update({'Side-reaches':[1,55,78,135,187,210,270],'Gentle-turns':[1,55,108,157],'Shoulder-rolls':[1,46,106],'Seated-breathe':[1,46,106,196]})
for name in clips:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT,name,'Pip.blend'));s=bpy.context.scene
 if eevee:
  s.render.engine='CYCLES' # Replaced below for a controlled engine comparison.
  s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
 else:
  s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.device='GPU'
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='METAL';p.kernel_optimization_level='OFF';p.metalrt='OFF';p.get_devices()
  for d in p.devices:d.use=d.type=='METAL'
 s.render.use_persistent_data=True
 s.render.resolution_x=600;s.render.resolution_y=720;s.render.resolution_percentage=100
 s.render.film_transparent=not review;bpy.data.objects['Studio ground'].hide_render=not review
 folder=os.path.join(OUT,name,'review' if review else 'alpha');os.makedirs(folder,exist_ok=True)
 frames=selection[name] if review else range(1,s.frame_end+1)
 if '--range' in sys.argv:
  a,b=map(int,sys.argv[sys.argv.index('--range')+1].split(':'));frames=range(a,b+1)
 for f in frames:
  dest=os.path.join(folder,f'{f:04d}.png')
  if os.path.exists(dest) and '--overwrite' not in sys.argv:continue
  s.frame_set(f);s.render.filepath=dest
  if name.startswith('Walk') and not review:
   deps=bpy.context.evaluated_depsgraph_get();projected=[]
   for obj in s.objects:
    if obj.type not in ('MESH','CURVE') or obj.hide_render:continue
    eo=obj.evaluated_get(deps);projected.extend(world_to_camera_view(s,s.camera,eo.matrix_world@Vector(c)).x for c in eo.bound_box)
   if min(projected)>1 or max(projected)<0:
    blank=bpy.data.images.get('Offscreen alpha')
    if blank is None:
     blank=bpy.data.images.new('Offscreen alpha',width=600,height=720,alpha=True);blank.generated_color=(0,0,0,0);blank.pixels.foreach_set(array('f',[0.0])*(600*720*4))
    blank.save_render(dest,scene=s);print('OFFSCREEN',name,f,flush=True);continue
  start=time.time();bpy.ops.render.render(write_still=True);print('RENDER',name,f,round(time.time()-start,2),flush=True)
