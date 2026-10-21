"""FEAT-021 Phase 1: authored slot, actual composition and release regressions."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from photobooth.meong_fly_print_fx import InstantPhotoEmitter, paper_corners
from photobooth.meong_fly_sprite import camera_frames, fit_rect, world_slot, SLOT
from photobooth.meong_fly_visual_v3 import paint_poster_screen, photo_feed_frames
from PIL import Image


class CameraGeometryTests(unittest.TestCase):
    def test_authored_aperture_has_rear_shadow_and_open_foreground(self):
        frame = camera_frames()['hero']
        self.assertEqual(frame.slot, (108, 124))
        self.assertEqual(frame.front.getpixel((108, 123))[3], 0)
        self.assertEqual(frame.rear.getpixel((108, 123))[3], 255)
        self.assertEqual(frame.front.getpixel((108, 119))[3], 255)
        self.assertEqual(frame.front.getpixel((86, 123))[3], 255)

    def test_tilt_moves_slot_with_pixels(self):
        frames = camera_frames()
        level = frames['level'].slot
        for name, sign in [('climb', -1), ('dive', 1)]:
            frame = frames[name]
            self.assertEqual(frame.angle, sign*5)
            self.assertNotEqual(frame.slot, level)
            # Independently check the rotated aperture remains dark in rear layer.
            x, y = (round(v) for v in frame.slot)
            neighborhood = frame.rear.crop((x-1,y-1,x+2,y+2))
            self.assertIsNotNone(neighborhood.getbbox())

    def test_fit_and_slot_share_uniform_scale(self):
        frame = camera_frames()['hero']
        for box in [(35,69,290,175), (78,190,215,160), (0,0,100,80)]:
            x,y,w,h = rect = fit_rect(frame.front.size, box)
            sx,sy = world_slot(frame, rect)
            self.assertAlmostEqual(w/224, h/152)
            self.assertAlmostEqual((sx-x)/(sy-y), SLOT[0]/SLOT[1])

    def test_backdrops_never_load_or_draw_hero(self):
        with patch('photobooth.meong_fly_visual_v3.meong_animation_frames',
                   side_effect=AssertionError('Background owns no hero')):
            for screen in ('start','won','lost'):
                self.assertEqual(paint_poster_screen(screen, 'unused').size, (360,720))

    def test_feed_moves_existing_pixels_outward_without_stretch(self):
        tile = Image.new('RGBA', (4, 8))
        for y in range(8):
            for x in range(4):
                tile.putpixel((x,y), (y*30,x*30,100,255))
        frames = photo_feed_frames(tile, steps=4)
        self.assertEqual(frames[0].getpixel((0,0)), tile.getpixel((0,6)))
        self.assertEqual(frames[1].getpixel((0,2)), tile.getpixel((0,6)))
        self.assertEqual(frames[0].getpixel((0,2))[3], 0)
        self.assertEqual(frames[-1].tobytes(), tile.tobytes())

    def test_paper_top_center_is_outlet_at_every_angle(self):
        for angle in (-5,0,5):
            p=paper_corners(100,200,30,40,angle)
            self.assertAlmostEqual((p[0][0]+p[3][0])/2,115)
            self.assertAlmostEqual((p[0][1]+p[3][1])/2,200)


class PrintLifecycleV5Tests(unittest.TestCase):
    def test_full_hold_release_continuity_and_independent_fall(self):
        e=InstantPhotoEmitter()
        held = None
        release = None
        for i in range(100):
            before = e.poses()
            e.update(.03, (150+i*.3,180+i*.2), 500, angle=5)
            poses=e.poses()
            if poses and poses[0].attached and poses[0].reveal==1:
                held=poses[0]
            if poses and not poses[0].attached:
                release=poses[0]
                self.assertTrue(before[0].attached)
                self.assertEqual(release.x,before[0].x)
                self.assertEqual(release.y,before[0].y)
                self.assertEqual(release.angle,before[0].angle)
                break
        self.assertIsNotNone(held)
        self.assertIsNotNone(release)
        e.update(.1,(40,90),500,angle=-5)
        self.assertGreater(e.poses()[0].y,release.y)
        self.assertLess(abs(e.poses()[0].x-release.x),1)

    def test_pause_freezes_both_attached_and_falling_paper(self):
        e=InstantPhotoEmitter()
        for i in range(60):
            e.update(.03,(180,200),500)
            before=e.poses()
            e.update(.1,(40,80),500,paused=True,angle=5)
            self.assertEqual(e.poses(),before)
        self.assertTrue(before)
        self.assertFalse(before[0].attached)

    def test_win_cap_and_rotated_safe_boundary(self):
        e=InstantPhotoEmitter()
        e.MAX_SHEETS=1
        for _ in range(400):
            e.update(.03,(180,200),350,angle=5)
            self.assertLessEqual(len(e.poses()),1)
            for p in e.poses():
                self.assertLess(max(y for x,y in paper_corners(
                    p.x,p.y,p.width,p.height,p.angle)),350)


@unittest.skipUnless(importlib.util.find_spec('kivy'), 'Kivy unavailable')
class KivyCompositionV5Tests(unittest.TestCase):
    def setUp(self):
        from photobooth.meong_fly_flow import MeongFlyFlow
        from photobooth.meong_fly_receipts import DemoReceiptLedger
        from photobooth.meong_fly_gui import MeongFlyStage
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.flow=MeongFlyFlow(DemoReceiptLedger(Path(self.tmp.name)/'test.db'))
        self.stage=MeongFlyStage(self.flow,size=(450,900),size_hint=(None,None))
        self.addCleanup(self.stage.dispose)

    def test_single_front_texture_and_immediate_scene_cleanup(self):
        from kivy.graphics import Rectangle
        for scene in ('start','won','lost'):
            self.flow.screen=scene
            self.stage._refresh()
            front=self.stage._camera_layers['hero'][1]
            count=sum(isinstance(c,Rectangle) and c.texture is front
                      for c in self.stage.canvas.before.children)
            self.assertEqual(count,1)
        self.flow.screen='start'
        for _ in range(30): self.stage.update(.03)
        self.assertTrue(self.stage._printer.poses())
        for scene in ('scan','lost','tutorial','layouts'):
            self.flow.screen=scene
            self.stage._refresh()
            self.assertFalse(self.stage._printer.poses())

    def test_anchor_tracks_hover_and_resize(self):
        for size in ((450,900),(800,600),(1200,800)):
            self.stage.size=size
            for t in (0,.4,1.2):
                self.stage._time=t
                slot,_=self.stage._printer_context('start')
                rect=self.stage._hero_rect('start')
                self.assertEqual(slot,world_slot(camera_frames()['hero'],rect))
                # Window conversion is shared with all UI hitboxes.
                pos,_=self.stage._rect((*slot,0,0))
                ox,oy,scale=self.stage._viewport()
                self.assertAlmostEqual((pos[0]-ox)/scale,slot[0])
                self.assertAlmostEqual(720-(pos[1]-oy)/scale,slot[1])

    def test_no_texture_upload_during_warmed_print_animation(self):
        with patch('photobooth.meong_fly_gui.kivy_texture',
                   side_effect=AssertionError('Per-frame upload')):
            for _ in range(100): self.stage.update(.03)
        self.assertTrue(self.stage._printer.poses())

    def test_quad_uses_leading_edge_uv_and_camera_depth(self):
        from kivy.graphics import Quad,Rectangle
        for _ in range(29): self.stage.update(.03)
        pose=self.stage._printer.poses()[0]
        self.assertTrue(pose.attached)
        children=self.stage.canvas.before.children
        quad=next(c for c in children if isinstance(c,Quad))
        self.assertAlmostEqual(quad.tex_coords[1],1-pose.reveal,places=5)
        front=self.stage._camera_layers['hero'][1]
        rear=self.stage._camera_layers['hero'][0]
        rear_index=next(i for i,c in enumerate(children)
                        if isinstance(c,Rectangle) and c.texture is rear)
        front_index=next(i for i,c in enumerate(children)
                         if isinstance(c,Rectangle) and c.texture is front)
        self.assertLess(rear_index,children.index(quad))
        self.assertLess(children.index(quad),front_index)


if __name__=='__main__': unittest.main()
