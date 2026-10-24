"""Owner-reported game resize, pointer and navigation regressions."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import kivy
except ImportError:
    HAS_KIVY=False
else:
    HAS_KIVY=True
    from kivy.base import EventLoop
    from kivy.config import ConfigParser
    from kivy.core.window import Window
    from kivy.input.providers.mouse import MouseMotionEventProvider
    from kivy.input.motionevent import MotionEvent
    from photobooth.kiosk_v2.theme import ArcadeButton
    from tests import test_kiosk_v2_game_widgets as support
    from tools.run_portrait_v2 import configure_kivy


@unittest.skipUnless(HAS_KIVY,'Native game/window environment required')
class GameFollowupTests(unittest.TestCase):
    def test_mouse_provider_reproduces_old_marker_and_new_config_leaves_none(self):
        before=len(Window.canvas.after.children)
        legacy=MouseMotionEventProvider('legacy-proof','')
        try:
            legacy.on_mouse_press(Window,10,10,'right',[])
            legacy.on_mouse_release(Window,10,10,'right',[])
            self.assertTrue(legacy.touches)
            self.assertGreater(len(Window.canvas.after.children),before)
        finally:legacy.on_mouse_release(Window,10,10,'all',[])
        config=ConfigParser()
        config.add_section('graphics');config.add_section('input')
        configure_kivy(config)
        provider=MouseMotionEventProvider('v2-proof',config.get('input','mouse').split(',',1)[1])
        provider.on_mouse_press(Window,10,10,'right',[])
        self.assertNotIn('_drawelement',provider.current_drag.ud)
        provider.on_mouse_release(Window,10,10,'right',[])
        self.assertFalse(provider.touches)
        self.assertEqual(len(Window.canvas.after.children),before)

    def test_no_return_to_ad_footer_on_intro_receipt_and_result(self):
        helper=support.GameWidgetTests()
        with helper.booth() as (app,_):
            app._choose_game()
            self.assertIsNone(app._game_footer)
            app._open_game_demo()
            self.assertIsNone(app._game_footer)
            app._demo_code.text='DEMO-FOOTER';app._claim_game_demo();helper.settle(app)
            self.assertIsNotNone(app._game_footer)  # Safe active-round exit remains.
            helper.finish(app,True)
            self.assertIsNone(app._game_footer)
            self.assertFalse(any(isinstance(w,ArcadeButton) and 'KEMBALI KE IKLAN' in w.text
                                 for w in app.stage.walk()))

    def test_game_page_tracks_full_window_and_side_background_is_not_a_flat_plate(self):
        from PIL import Image
        original=Window.size
        try:
            with support.GameWidgetTests().booth() as (app,_):
                app._choose_game()
                for size in ((800,900),(800,1280),(452,900),(360,640)):
                    Window.size=size
                    for _ in range(5):EventLoop.idle()
                    field=app._game_field
                    origin=field.to_window(*field.pos)
                    corner=field.to_window(field.right,field.top)
                    self.assertAlmostEqual(origin[0],0,delta=1)
                    self.assertAlmostEqual(origin[1],0,delta=1)
                    self.assertAlmostEqual(corner[0],size[0],delta=1)
                    self.assertAlmostEqual(corner[1],size[1],delta=1)
                Window.size=(800,900)
                for _ in range(5):EventLoop.idle()
                with tempfile.TemporaryDirectory() as root:
                    filename=Window.screenshot(name=str(Path(root)/'wide.png'))
                    with Image.open(filename) as image:
                        # The original flat letterbox had one color here.
                        colors=image.convert('RGB').crop((5,30,100,850)).getcolors(100000)
                        self.assertGreater(len(colors),5)
        finally:Window.size=original

    def test_right_click_does_not_navigate_and_wide_side_tap_flaps_once(self):
        class Pointer(MotionEvent):
            def depack(self,args):
                self.sx,self.sy,self.button=args;self.profile=['pos','button'];super().depack(args)
        def tap(point,button):
            event=Pointer('followup',button,(point[0]/Window.width,point[1]/Window.height,button),is_touch=True)
            EventLoop.post_dispatch_input('begin',event);EventLoop.post_dispatch_input('end',event)
        original=Window.size
        try:
            with support.GameWidgetTests().booth() as (app,_):
                Window.size=(800,900);app._choose_game()
                for _ in range(4):EventLoop.idle()
                stage=app._game_field
                pos,extent=stage._rect((35,542,290,55))
                tap(stage.to_window(pos[0]+extent[0]/2,pos[1]+extent[1]/2),'right')
                self.assertEqual(app.navigation.page,'game_preview')
                app._open_game_demo();app._demo_code.text='DEMO-SIDE';app._claim_game_demo()
                support.GameWidgetTests().settle(app)
                for _ in range(3):EventLoop.idle()
                app._game_engine.velocity=100
                with patch.object(app.audio_v2,'cue') as cue:
                    tap((10,Window.height/2),'left')
                    self.assertLess(app._game_engine.velocity,0)
                    self.assertEqual(cue.call_count,1)
        finally:Window.size=original


if __name__=='__main__':unittest.main()
