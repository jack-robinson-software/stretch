import bpy,os,json,math,numpy as np
B=os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'));result={}
for name in ['Stretch','Walk-off','Walk-back']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(B,'animations',name,'Pip.blend'));s=bpy.context.scene;old={};drift=0;lowest=1.;penetrationframes=[]
 for f in range(1,s.frame_end+1):
  s.frame_set(f);t=(f-1)/30
  for side in ['L','R']:
   foot=bpy.data.objects['Foot.'+side];m=np.asarray(foot.matrix_world);coords=np.asarray([v.co[:] for v in foot.data.vertices]);z=(coords@m[:3,:3].T+m[:3,3])[:,2].min();lowest=min(lowest,float(z))
   if z<-.02:penetrationframes.append((f,side,float(z)))
   stance=True
   if name.startswith('Walk'):
    phase=(t-.35)/.82+(0 if side=='L' else .5);stance=phase%1<.6 and .85<t<4.55;cycle=math.floor(phase)
   else:cycle=0
   p=foot.matrix_world.translation.copy()
   if stance and side in old and old[side][0]==cycle:drift=max(drift,(p-old[side][1]).length)
   if stance:old[side]=(cycle,p)
   else:old.pop(side,None)
 result[name]={'max_stance_step_drift':drift,'lowest_sole_z':lowest,'penetration_below_2cm':penetrationframes[:10]}
 print(name,result[name],flush=True)
with open(os.path.join(B,'animations','contact-validation.json'),'w') as f:json.dump(result,f,indent=2)
