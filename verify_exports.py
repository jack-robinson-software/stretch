import json,subprocess
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent/'animations';clips={'Idle':180,'Stretch':300,'Breathe':240,'Wave':120,'Celebrate':90,'Walk-off':165,'Walk-back':165};report={}
for name,count in clips.items():
 folder=B/name;frames=sorted((folder/'alpha').glob('*.png'));assert len(frames)==count,(name,len(frames))
 for f in frames:
  with Image.open(f) as im:assert im.mode=='RGBA' and im.size==(600,720),(name,f,im.mode,im.size);im.verify()
 video=folder/f'Pip-{name.lower()}.mp4';metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_frames','-show_entries','format=duration','-of','json',str(video)]));st=metadata['streams'][0]
 assert st['codec_name']=='h264' and st['pix_fmt']=='yuv420p' and st['r_frame_rate']=='30/1' and int(st['nb_frames'])==count,(name,st)
 subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
 report[name]={'frames':count,'duration':metadata['format']['duration'],'format':'H.264 / yuv420p / 600x720 / 30 fps','decode':'pass','alpha':'RGBA PNG sequence verified'}
for path,count in [(B/'Pip-movements-preview.mp4',1260),(B/'Pip-stretch-two-loops.mp4',600)]:
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=nb_frames','-show_entries','format=duration','-of','json',str(path)]));assert int(metadata['streams'][0]['nb_frames'])==count,(path,metadata)
 subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True);report[path.name]={'frames':count,'duration':metadata['format']['duration'],'decode':'pass'}
for name,fr in [('Walk-off',165),('Walk-back',1)]:
 with Image.open(B/name/'alpha'/f'{fr:04d}.png') as im:assert im.getchannel('A').getextrema()==(0,0),(name,'offscreen frame must be transparent')
(B/'export-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
