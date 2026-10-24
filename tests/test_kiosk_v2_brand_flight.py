"""Native decorative motion, real contact, source reuse and film lifecycle."""
import time
import unittest
from unittest.mock import patch

try:
    import kivy
except ImportError:
    HAS_KIVY=False
else:
    HAS_KIVY=True
    from kivy.base import EventLoop
    from kivy.core.window import Window
    from kivy.graphics import Quad,Rectangle
    from kivy.uix.floatlayout import FloatLayout
    from photobooth.kiosk_v2.branding import MeongLogo
    from photobooth.kiosk_v2.brand_flight import FlyingMeongArt,flight_art


@unittest.skipUnless(HAS_KIVY,'Native decorative compositor required')
class BrandFlightTests(unittest.TestCase):
    def setUp(self):
        self.parent=FloatLayout()
        self.logo=MeongLogo(size_hint=(None,None),size=(428,78),pos=(12,100))
        self.parent.add_widget(self.logo);Window.add_widget(self.parent)
        self.settle(.05);self.logo.set_active(False)

    def tearDown(self):
        self.logo.dispose();Window.remove_widget(self.parent)

    @staticmethod
    def settle(seconds=.06):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:EventLoop.idle()

    def contact_phase(self,direction):
        art=self.logo.art
        unit=art.unit
        if direction>0:
            return (self.logo.lettering.x-art.x-58.5*unit)/art.travel
        return (self.logo.lettering.right-art.x)/art.travel

    def wait_for_impact(self):
        deadline=time.monotonic()+1
        while self.logo.spin==0 and time.monotonic()<deadline:EventLoop.idle()
        self.assertNotEqual(self.logo.spin,0,'Native flight never reached the lettering')

    def test_reuses_original_camera_film_emitter_and_immutable_source_pixels(self):
        from photobooth.meong_fly_gui import MeongFlyStage
        from photobooth.meong_fly_print_fx import InstantPhotoEmitter
        from photobooth.meong_fly_sprite import camera_frames
        self.assertIs(FlyingMeongArt._paint_camera,MeongFlyStage._paint_camera)
        self.assertIs(FlyingMeongArt._paint_print_sheets,MeongFlyStage._paint_print_sheets)
        self.assertIsInstance(self.logo.art._printer,InstantPhotoEmitter)
        original=camera_frames()['level'].front
        before=original.tobytes();frames,_,_=flight_art()
        self.assertGreater(len({frames[f'level-{i}'].front.tobytes() for i in range(4)}),1)
        # Moving limbs must never move or repaint the authored camera aperture.
        for phase in range(4):
            frame=frames[f'level-{phase}']
            self.assertEqual(frame.front.crop((10,10,40,46)).tobytes(),original.crop((10,10,40,46)).tobytes())
            self.assertEqual(frame.slot,camera_frames()['level'].slot)
        self.assertEqual(original.tobytes(),before)

    def test_real_clock_contact_spins_once_then_settles_and_return_hits_from_other_side(self):
        logo=self.logo
        logo.size=(428,104);self.settle(.03)  # Compact advert's taller header.
        with patch.object(logo,'_hit_wordmark',wraps=logo._hit_wordmark) as impact:
            for direction in (1,-1):
                logo.set_active(False)
                logo._flight_direction=direction;logo._hit_this_pass=False
                logo.flight=self.contact_phase(direction)-direction*.02
                logo._fly(detect_impact=False)
                previous=impact.call_count
                logo.set_active(True);self.wait_for_impact()
                self.assertEqual(impact.call_count,previous+1)
                self.assertNotEqual(logo.spin,0)
                self.assertEqual(logo.wordmark.center_x,logo.center_x)
                self.settle(.8)
                self.assertEqual(impact.call_count,previous+1)
                self.assertEqual(logo.spin,0)
                self.assertEqual(logo._word_spin.angle,0)
                self.assertIsNone(logo._spin_anim)

    def test_pause_resize_resume_and_dispose_do_not_replay_or_leave_animations(self):
        logo=self.logo
        logo.flight=self.contact_phase(1)-.02;logo._fly(detect_impact=False)
        with patch.object(logo,'_hit_wordmark',wraps=logo._hit_wordmark) as impact:
            logo.set_active(True);self.wait_for_impact()
            self.assertNotEqual(logo.spin,0)
            logo.set_active(False)
            frozen=(logo.flight,logo.spin,logo.art.elapsed,logo.art._printer.elapsed,logo.art._printer.poses())
            self.settle(.12)
            self.assertEqual((logo.flight,logo.spin,logo.art.elapsed,logo.art._printer.elapsed,logo.art._printer.poses()),frozen)
            self.assertIsNone(logo._spin_anim);self.assertIsNone(logo._flight_anim)
            for width,height in ((776,78),(428,78),(600,90)):
                logo.size=(width,height);self.settle(.02)
                self.assertEqual(logo.spin,frozen[1])
                self.assertAlmostEqual(logo._word_spin.origin[0],logo.center_x)
            logo.set_active(True);self.settle(.8)
            self.assertEqual(impact.call_count,1)
            self.assertEqual(logo.spin,0)
            logo.dispose();frozen=(logo.flight,logo.spin,logo.art.elapsed)
            self.settle(.08)
            self.assertEqual((logo.flight,logo.spin,logo.art.elapsed),frozen)
            self.assertIsNone(logo._spin_anim);self.assertIsNone(logo._flight_anim)
            self.assertTrue(logo.art._disposed)

    def test_attached_photo_tracks_outlet_and_detached_photo_stays_behind_meong(self):
        from photobooth.meong_fly_sprite import world_slot
        art=self.logo.art
        art.reset_geometry()
        for _ in range(8):art.advance(.3,1,.1)
        attached=art._printer.poses()[0]
        self.assertTrue(attached.attached)
        name,box=art._camera_context('header');slot=world_slot(art._camera_frames[name],box)
        self.assertAlmostEqual(attached.x+attached.width/2,slot[0])
        self.assertAlmostEqual(attached.y,slot[1])
        for _ in range(7):art.advance(.3,1,.1)
        detached=art._printer.poses()[0]
        self.assertFalse(detached.attached)
        art.advance(.7,1,.1)
        fallen=art._printer.poses()[0]
        self.assertFalse(fallen.attached)
        self.assertLess(abs(fallen.x-detached.x),6)
        self.assertGreater(fallen.y,detached.y)
        art._draw()
        self.assertTrue(any(isinstance(i,Quad) for i in art._art_canvas.children))

    def test_cached_frame_motion_changes_limbs_rainbow_and_keeps_mirror_uvs_without_uploads(self):
        art=self.logo.art;seen=set();trails=set()
        with patch('photobooth.kiosk_v2.brand_flight.kivy_texture',side_effect=AssertionError('Per-frame upload')):
            for index in range(32):
                art.advance(.3,1,.04);art._draw();seen.add(art._pose)
                bodies=art._camera_layers[art._pose]
                trails.add(tuple(tuple(i.pos) for i in art._art_canvas.children
                                 if isinstance(i,Rectangle) and i.texture not in bodies))
        self.assertGreater(len(seen),4);self.assertGreater(len(trails),1)
        art.advance(.7,-1,0);art._draw()
        textures=art._camera_layers[art._pose]
        bodies=[i for i in art._art_canvas.children if isinstance(i,Rectangle) and i.texture in textures]
        self.assertEqual(len(bodies),2)
        for body in bodies:
            uv=body.texture.tex_coords
            self.assertEqual(tuple(body.tex_coords),(*uv[2:4],*uv[0:2],*uv[6:8],*uv[4:6]))

    def test_same_level_brand_geometry_at_compact_and_large_headers(self):
        logo=self.logo
        for width,height in ((428,78),(776,78),(428,90),(776,104),(1200,78)):
            logo.size=(width,height);self.settle(.02)
            self.assertEqual(logo.wordmark.center_x,logo.center_x)
            self.assertEqual(logo.caption.center_x,logo.center_x)
            self.assertGreaterEqual(logo.art.body_box[3],height*.65)
            for phase in (0,.25,.5,.75,1):
                logo.flight=phase
                x,y,w,h=logo.art.body_box
                self.assertGreaterEqual(x,logo.x)
                self.assertLessEqual(x+w,logo.right)
                self.assertAlmostEqual(y+h/2,logo.lettering.center_y,delta=2)
                self.assertGreaterEqual(y,logo.y)
                self.assertLessEqual(y+h,logo.top)
                if phase==0:
                    self.assertLess(x+w,logo.lettering.x,'Flight starts inside the wordmark')
                elif phase==1:
                    before=logo.art.body_box[0]
                    logo._flight_direction=-1;logo._fly(detect_impact=False)
                    self.assertGreater(logo.art.body_box[0],logo.lettering.right)
                    self.assertEqual(logo.art.body_box[0],before,'Meong jumps on its return turn')
                    logo._flight_direction=1
