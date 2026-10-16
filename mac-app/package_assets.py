from pathlib import Path
from PIL import Image
import concurrent.futures,json
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
specs={
'idle':('animations/Idle',180),'wave':('animations/Wave',120),'stretch':('animations/Stretch',300),'breathe':('animations/Breathe',240),'celebrate':('animations/Celebrate',90),'walkOff':('animations/Walk-off',165),
'seatedReach':('seated/Side-reaches',300),'seatedTurn':('seated/Gentle-turns',240),'seatedShoulders':('seated/Shoulder-rolls',180),'seatedBreathe':('seated/Seated-breathe',240)}
resources=ROOT/'Stretch.app/Contents/Resources';jobs=[]
for name,(source,count) in specs.items():
 folder=resources/'Clips'/name;folder.mkdir(parents=True,exist_ok=True)
 jobs.extend((PROJECT/source/'alpha'/f'{i:04d}.png',folder/f'{i:04d}.png') for i in range(1,count+1))
def convert(job):
 source,target=job
 if target.exists():return
 with Image.open(source) as im:im.resize((300,360),Image.Resampling.LANCZOS).save(target,compress_level=6)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(convert,jobs))
(resources/'clips.json').write_text(json.dumps({k:{'frames':n,'fps':30} for k,(_,n) in specs.items()},indent=2))
print('PACKAGED',len(jobs),'frames',round(sum(x.stat().st_size for x in (resources/'Clips').rglob('*.png'))/1024/1024,1),'MB')
