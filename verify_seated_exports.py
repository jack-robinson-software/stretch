import json,subprocess
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent/'seated';clips={'Side-reaches':300,'Gentle-turns':240,'Shoulder-rolls':180,'Seated-breathe':240};report={}
for name,count in clips.items():
 folder=B/name;frames=sorted((folder/'alpha').glob('*.png'));assert len(frames)==count,(name,len(frames))
 for f in frames:
  with Image.open(f) as im:assert im.mode=='RGBA' and im.size==(600,720),(name,f,im.mode,im.size);im.verify()
 video=folder/f'Pip-{name.lower()}.mp4';metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_frames','-show_entries','format=duration','-of','json',str(video)]));st=metadata['streams'][0]
 assert st['codec_name']=='h264' and st['pix_fmt']=='yuv420p' and st['r_frame_rate']=='30/1' and int(st['nb_frames'])==count,(name,st)
 subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
 report[name]={'frames':count,'duration':metadata['format']['duration'],'format':'H.264 / yuv420p / 600x720 / 30 fps','decode':'pass','alpha':'RGBA PNG sequence verified'}
for path,count in [(B/'Pip-seated-preview.mp4',960),(B/'Pip-seated-side-reaches-two-loops.mp4',600)]:
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=nb_frames','-show_entries','format=duration','-of','json',str(path)]));assert int(metadata['streams'][0]['nb_frames'])==count,(path,metadata)
 subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True);report[path.name]={'frames':count,'duration':metadata['format']['duration'],'decode':'pass'}
(B/'export-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
