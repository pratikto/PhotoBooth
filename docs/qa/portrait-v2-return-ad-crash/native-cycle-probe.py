import faulthandler,json,os,time,threading,traceback,gc
from pathlib import Path
from photobooth.kiosk_v2.diagnostics import DiagnosticSession
diagnostics=DiagnosticSession(Path.cwd())
os.write(1,("Diagnostic file: "+str(diagnostics.path)+"\n").encode())
root=Path('/tmp/v2-return-ad-probe')
config=root/'playlist.json'
config.write_text(json.dumps({'ads':[{'id':'mono','file':str(root/'mono.mp4'),'placements':['idle']},{'id':'stereo','file':str(root/'stereo.mp4'),'placements':['idle']},{'id':'image','file':str(Path('photobooth/assets/ads/sample-01.jpg').resolve()),'placements':['idle']}]}))
os.environ['PHOTOBOOTH_AD_CONFIG']=str(config)
from kivy.base import EventLoop
from kivy.core.window import Window
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.theme import ArcadeButton
from photobooth.advertising import AdEventLog
report=[]
def emit(**row):
 report.append(row);os.write(1,(json.dumps(row)+'\n').encode())
def settle(seconds=.10):
 end=time.monotonic()+seconds
 while time.monotonic()<end:EventLoop.idle()
def action(text):
 next(w for w in app.stage.walk() if isinstance(w,ArcadeButton) and w.text==text).dispatch('on_release')
def ready(player):
 end=time.monotonic()+10
 while time.monotonic()<end and not player._ready:settle(.025)
 assert player._ready,'Video did not deliver a native texture'
app=PortraitKioskV2App()
try:
 Window.add_widget(app.build());app.events=AdEventLog(root/'events.jsonl');Window.size=(452,900)
 for cycle in range(20):
  player=app._ad_player;ready(player)
  assert player.video.texture is not None
  if cycle%2:player.next();ready(player)
  old_video=player.video
  emit(cycle=cycle+1,phase='video-ready',ad_id=player.ad_id,video_size=list(old_video.texture.size))
  action('MULAI FOTO');settle(.08)
  assert old_video._video is None and player._closed
  action('LANJUT PILIH TEMPLATE');settle(.08)
  app._shift_template(1);settle(.03);app._change_copies(1)
  action('SELESAI / KEMBALI IKLAN');settle(.10)
  assert app.navigation.page=='advert' and not app._closed
  assert not any(app.quantities.values()) and not app.navigation.tutorial_seen
  if cycle%5==0:gc.collect()
  emit(cycle=cycle+1,phase='returned',next_frame_threads=sum(t.name=='Next frame' for t in threading.enumerate()))
 ready(app._ad_player)
 emit(result='COMPLETED',cycles=20)
except BaseException:
 os.write(2,traceback.format_exc().encode());raise
finally:
 app.on_stop();Window.remove_widget(app.stage);diagnostics.close()
 (root/'corrected-result.json').write_text(json.dumps(report,indent=2)+'\n')
