"""Encode completed 30 fps alpha sequences as portable H.264 review clips."""
import os,time,subprocess,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[2];OUT=B/'seated'
clips={'Side-reaches':300,'Gentle-turns':240,'Shoulder-rolls':180,'Seated-breathe':240}
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
pending=dict(clips)
while pending:
 for name,count in list(pending.items()):
  folder=OUT/name;last=folder/'alpha'/f'{count:04d}.png'
  if not last.exists() or len(list((folder/'alpha').glob('*.png')))!=count:continue
  try:
   with Image.open(last) as im:im.verify()
  except Exception:continue
  bg=Image.new('RGB',(600,720),'#f4eee1');d=ImageDraw.Draw(bg);d.text((25,22),{'Side-reaches':'Side reaches','Gentle-turns':'Gentle turns','Shoulder-rolls':'Shoulder rolls','Seated-breathe':'Seated breathing'}[name],fill='#683c24',font=font);bg.save(folder/'review-background.png')
  cmd=['ffmpeg','-y','-loglevel','error','-framerate','30','-i',str(folder/'alpha'/'%04d.png'),'-framerate','30','-loop','1','-i',str(folder/'review-background.png'),'-filter_complex','[1:v][0:v]overlay=shortest=1,format=yuv420p','-frames:v',str(count),'-r','30','-c:v','libx264','-profile:v','main','-level','3.1','-crf','18','-preset','medium','-movflags','+faststart',str(folder/f'Pip-{name.lower()}.mp4')]
  subprocess.run(cmd,check=True)
  print('ENCODED',name,flush=True);del pending[name]
 if pending:time.sleep(3)
order=list(clips)
playlist=OUT/'playlist.txt';playlist.write_text(''.join("file '"+str(OUT/n/f'Pip-{n.lower()}.mp4')+"'\n" for n in order))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(playlist),'-c','copy','-movflags','+faststart',str(OUT/'Pip-seated-preview.mp4')],check=True)
loops=OUT/'side-reach-loops.txt';clip=OUT/'Side-reaches'/'Pip-side-reaches.mp4';loops.write_text(("file '"+str(clip)+"'\n")*2)
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(loops),'-c','copy','-movflags','+faststart',str(OUT/'Pip-seated-side-reaches-two-loops.mp4')],check=True)
print('ALL REVIEW VIDEOS COMPLETE',flush=True)
