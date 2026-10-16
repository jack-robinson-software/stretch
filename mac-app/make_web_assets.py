from pathlib import Path
from PIL import Image
import concurrent.futures
B=Path(__file__).resolve().parent;out=B/'preview-assets';out.mkdir(exist_ok=True)
clips=['idle','wave','stretch','breathe','celebrate','seatedReach','seatedTurn','seatedShoulders','seatedBreathe']
def export(name):
 target=out/(name+'.webp')
 if target.exists():return
 files=sorted((B/'Stretch.app/Contents/Resources/Clips'/name).glob('*.png'))
 frames=[]
 for p in files:
  with Image.open(p) as im:frames.append(im.resize((200,240),Image.Resampling.LANCZOS))
 duration=[34 if i%3==2 else 33 for i in range(len(frames))]
 frames[0].save(target,save_all=True,append_images=frames[1:],duration=duration,loop=0,quality=80,method=4)
 print(name,round(target.stat().st_size/1024),'KB',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(export,clips))
