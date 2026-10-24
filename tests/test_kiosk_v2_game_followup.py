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
    def test_recovered_consumed_win_removes_preview_discount_without_replaying_admission(self):
        from tests import test_kiosk_v2_checkout_widgets as checkout_support
        helper=checkout_support.CheckoutWidgetTests()
        with helper.booth() as (app,store):
            attempt=store.claim('DEMO-LOST-ACK')['attempt_id']
            app._game_result=store.finish(attempt,'won',10)
            helper.gallery(app);app._open_mock_checkout();helper.settle(app)
            oid=app._mock_view['order_id']
            store.transition(oid,'confirm');store.admit(oid)
            app._mock_status();helper.settle(app)
            self.assertTrue(app._game_discount_used)
            self.assertIsNone(app._photo_jobs)
            app._mock_leave()
            self.assertEqual(app._gallery_amount.total,10000)

    def test_winning_gallery_total_matches_checkout_and_consumed_offer_is_not_reused(self):
        import time
        from tests import test_kiosk_v2_checkout_widgets as checkout_support
        from photobooth.kiosk_v2.photos import PhotoTest
        for won in (False,True):
            with tempfile.TemporaryDirectory() as root,patch('photobooth.kiosk_v2.photos.configured_test',
                    return_value=PhotoTest(root)),checkout_support.CheckoutWidgetTests().booth() as (app,store):
                helper=checkout_support.CheckoutWidgetTests()
                attempt=store.claim('DEMO-GALLERY-OFFER')['attempt_id']
                app._game_result=store.finish(attempt,'won' if won else 'lost',10 if won else 0)
                helper.gallery(app)
                self.assertEqual(app._gallery_amount.total,7500 if won else 10000)
                self.assertIn('Rp7.500' if won else 'Rp10.000',app._order_total_label.text)
                app._open_mock_checkout();helper.settle(app)
                self.assertEqual(app._mock_view['total'],app._gallery_amount.total)
                if won:
                    app._mock_transition('confirm');helper.settle(app)
                    app._mock_admit();helper.settle(app)
                    deadline=time.monotonic()+3
                    while app._photo_jobs.busy and time.monotonic()<deadline:
                        app._poll_photos();time.sleep(.005)
                    self.assertFalse(app._photo_jobs.busy)
                    app._leave_photo_confirm()
                    self.assertEqual(app._gallery_amount.discount,0)
                    self.assertIn('sudah dipakai',app._game_offer_note.text)

    def test_gallery_discount_is_once_per_order_and_empty_cart_stays_zero(self):
        helper=support.GameWidgetTests()
        with helper.booth() as (app,store):
            record=store.claim('DEMO-MANY-COPIES')['attempt_id']
            app._game_result=store.finish(record,'won',10)
            app._choose_photo();app._complete_tutorial()
            self.assertEqual(app._gallery_amount.total,0)
            app._change_copies(2)
            self.assertEqual(app._gallery_amount.total,12500)
            app._shift_template(1);app._change_copies(1)
            self.assertEqual(app._gallery_amount.total,22500)
            self.assertEqual(app._gallery_amount.discount,2500)

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

    def test_game_controls_reflow_across_full_window_and_sky_is_one_opaque_scene(self):
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
                    pos,extent=field._rect((35,542,290,55))
                    self.assertGreater(extent[0],field.width*.78)
                    # One full-stage original sky covers the old main filler.
                    group,bg,_,_,_=field._responsive_scenes['start']
                    self.assertEqual(tuple(bg.size),tuple(field.size))
                    self.assertEqual(tuple(bg.pos),tuple(field.pos))
                    self.assertGreaterEqual(min(bg.texture.pixels[3::4]),255)
                Window.size=(800,900)
                for _ in range(5):EventLoop.idle()
                with tempfile.TemporaryDirectory() as root:
                    filename=Window.screenshot(name=str(Path(root)/'wide.png'))
                    with Image.open(filename) as image:
                        # Original sky extends into the actual former side area.
                        colors=image.convert('RGB').crop((5,30,100,850)).getcolors(100000)
                        self.assertGreater(len(colors),5)
        finally:Window.size=original

    def test_resize_preserves_code_game_clock_and_cached_textures(self):
        original=Window.size
        helper=support.GameWidgetTests()
        try:
            with helper.booth() as (app,_):
                app._choose_game();app._open_game_demo()
                app._demo_code.text='DEMO-RESIZE'
                field=app._game_field
                with patch('photobooth.kiosk_v2.game_scene.kivy_texture',side_effect=AssertionError('Resize upload')):
                    for size in ((800,900),(452,900),(800,1280),(360,640)):
                        Window.size=size
                        for _ in range(4):EventLoop.idle()
                        self.assertEqual(field.receipt.text,'DEMO-RESIZE')
                        self.assertGreater(field.receipt.width,field.width*.70)
                app._claim_game_demo();helper.settle(app)
                app._toggle_game_pause()
                field=app._game_field
                engine=app._game_engine;engine.score=4
                before=(engine.y,engine.elapsed,field._printer_screen)
                with patch('photobooth.kiosk_v2.game_scene.kivy_texture',side_effect=AssertionError('Resize upload')):
                    for size in ((800,900),(452,900),(800,1280),(360,640)):
                        Window.size=size
                        for _ in range(4):EventLoop.idle()
                        self.assertIs(app._game_engine,engine)
                        self.assertEqual(engine.score,4)
                        self.assertEqual((engine.y,engine.elapsed,field._printer_screen),before)
                self.assertIsNone(field._scanner)
        finally:Window.size=original

    def test_projection_keeps_collision_geometry_and_original_sprite_aspect(self):
        from photobooth.kiosk_v2.game_layout import Layout
        from photobooth.meong_fly_game_art import camera_screen_rect,asteroid_screen_rects
        for size in ((800,900),(800,1280),(452,900),(360,640)):
            layout=Layout(*size,'game')
            self.assertAlmostEqual(layout.world_x(360),size[0]/layout.scale)
            offset=layout.extra[0]*.23
            for x in (15.75,16,24,40,70,110,160,200):
                self.assertAlmostEqual(layout.world_x(x)-x,offset)
            for box in [camera_screen_rect(320)]+[r for _,r in asteroid_screen_rects(110,320)]:
                projected=layout.rect(box)
                self.assertEqual(projected[2:],box[2:])

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
